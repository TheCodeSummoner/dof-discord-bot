"""
Help Cog
========

Module storing help related functionality.

TODO: Most of the code here should be extracted into utils.py, and then used both in this cog and in the Info cog.
  (Next release)
"""
import discord
import asyncio
import itertools
import contextlib
from discord.ext import commands
from ..constants import *
from .. import strings
from ..bot import Bot
from ..logger import Log


class HelpQueryNotFound(discord.DiscordException):
    """
    Raised when a HelpSession query doesn't match a command or a cog.
    """
    def __init__(self, arg: str):
        super().__init__(arg)


class LinePaginator(commands.Paginator):
    """
    TODO: Should be in utils.py, and also extended to support more things. Then write docs.
    """

    def __init__(self, max_lines: int = None, **kwargs):
        super().__init__(**kwargs)
        self.max_lines = max_lines
        self.lines_count = 0

    def add_line(self, line: str = '', *, empty: bool = False):
        """
        Extended add_line method from the parent class, added the functionality to also restrict the number of lines.
        """
        if self.max_lines is not None:
            if self.lines_count >= self.max_lines:
                self.lines_count = 0
                self.close_page()
            self.lines_count += 1

        super().add_line(line)


class HelpSession:
    """
    Help Session handling properly displaying help command contents in an interactive, per-user session.

    TODO: Extract this into a super class PagedSession in utils.py, connect it with LinePaginator, and inherit from it
      here by implementing abstract methods. Then write help-specific docs.
    """

    def __init__(self, ctx: commands.Context, command: str = ""):
        self.author = ctx.author
        self.destination = ctx.channel
        self.bot = ctx.bot
        self.title = strings.Help.help_title
        self.pages = list()
        self.current_page = 0
        self.message = None
        self.timeout_task = None

        # Declare a mapping of emoji to reaction functions
        self.reactions = {
            FIRST_PAGE_EMOJI: self.do_first_page,
            PREVIOUS_PAGE_EMOJI: self.do_previous_page,
            NEXT_PAGE_EMOJI: self.do_next_page,
            LAST_PAGE_EMOJI: self.do_last_page,
            DELETE_EMOJI: self.do_delete
        }

        # Set the query details for the session
        if command:
            self.query = self.bot.get_command(command)
            if not self.query:
                raise HelpQueryNotFound(strings.Help.invalid_query.format(command))
        else:
            self.query = ctx.bot

        # Initial timeout reset to set the timer
        self.reset_timeout()

    @classmethod
    async def start(cls, ctx: commands.Context, command: str) -> "HelpSession":
        """
        Create and begin a help session based on the given context.
        """
        Log.info(f"Starting a help session, initiated by {ctx.author}")

        session = cls(ctx, command)
        await session.prepare()
        return session

    async def stop(self):
        """
        Stops the help session, removes event listeners and attempts to delete the help message.
        """
        Log.info(f"Stopping the help session started by {self.author}")

        self.bot.remove_listener(self.on_reaction_add)
        self.bot.remove_listener(self.on_message_delete)

        # Ignore if permission issue, or the message doesn't exist
        with contextlib.suppress(discord.HTTPException, AttributeError):
            await self.message.delete()

    async def prepare(self):
        """
        Sets up the help session pages, events, message, and reactions.
        """
        Log.debug(f"Preparing the session for {self.author}")

        # Create paginated content
        await self.build_pages()

        # Setup the listeners to allow page browsing
        self.bot.add_listener(self.on_reaction_add)
        self.bot.add_listener(self.on_message_delete)

        # Display the first page and add all reactions
        await self.update_page()
        self.add_reactions()

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
        Log.debug(f"Getting first page for {self.author}")

        if not self.is_first_page:
            await self.update_page(0)

    async def do_previous_page(self):
        """
        Event that is called when the user requests the previous page.
        """
        Log.debug(f"Getting previous page for {self.author}")

        if not self.is_first_page:
            await self.update_page(self.current_page - 1)

    async def do_next_page(self):
        """
        Event that is called when the user requests the next page.
        """
        Log.debug(f"Getting next page for {self.author}")

        if not self.is_last_page:
            await self.update_page(self.current_page + 1)

    async def do_last_page(self):
        """
        Event that is called when the user requests the last page.
        """
        Log.debug(f"Getting last page")

        if not self.is_last_page:
            await self.update_page(len(self.pages) - 1)

    async def do_delete(self):
        """
        Event that is called when the user requests to stop the help session.
        """
        Log.debug(f"Deleting the message for {self.author}")

        await self.message.delete()

    async def timeout(self):
        """
        Waits for a set number of seconds, then stops the help session.
        """
        await asyncio.sleep(HELP_SESSION_TIMEOUT)
        await self.stop()

    def reset_timeout(self):
        """
        Cancels the original timeout task and sets it up again from the start.

        Used mainly to keep the session after users interact with it.
        """
        Log.debug(f"A user action by {self.author} forced the timeout reset")

        # Cancel the original task if it exists
        if self.timeout_task:
            if not self.timeout_task.cancelled():
                self.timeout_task.cancel()

        # Recreate the timeout task
        self.timeout_task = self.bot.loop.create_task(self.timeout())

    def add_reactions(self):
        """
        Adds the relevant reactions to the help message based on if pagination is required.
        """
        Log.debug(f"Adding reactions for {self.author} (help session)")

        if len(self.pages) > 1:
            for reaction in self.reactions:
                self.bot.loop.create_task(self.message.add_reaction(reaction))
        else:
            self.bot.loop.create_task(self.message.add_reaction(DELETE_EMOJI))

    async def build_pages(self):
        """
        Builds the list of content pages to be paginated through in the help message, as a list of str.
        """
        # Use LinePaginator to restrict embed line height
        paginator = LinePaginator(prefix='', suffix='', max_lines=MAX_HELP_LINES)

        if isinstance(self.query, commands.Command):
            await self.command_help(paginator, self.query)
        elif isinstance(self.query, Bot):
            await self.global_help(paginator)

        # Save organised pages to session
        self.pages = paginator.pages

    async def global_help(self, paginator: LinePaginator):
        """
        Retrieves all commands and formats them correctly
        """
        Log.debug(f"Displaying global help (all commands) for {self.author}")

        all_commands = self.bot.commands
        sorted_by_cog = sorted(all_commands, key=lambda cmd: cmd.cog_name)
        grouped_by_cog = itertools.groupby(sorted_by_cog, key=lambda cmd: cmd.cog_name)

        for category, commands in grouped_by_cog:
            commands = sorted(commands, key=lambda cmd: cmd.name)

            # If there are no commands, skip the category
            if len(commands) == 0:
                continue

            # Format details for each child command
            command_descriptions = []
            for command in commands:
                info = f"**`{COMMAND_PREFIX}{str.join(' ', (command.name, command.signature))}`**"
                if command.short_doc:
                    command_descriptions.append(f'{info}\n*{command.short_doc}*')
                else:
                    command_descriptions.append(f'{info}\n*No details provided.*')

            for details in command_descriptions:
                if paginator.lines_count + len(details.split('\n')) > MAX_HELP_LINES:
                    paginator.lines_count = 0
                    paginator.close_page()

                paginator.add_line(details)
                paginator.add_line("")

    async def command_help(self, paginator: LinePaginator, command: commands.Command):
        """
        Retrieves command-related information and formats it correctly.
        """
        Log.debug(f"Displaying command-specific help about {command.name} for {self.author}")

        paginator.add_line(f'**```{COMMAND_PREFIX}{str.join(" ", (command.name, command.signature))}```**')
        paginator.add_line(f'*{command.help}*')

        # Show command aliases
        aliases = ', '.join(f'`{a}`' for a in command.aliases)
        if aliases:
            paginator.add_line(f'**Can also use:** {aliases}\n')

    async def update_page(self, page_number: int = 0):
        """
        Displays the initial page, or changes the existing one to the given page number.
        """
        self.current_page = page_number
        embed_page = self.embed_page(page_number)

        if not self.message:
            self.message = await self.destination.send(embed=embed_page)
        else:
            await self.message.edit(embed=embed_page)

    def embed_page(self, page_number: int = 0) -> discord.Embed:
        """
        Returns an Embed with the requested page formatted within.
        """
        embed = discord.Embed()

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

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        """
        Event handler for when reactions are added on the help message.
        """
        Log.debug(f"Reaction added by {user.display_name}")

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
        with contextlib.suppress(discord.HTTPException):
            Log.debug(f"Reaction by {user.display_name} handled by the session")
            await self.message.remove_reaction(reaction, user)

    async def on_message_delete(self, message: discord.Message):
        """
        Closes the help session when the help message is deleted.
        """
        if message.id == self.message.id:
            await self.stop()


class HelpCog(commands.Cog):
    """
    Help Cog is a discord extension providing the !help command and an associated error handler.

    ALl further help functionality is handled within the `HelpSession` class.
    """

    @commands.command()
    async def help(self, ctx: commands.Context, command: str = ""):
        """
        Help command displays available commands, or displays command-specific information when used with an additional
        argument.

        Some examples of the command:

            1. !help -> displays all available command
            2. !help apply - displays information about the !apply command

        The help commands also creates a help session - use arrows to navigate the pages or the wastebasket icon to
        stop the session early and remove it.
        """
        member = ctx.author
        Log.debug(f"Detected !help command used by {member.display_name}")

        try:
            await HelpSession.start(ctx, command)
        except HelpQueryNotFound as e:
            await self.help_handler(ctx, e)

    @help.error
    async def help_handler(self, ctx: commands.Context, error: discord.DiscordException):
        """
        Custom handler needed to handle the custom error - the user should be informed about an invalid query.
        """
        if isinstance(error, HelpQueryNotFound):
            Log.debug(f"Caught invalid query error - {error}")
            embed = discord.Embed()
            embed.colour = discord.Colour.red()
            embed.title = str(error)
            await ctx.send(embed=embed)


def setup(bot: Bot):
    """
    Standard setup, loads the cog.

    Removes the default help command beforehand.
    """
    bot.remove_command("help")
    bot.add_cog(HelpCog())
