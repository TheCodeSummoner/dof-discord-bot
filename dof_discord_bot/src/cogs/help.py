"""
TODO: Docs, logs
"""
import discord
from discord.ext import commands
from ..constants import *
from .. import strings

import asyncio
import itertools
from collections import namedtuple
from contextlib import suppress
from ..bot import Bot
import typing as t
from ..logger import Log
from discord.ext.commands import Paginator

from discord import Colour, Embed, HTTPException, User
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
        self.lines_count = 0
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
            if self.lines_count >= self.max_lines:
                self.lines_count = 0
                self.close_page()

            self.lines_count += 1
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


# Declare unicode-based emojis
FIRST_PAGE_EMOJI = "\u23EE"
PREVIOUS_PAGE_EMOJI = "\u2B05"
NEXT_PAGE_EMOJI = "\u27A1"
LAST_PAGE_EMOJI = "\u23ED"
DELETE_EMOJI = "<:trashcan:>"

Cog = namedtuple('Cog', ['name', 'description', 'commands'])


class HelpQueryNotFound(discord.DiscordException):
    """
    Raised when a HelpSession query doesn't match a command or a cog.
    """
    def __init__(self, arg: str):
        super().__init__(arg)


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

    Available options kwargs:
        * cleanup: Optional[bool]
            Set to `True` to have the message deleted on session end. Defaults to `False`.
        * only_can_run: Optional[bool]
            Set to `True` to hide commands the user can't run. Defaults to `False`.
        * show_hidden: Optional[bool]
            Set to `True` to include hidden commands. Defaults to `False`.
        * max_lines: Optional[int]
            Sets the max number of lines the paginator will add to a single page. Defaults to 20.

    Cogs can be grouped into custom categories. All cogs with the same category will be displayed
    under a single category name in the help output. Custom categories are defined inside the cogs
    as a class attribute named `category`. A description can also be specified with the attribute
    `category_description`. If a description is not found in at least one cog, the default will be
    the regular description (class docstring) of the first cog found in the category.
    """

    def __init__(self, ctx: commands.Context, command: str = "", max_lines: int = 8):
        # Declare a mapping of emoji to reaction functions
        self.reactions = {
            FIRST_PAGE_EMOJI: self.do_first_page,
            PREVIOUS_PAGE_EMOJI: self.do_previous_page,
            NEXT_PAGE_EMOJI: self.do_next_page,
            LAST_PAGE_EMOJI: self.do_last_page,
            DELETE_EMOJI: self.do_delete()
        }

        self.ctx = ctx
        self.bot = ctx.bot
        self.title = "Command Help"

        # set the query details for the session
        if command:
            self.query = self.bot.get_command(command)
            if not self.query:
                raise HelpQueryNotFound(strings.Help.invalid_query.format(command))
            self.description = self.query.description or self.query.help
        else:
            self.query = ctx.bot
            self.description = self.query.description
        self.author = ctx.author
        self.destination = ctx.channel

        # set the config for the session
        self._max_lines = max_lines

        # init session states
        self.pages = None
        self.current_page = 0
        self.message = None
        self.timeout_task = None
        self.reset_timeout()


    async def timeout(self, seconds: int = 30) -> None:
        """Waits for a set number of seconds, then stops the help session."""
        await asyncio.sleep(seconds)
        await self.stop()

    def reset_timeout(self):
        """
        Cancels the original timeout task and sets it up again from the start.
        """
        # Cancel the original task if it exists
        if self.timeout_task:
            if not self.timeout_task.cancelled():
                self.timeout_task.cancel()

        # Recreate the timeout task
        self.timeout_task = self.bot.loop.create_task(self.timeout())

    async def _prepare(self) -> None:
        """Sets up the help session pages, events, message and reactions."""
        # create paginated content
        try:
            await self.build_pages()
        except HelpQueryNotFound as e:
            raise

        # setup listeners
        self.bot.add_listener(self.on_reaction_add)
        self.bot.add_listener(self.on_message_delete)

        # Send the help message
        await self.update_page()
        self.add_reactions()

    def add_reactions(self) -> None:
        """Adds the relevant reactions to the help message based on if pagination is required."""
        # if paginating
        if len(self.pages) > 1:
            for reaction in self.reactions:
                self.bot.loop.create_task(self.message.add_reaction(reaction))

        # if single-page
        else:
            self.bot.loop.create_task(self.message.add_reaction(DELETE_EMOJI))

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

    async def global_help(self, paginator: LinePaginator):
        """
        Retrieves all commands and formats them correctly
        """
        all_commands = self.bot.commands
        sorted_by_cog = sorted(all_commands, key=lambda cmd: cmd.cog_name) #TODO: Sort by pre-defined order instead
        grouped_by_cog = itertools.groupby(sorted_by_cog, key=lambda cmd: cmd.cog_name)

        for category, commands in grouped_by_cog:
            commands = sorted(commands, key=lambda cmd: cmd.name)

            # If there are no commands, skip the category
            if len(commands) == 0:
                continue

            # Format details for each child command
            command_descriptions = []
            for command in commands:
                signature = self._get_command_params(command)
                info = f"**`{COMMAND_PREFIX}{signature}`**"
                if command.short_doc:
                    command_descriptions.append(f'{info}\n*{command.short_doc}*')
                else:
                    command_descriptions.append(f'{info}\n*No details provided.*')

            for details in command_descriptions:
                if paginator.lines_count + len(details.split('\n')) > self._max_lines:
                    paginator.lines_count = 0
                    paginator.close_page()

                paginator.add_line(details)
                paginator.add_line("")

    async def command_help(self, paginator: LinePaginator, command: commands.Command):
        """
        Retrieves command-related information and formats it correctly.
        """
        signature = self._get_command_params(command)
        parent = command.full_parent_name + ' ' if command.parent else ''
        paginator.add_line(f'**```{COMMAND_PREFIX}{parent}{signature}```**')

        # Show command aliases
        aliases = ', '.join(f'`{a}`' for a in command.aliases)
        if aliases:
            paginator.add_line(f'**Can also use:** {aliases}\n')

    async def build_pages(self) -> None:
        """
        Builds the list of content pages to be paginated through in the help message, as a list of str.
        """
        # Use LinePaginator to restrict embed line height
        paginator = LinePaginator(prefix='', suffix='', max_lines=MAX_HELP_LINES)

        if self.description:
            paginator.add_line(f'*{self.description}*')

        if isinstance(self.query, commands.Command):
            await self.command_help(paginator, self.query)
        elif isinstance(self.query, Bot):
            await self.global_help(paginator)

        # Save organised pages to session
        self.pages = paginator.pages

    def embed_page(self, page_number: int = 0) -> Embed:
        """
        Returns an Embed with the requested page formatted within.
        """
        embed = Embed()

        # If command or cog, add query to the title
        if isinstance(self.query, commands.Command):
            title = str.join(" | ", (self.title, self.query.name))
        else:
            title = self.title

        embed.set_author(name=title, icon_url="https://cdn.discordapp.com/emojis/512367613339369475.png")
        embed.description = self.pages[page_number]

        # Add page counter to footer if paginating
        page_count = len(self.pages)
        if page_count > 1:
            embed.set_footer(text=f'Page {self.current_page + 1} / {page_count}')

        return embed

    async def update_page(self, page_number: int = 0):
        """
        Sends the initial message, or changes the existing one to the given page number.
        """
        self.current_page = page_number
        embed_page = self.embed_page(page_number)

        if not self.message:
            self.message = await self.destination.send(embed=embed_page)
        else:
            await self.message.edit(embed=embed_page)

    @classmethod
    async def start(cls, ctx: commands.Context, command: str) -> "HelpSession":
        """
        Create and begin a help session based on the given context.
        """
        session = cls(ctx, command)
        await session._prepare()
        return session

    async def stop(self) -> None:
        """
        Stops the help session, removes event listeners and attempts to delete the help message.
        """
        self.bot.remove_listener(self.on_reaction_add)
        self.bot.remove_listener(self.on_message_delete)

        # Ignore if permission issue, or the message doesn't exist
        with suppress(HTTPException, AttributeError):
            await self.message.delete()

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        Event handler for when reactions are added on the help message.
        """
        # Ensure it was the relevant session message
        if reaction.message.id != self.message.id:
            return

        # Ensure it was the session author who reacted
        if user.id != self.author.id:
            return

        # Only handle valid action emoji-s
        if str(reaction.emoji) in self.reactions:
            self.reset_timeout()
            await self.reactions[str(reaction.emoji)]()
        else:
            return

        # Remove the added reaction to prep for re-use
        with suppress(HTTPException):
            await self.message.remove_reaction(reaction, user)

    async def on_message_delete(self, message: discord.Message):
        """
        Closes the help session when the help message is deleted.
        """
        if message.id == self.message.id:
            await self.stop()

    @property
    def is_first_page(self) -> bool:
        """
        Check if session is currently showing the first page.
        """
        return self.current_page == 0

    @property
    def is_last_page(self) -> bool:
        """
        Check if the session is currently showing the last page.
        """
        return self.current_page == (len(self.pages) - 1)

    async def do_first_page(self):
        """
        Event that is called when the user requests the first page.
        """
        if not self.is_first_page:
            await self.update_page(0)

    async def do_previous_page(self):
        """
        Event that is called when the user requests the previous page.
        """
        if not self.is_first_page:
            await self.update_page(self.current_page - 1)

    async def do_next_page(self):
        """
        Event that is called when the user requests the next page.
        """
        if not self.is_last_page:
            await self.update_page(self.current_page + 1)

    async def do_last_page(self):
        """
        Event that is called when the user requests the last page.
        """
        if not self.is_last_page:
            await self.update_page(len(self.pages) - 1)

    async def do_delete(self):
        """
        Event that is called when the user requests to stop the help session.
        """
        await self.message.delete()


class HelpCog(DiscordCog):
    """
    TODO: Docs
    """

    @commands.command()
    async def help(self, ctx: commands.Context, command: str = ""):
        """
        TODO: Docs, mention only 1 argument is accepted
        """
        try:
            await HelpSession.start(ctx, command)
        except HelpQueryNotFound as e:
            await self.help_handler(ctx, e)

    @help.error
    async def help_handler(self, ctx: commands.Context, error: discord.DiscordException):
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
    bot.remove_command("help")
    bot.add_cog(HelpCog())
