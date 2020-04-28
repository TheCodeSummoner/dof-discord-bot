"""
Help Cog
========

Module storing help related functionality.
"""
import itertools
import discord
import typing
from discord.ext import commands
from .. import strings
from ..bot import Bot
from ..logger import Log
from ..constants import MAX_HELP_LINES, COMMAND_PREFIX, COMMANDS_ORDER
from ..utils import Session, LinePaginator


class HelpQueryNotFound(discord.DiscordException):
    """
    Raised when a HelpSession query doesn't match a command or a cog.
    """
    def __init__(self, arg: str):
        super().__init__(arg)


class HelpSession(Session):
    """
    Help Session handling properly displaying help command contents in an interactive, per-user session.
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, ctx: commands.Context, *args, **kwargs):
        """
        Overridden init to include query information - each help query is either a command or the bot's instance.
        """
        self.query: typing.Union[commands.Command, Bot] = ctx.query
        super().__init__(ctx, *args, **kwargs)

    async def build_pages(self):
        """
        Builds the list of content pages to be paginated through in the help message, as a list of str.
        """
        paginator = LinePaginator(prefix="", suffix="", max_lines=MAX_HELP_LINES)

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

        # Sort the commands by the index in the ordering and add them to the help message
        for command in sorted(self.bot.commands, key=lambda cmd: COMMANDS_ORDER.index(cmd.name)):

            # Retrieve command name. signature and docs (description)
            info = f"**`{COMMAND_PREFIX}{str.join(' ', (command.name, command.signature))}`**"
            if command.short_doc:
                details = f"{info}\n*{command.short_doc}*"
            else:
                details = f"{info}\n*No details provided.*"

            if paginator.lines_count + len(details.split("\n")) > MAX_HELP_LINES:
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
        paginator.add_line(f"*{command.help}*")

        # Show command aliases
        aliases = ", ".join(f"`{a}`" for a in command.aliases)
        if aliases:
            paginator.add_line("")
            paginator.add_line(strings.Help.help_aliases.format(aliases))


class HelpCog(commands.Cog):
    """
    Help Cog is a discord extension providing the !help command and an associated error handler.

    ALl further help functionality is handled within the `HelpSession` class.
    """

    @commands.command(aliases=["isummontheedofbot"])
    async def help(self, ctx: commands.Context, command: str = ""):
        """
        Help command displays available commands, or displays command-specific information when used with an additional\
        argument.

        Some examples of the command:

            1. !help -> displays all available command
            2. !help apply - displays information about the !apply command

        The help commands also creates a help session - use arrows to navigate the pages or the wastebasket icon to
        stop the session early and remove it.
        """
        member = ctx.author
        Log.debug(f"Detected !help command used by {member.display_name}")

        # Set the query details for the session - query is either a command object, or a bot object
        if command:
            query = ctx.bot.get_command(command)
            if not query:
                await self.help_handler(ctx, HelpQueryNotFound(strings.Help.invalid_query.format(command)))
            else:
                ctx.query = query
                title = str.join(" | ", (strings.Help.help_title, query.name))
                await HelpSession.start(ctx, title)
        else:
            ctx.query = ctx.bot
            title = strings.Help.help_title
            await HelpSession.start(ctx, title)

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
        else:
            raise error


def setup(bot: Bot):
    """
    Standard setup, loads the cog.

    Removes the default help command beforehand.
    """
    bot.remove_command("help")
    bot.add_cog(HelpCog())
