"""
TODO: Docs, logs
"""
import discord
from discord.ext import commands
from .. import strings

import asyncio
import itertools
from collections import namedtuple
from contextlib import suppress
from typing import Union
from ..bot import Bot
import typing as t
import discord
from ..logger import Log
from discord.ext.commands import Paginator

from discord import Colour, Embed, HTTPException, Message, Reaction, User
from discord.ext import commands
from discord.ext.commands import Cog as DiscordCog, Command, Context

DELETE_EMOJI = "<:trashcan:>"
FIRST_EMOJI = "\u23EE"   # [:track_previous:]
LEFT_EMOJI = "\u2B05"    # [:arrow_left:]
RIGHT_EMOJI = "\u27A1"   # [:arrow_right:]
LAST_EMOJI = "\u23ED"    # [:track_next:]

PAGINATION_EMOJI = (FIRST_EMOJI, LEFT_EMOJI, RIGHT_EMOJI, LAST_EMOJI, DELETE_EMOJI)
class EmptyPaginatorEmbed(Exception):
    """Raised when attempting to paginate with empty contents."""

    pass
class LinePaginator(Paginator):
    """
    A class that aids in paginating code blocks for Discord messages.
    Available attributes include:
    * prefix: `str`
        The prefix inserted to every page. e.g. three backticks.
    * suffix: `str`
        The suffix appended at the end of every page. e.g. three backticks.
    * max_size: `int`
        The maximum amount of codepoints allowed in a page.
    * max_lines: `int`
        The maximum amount of lines allowed in a page.
    """

    def __init__(
        self, prefix: str = '```', suffix: str = '```', max_size: int = 2000, max_lines: int = None
    ) -> None:
        """
        This function overrides the Paginator.__init__ from inside discord.ext.commands.
        It overrides in order to allow us to configure the maximum number of lines per page.
        """
        self.prefix = prefix
        self.suffix = suffix
        self.max_size = max_size - len(suffix)
        self.max_lines = max_lines
        self._current_page = [prefix]
        self._linecount = 0
        self._count = len(prefix) + 1  # prefix + newline
        self._pages = []

    def add_line(self, line: str = '', *, empty: bool = False) -> None:
        """
        Adds a line to the current page.
        If the line exceeds the `self.max_size` then an exception is raised.
        This function overrides the `Paginator.add_line` from inside `discord.ext.commands`.
        It overrides in order to allow us to configure the maximum number of lines per page.
        """
        if len(line) > self.max_size - len(self.prefix) - 2:
            raise RuntimeError('Line exceeds maximum page size %s' % (self.max_size - len(self.prefix) - 2))

        if self.max_lines is not None:
            if self._linecount >= self.max_lines:
                self._linecount = 0
                self.close_page()

            self._linecount += 1
        if self._count + len(line) + 1 > self.max_size:
            self.close_page()

        self._count += len(line) + 1
        self._current_page.append(line)

        if empty:
            self._current_page.append('')
            self._count += 1

    @classmethod
    async def paginate(
        cls,
        lines: t.List[str],
        ctx: Context,
        embed: discord.Embed,
        prefix: str = "",
        suffix: str = "",
        max_lines: t.Optional[int] = None,
        max_size: int = 500,
        empty: bool = True,
        restrict_to_user: User = None,
        timeout: int = 300,
        footer_text: str = None,
        url: str = None,
        exception_on_empty_embed: bool = False
    ) -> t.Optional[discord.Message]:
        """
        Use a paginator and set of reactions to provide pagination over a set of lines.
        The reactions are used to switch page, or to finish with pagination.
        When used, this will send a message using `ctx.send()` and apply a set of reactions to it. These reactions may
        be used to change page, or to remove pagination from the message.
        Pagination will also be removed automatically if no reaction is added for five minutes (300 seconds).
        Example:
        >>> embed = discord.Embed()
        >>> embed.set_author(name="Some Operation", url=url, icon_url=icon)
        >>> await LinePaginator.paginate([line for line in lines], ctx, embed)
        """
        def event_check(reaction_: discord.Reaction, user_: discord.Member) -> bool:
            """Make sure that this reaction is what we want to operate on."""
            no_restrictions = (
                # Pagination is not restricted
                not restrict_to_user
                # The reaction was by a whitelisted user
                or user_.id == restrict_to_user.id
            )

            return (
                # Conditions for a successful pagination:
                all((
                    # Reaction is on this message
                    reaction_.message.id == message.id,
                    # Reaction is one of the pagination emotes
                    str(reaction_.emoji) in PAGINATION_EMOJI,
                    # Reaction was not made by the Bot
                    user_.id != ctx.bot.user.id,
                    # There were no restrictions
                    no_restrictions
                ))
            )

        paginator = cls(prefix=prefix, suffix=suffix, max_size=max_size, max_lines=max_lines)
        current_page = 0

        if not lines:
            if exception_on_empty_embed:
                Log.exception(f"Pagination asked for empty lines iterable")
                raise EmptyPaginatorEmbed("No lines to paginate")

            Log.debug("No lines to add to paginator, adding '(nothing to display)' message")
            lines.append("(nothing to display)")

        for line in lines:
            try:
                paginator.add_line(line, empty=empty)
            except Exception:
                Log.exception(f"Failed to add line to paginator: '{line}'")
                raise  # Should propagate
            else:
                Log.trace(f"Added line to paginator: '{line}'")

        Log.debug(f"Paginator created with {len(paginator.pages)} pages")

        embed.description = paginator.pages[current_page]

        if len(paginator.pages) <= 1:
            if footer_text:
                embed.set_footer(text=footer_text)
                Log.trace(f"Setting embed footer to '{footer_text}'")

            if url:
                embed.url = url
                Log.trace(f"Setting embed url to '{url}'")

            Log.debug("There's less than two pages, so we won't paginate - sending single page on its own")
            return await ctx.send(embed=embed)
        else:
            if footer_text:
                embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
            else:
                embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")
            Log.trace(f"Setting embed footer to '{embed.footer.text}'")

            if url:
                embed.url = url
                Log.trace(f"Setting embed url to '{url}'")

            Log.debug("Sending first page to channel...")
            message = await ctx.send(embed=embed)

        Log.debug("Adding emoji reactions to message...")

        for emoji in PAGINATION_EMOJI:
            # Add all the applicable emoji to the message
            Log.trace(f"Adding reaction: {repr(emoji)}")
            await message.add_reaction(emoji)

        while True:
            try:
                reaction, user = await ctx.bot.wait_for("reaction_add", timeout=timeout, check=event_check)
                Log.trace(f"Got reaction: {reaction}")
            except asyncio.TimeoutError:
                Log.debug("Timed out waiting for a reaction")
                break  # We're done, no reactions for the last 5 minutes

            if str(reaction.emoji) == DELETE_EMOJI:
                Log.debug("Got delete reaction")
                return await message.delete()

            if reaction.emoji == FIRST_EMOJI:
                await message.remove_reaction(reaction.emoji, user)
                current_page = 0

                Log.debug(f"Got first page reaction - changing to page 1/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]
                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")
                await message.edit(embed=embed)

            if reaction.emoji == LAST_EMOJI:
                await message.remove_reaction(reaction.emoji, user)
                current_page = len(paginator.pages) - 1

                Log.debug(f"Got last page reaction - changing to page {current_page + 1}/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]
                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")
                await message.edit(embed=embed)

            if reaction.emoji == LEFT_EMOJI:
                await message.remove_reaction(reaction.emoji, user)

                if current_page <= 0:
                    Log.debug("Got previous page reaction, but we're on the first page - ignoring")
                    continue

                current_page -= 1
                Log.debug(f"Got previous page reaction - changing to page {current_page + 1}/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]

                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")

                await message.edit(embed=embed)

            if reaction.emoji == RIGHT_EMOJI:
                await message.remove_reaction(reaction.emoji, user)

                if current_page >= len(paginator.pages) - 1:
                    Log.debug("Got next page reaction, but we're on the last page - ignoring")
                    continue

                current_page += 1
                Log.debug(f"Got next page reaction - changing to page {current_page + 1}/{len(paginator.pages)}")

                embed.description = ""
                await message.edit(embed=embed)
                embed.description = paginator.pages[current_page]

                if footer_text:
                    embed.set_footer(text=f"{footer_text} (Page {current_page + 1}/{len(paginator.pages)})")
                else:
                    embed.set_footer(text=f"Page {current_page + 1}/{len(paginator.pages)}")

                await message.edit(embed=embed)

        Log.debug("Ending pagination and clearing reactions.")
        with suppress(discord.NotFound):
            await message.clear_reactions()

REACTIONS = {
    FIRST_EMOJI: 'first',
    LEFT_EMOJI: 'back',
    RIGHT_EMOJI: 'next',
    LAST_EMOJI: 'end',
    DELETE_EMOJI: 'stop',
}

Cog = namedtuple('Cog', ['name', 'description', 'commands'])


class HelpQueryNotFound(ValueError):
    """
    Raised when a HelpSession Query doesn't match a command or cog.

    Contains the custom attribute of ``possible_matches``.

    Instances of this object contain a dictionary of any command(s) that were close to matching the
    query, where keys are the possible matched command names and values are the likeness match scores.
    """

    def __init__(self, arg: str, possible_matches: dict = None):
        super().__init__(arg)
        self.possible_matches = possible_matches


class HelpSession:
    """
    An interactive session for bot and command help output.

    Expected attributes include:
        * title: str
            The title of the help message.
        * query: Union[discord.ext.commands.Bot, discord.ext.commands.Command]
        * description: str
            The description of the query.
        * pages: list[str]
            A list of the help content split into manageable pages.
        * message: `discord.Message`
            The message object that's showing the help contents.
        * destination: `discord.abc.Messageable`
            Where the help message is to be sent to.

    Cogs can be grouped into custom categories. All cogs with the same category will be displayed
    under a single category name in the help output. Custom categories are defined inside the cogs
    as a class attribute named `category`. A description can also be specified with the attribute
    `category_description`. If a description is not found in at least one cog, the default will be
    the regular description (class docstring) of the first cog found in the category.
    """

    def __init__(
        self,
        ctx: Context,
        *command,
        cleanup: bool = False,
        only_can_run: bool = True,
        show_hidden: bool = False,
        max_lines: int = 3
    ):
        """Creates an instance of the HelpSession class."""
        self._ctx = ctx
        self._bot = ctx.bot
        self.title = "Command Help"

        # set the query details for the session
        if command:
            query_str = ' '.join(command)
            self.query = self._get_query(query_str)
            self.description = self.query.description or self.query.help
        else:
            self.query = ctx.bot
            self.description = self.query.description
        self.author = ctx.author
        self.destination = ctx.channel

        # set the config for the session
        self._cleanup = cleanup
        self._only_can_run = only_can_run
        self._show_hidden = show_hidden
        self._max_lines = max_lines

        # init session states
        self._pages = None
        self._current_page = 0
        self.message = None
        self._timeout_task = None
        self.reset_timeout()

    def _get_query(self, query: str) -> Union[Command, Cog]:
        """Attempts to match the provided query with a valid command or cog."""
        command = self._bot.get_command(query)
        if command:
            return command

        # Find all cog categories that match.
        cog_matches = []
        description = None
        for cog in self._bot.cogs.values():
            if hasattr(cog, "category") and cog.category == query:
                cog_matches.append(cog)
                if hasattr(cog, "category_description"):
                    description = cog.category_description

        # Try to search by cog name if no categories match.
        if not cog_matches:
            cog = self._bot.cogs.get(query)

            # Don't consider it a match if the cog has a category.
            if cog and not hasattr(cog, "category"):
                cog_matches = [cog]

        if cog_matches:
            cog = cog_matches[0]
            cmds = (cog.get_commands() for cog in cog_matches)  # Commands of all cogs

            return Cog(
                name=cog.category if hasattr(cog, "category") else cog.qualified_name,
                description=description or cog.description,
                commands=tuple(itertools.chain.from_iterable(cmds))  # Flatten the list
            )

        self._handle_not_found(query)

    def _handle_not_found(self, query: str) -> None:
        """
        Handles when a query does not match a valid command or cog.

        Will pass on possible close matches along with the `HelpQueryNotFound` exception.
        """
        # Combine command and cog names
        choices = list(self._bot.all_commands) + list(self._bot.cogs)
        raise HelpQueryNotFound(f'Query "{query}" not found.')

    async def timeout(self, seconds: int = 30) -> None:
        """Waits for a set number of seconds, then stops the help session."""
        await asyncio.sleep(seconds)
        await self.stop()

    def reset_timeout(self) -> None:
        """Cancels the original timeout task and sets it again from the start."""
        # cancel original if it exists
        if self._timeout_task:
            if not self._timeout_task.cancelled():
                self._timeout_task.cancel()

        # recreate the timeout task
        self._timeout_task = self._bot.loop.create_task(self.timeout())

    async def on_reaction_add(self, reaction: Reaction, user: User) -> None:
        """Event handler for when reactions are added on the help message."""
        # ensure it was the relevant session message
        if reaction.message.id != self.message.id:
            return

        # ensure it was the session author who reacted
        if user.id != self.author.id:
            return

        emoji = str(reaction.emoji)

        # check if valid action
        if emoji not in REACTIONS:
            return

        self.reset_timeout()

        # Run relevant action method
        action = getattr(self, f'do_{REACTIONS[emoji]}', None)
        if action:
            await action()

        # remove the added reaction to prep for re-use
        with suppress(HTTPException):
            await self.message.remove_reaction(reaction, user)

    async def on_message_delete(self, message: Message) -> None:
        """Closes the help session when the help message is deleted."""
        if message.id == self.message.id:
            await self.stop()

    async def prepare(self) -> None:
        """Sets up the help session pages, events, message and reactions."""
        # create paginated content
        await self.build_pages()

        # setup listeners
        self._bot.add_listener(self.on_reaction_add)
        self._bot.add_listener(self.on_message_delete)

        # Send the help message
        await self.update_page()
        self.add_reactions()

    def add_reactions(self) -> None:
        """Adds the relevant reactions to the help message based on if pagination is required."""
        # if paginating
        if len(self._pages) > 1:
            for reaction in REACTIONS:
                self._bot.loop.create_task(self.message.add_reaction(reaction))

        # if single-page
        else:
            self._bot.loop.create_task(self.message.add_reaction(DELETE_EMOJI))

    def _category_key(self, cmd: Command) -> str:
        """
        Returns a cog name of a given command for use as a key for `sorted` and `groupby`.

        A zero width space is used as a prefix for results with no cogs to force them last in ordering.
        """
        if cmd.cog:
            try:
                if cmd.cog.category:
                    return f'**{cmd.cog.category}**'
            except AttributeError:
                pass

            return f'**{cmd.cog_name}**'
        else:
            return "**\u200bNo Category:**"

    def _get_command_params(self, cmd: Command) -> str:
        """
        Returns the command usage signature.

        This is a custom implementation of `command.signature` in order to format the command
        signature without aliases.
        """
        results = []
        for name, param in cmd.clean_params.items():

            # if argument has a default value
            if param.default is not param.empty:

                if isinstance(param.default, str):
                    show_default = param.default
                else:
                    show_default = param.default is not None

                # if default is not an empty string or None
                if show_default:
                    results.append(f'[{name}={param.default}]')
                else:
                    results.append(f'[{name}]')

            # if variable length argument
            elif param.kind == param.VAR_POSITIONAL:
                results.append(f'[{name}...]')

            # if required
            else:
                results.append(f'<{name}>')

        return f"{cmd.name} {' '.join(results)}"

    async def _global_help(self, paginator: LinePaginator, bot: Bot):
        # for cmd in bot.commands:
        #     await self._command_help(paginator, cmd)
        # remove hidden commands if session is not wanting hiddens
        if not self._show_hidden:
            filtered = [c for c in self.query.commands if not c.hidden]
        else:
            filtered = self.query.commands

        # if after filter there are no commands, finish up
        if not filtered:
            self._pages = paginator.pages
            return

        # set category to Commands if cog
        if isinstance(self.query, Cog):
            grouped = (('**Commands:**', self.query.commands),)

        # set category to Subcommands if command
        elif isinstance(self.query, commands.Command):
            grouped = (('**Subcommands:**', self.query.commands),)

            # don't show prefix for subcommands
            prefix = ''

        # otherwise sort and organise all commands into categories
        else:
            cat_sort = sorted(filtered, key=self._category_key)
            grouped = itertools.groupby(cat_sort, key=self._category_key)

        # process each category
        for category, cmds in grouped:
            cmds = sorted(cmds, key=lambda c: c.name)

            # if there are no commands, skip category
            if len(cmds) == 0:
                continue

            cat_cmds = []

            # format details for each child command
            for command in cmds:

                # skip if hidden and hide if session is set to
                if command.hidden and not self._show_hidden:
                    continue

                # see if the user can run the command
                strikeout = ''
                prefix = "!"
                signature = self._get_command_params(command)
                info = f"{strikeout}**`{prefix}{signature}`**{strikeout}"

                # handle if the command has no docstring
                if command.short_doc:
                    cat_cmds.append(f'{info}\n*{command.short_doc}*')
                else:
                    cat_cmds.append(f'{info}\n*No details provided.*')

            # state var for if the category should be added next
            print_cat = 1
            new_page = True

            for details in cat_cmds:

                # keep details together, paginating early if it won't fit
                lines_adding = len(details.split('\n')) + print_cat
                if paginator._linecount + lines_adding > self._max_lines:
                    paginator._linecount = 0
                    new_page = True
                    paginator.close_page()

                    # new page so print category title again
                    print_cat = 1

                if print_cat:
                    if new_page:
                        paginator.add_line('')
                    paginator.add_line(category)
                    print_cat = 0

                paginator.add_line(details)

    async def _command_help(self, paginator: LinePaginator, command: commands.Command):
        signature = self._get_command_params(command)
        prefix = "!"
        parent = command.full_parent_name + ' ' if command.parent else ''
        paginator.add_line(f'**```{prefix}{parent}{signature}```**')

        # show command aliases
        aliases = ', '.join(f'`{a}`' for a in command.aliases)
        if aliases:
            paginator.add_line(f'**Can also use:** {aliases}\n')

    async def build_pages(self) -> None:
        """Builds the list of content pages to be paginated through in the help message, as a list of str."""
        # Use LinePaginator to restrict embed line height
        paginator = LinePaginator(prefix='', suffix='', max_lines=self._max_lines)

        if self.description:
            print("adding", self.description)
            paginator.add_line(f'*{self.description}*')

        if isinstance(self.query, commands.Command):
            await self._command_help(paginator, self.query)

        elif isinstance(self.query, Bot):
            await self._global_help(paginator, self.query)

        # Save organised pages to session
        self._pages = paginator.pages

    def embed_page(self, page_number: int = 0) -> Embed:
        """Returns an Embed with the requested page formatted within."""
        embed = Embed()

        # if command or cog, add query to title for pages other than first
        if isinstance(self.query, (commands.Command, Cog)) and page_number > 0:
            title = f'Command Help | "{self.query.name}"'
        else:
            title = self.title

        embed.set_author(name=title, icon_url="https://cdn.discordapp.com/emojis/512367613339369475.png")
        embed.description = self._pages[page_number]

        # add page counter to footer if paginating
        page_count = len(self._pages)
        if page_count > 1:
            embed.set_footer(text=f'Page {self._current_page+1} / {page_count}')

        return embed

    async def update_page(self, page_number: int = 0) -> None:
        """Sends the intial message, or changes the existing one to the given page number."""
        self._current_page = page_number
        embed_page = self.embed_page(page_number)

        if not self.message:
            self.message = await self.destination.send(embed=embed_page)
        else:
            await self.message.edit(embed=embed_page)

    @classmethod
    async def start(cls, ctx: Context, *command, **options) -> "HelpSession":
        """
        Create and begin a help session based on the given command context.

        Available options kwargs:
            * cleanup: Optional[bool]
                Set to `True` to have the message deleted on session end. Defaults to `False`.
            * only_can_run: Optional[bool]
                Set to `True` to hide commands the user can't run. Defaults to `False`.
            * show_hidden: Optional[bool]
                Set to `True` to include hidden commands. Defaults to `False`.
            * max_lines: Optional[int]
                Sets the max number of lines the paginator will add to a single page. Defaults to 20.
        """
        session = cls(ctx, *command, **options)
        await session.prepare()

        return session

    async def stop(self) -> None:
        """Stops the help session, removes event listeners and attempts to delete the help message."""
        self._bot.remove_listener(self.on_reaction_add)
        self._bot.remove_listener(self.on_message_delete)

        # ignore if permission issue, or the message doesn't exist
        with suppress(HTTPException, AttributeError):
            if self._cleanup:
                await self.message.delete()
            else:
                await self.message.clear_reactions()

    @property
    def is_first_page(self) -> bool:
        """Check if session is currently showing the first page."""
        return self._current_page == 0

    @property
    def is_last_page(self) -> bool:
        """Check if the session is currently showing the last page."""
        return self._current_page == (len(self._pages)-1)

    async def do_first(self) -> None:
        """Event that is called when the user requests the first page."""
        if not self.is_first_page:
            await self.update_page(0)

    async def do_back(self) -> None:
        """Event that is called when the user requests the previous page."""
        if not self.is_first_page:
            await self.update_page(self._current_page-1)

    async def do_next(self) -> None:
        """Event that is called when the user requests the next page."""
        if not self.is_last_page:
            await self.update_page(self._current_page+1)

    async def do_end(self) -> None:
        """Event that is called when the user requests the last page."""
        if not self.is_last_page:
            await self.update_page(len(self._pages)-1)

    async def do_stop(self) -> None:
        """Event that is called when the user requests to stop the help session."""
        await self.message.delete()


class Help(DiscordCog):
    """
    TODO: Docs
    """

    @commands.command()
    async def help(self, ctx: commands.Context, *commands) -> None:
        """
        TODO: Docs
        """
        await HelpSession.start(ctx, *commands)


    @help.error
    async def help_handler(self, ctx: commands.Context, error: Exception):
        """
        TODO: Docs
        """
        if isinstance(error, HelpQueryNotFound):
            embed = Embed()
            embed.colour = Colour.red()
            embed.title = str(error)
            await ctx.send(embed=embed)



def setup(bot: Bot):
    """
    Standard setup, loads the cog.

    Removes the default help command beforehand.
    """
    bot.remove_command('help')
    bot.add_cog(Help())
