"""
Module storing DoF info-related and welcome functionalities, as well as bot-related informational commands.
"""
import discord
from dof_discord_bot import __version__, __title__
from discord.ext import commands
from .. import strings
from ..bot import Bot
from ..logger import Log
from ..utils import Session, Page, LinePaginator, MessageEmbed


class InfoSession(Session):
    """
    Info Session handling properly displaying info command contents in an interactive, per-user session.
    """
    async def build_pages(self):
        """
        Builds predefined pages and puts them into the paginator.
        """
        paginator = LinePaginator(prefix="", suffix="")

        # Add general info page
        paginator.add_page(Page(
            strings.Info.bot_welcome,
            "",
            strings.Info.bot_tutorial,
            "",
            strings.Info.bot_browse,
            "",
            strings.Info.bot_output
        ))

        # Add rules page
        paginator.add_page(Page(
            strings.Info.rules_welcome,
            "",
            strings.Info.rules_first,
            strings.Info.rules_second,
            strings.Info.rules_third,
            strings.Info.rules_fourth,
            strings.Info.rules_fifth,
            strings.Info.rules_sixth
        ))

        # Add links page
        paginator.add_page(Page(
            strings.Info.links_welcome,
            "",
            strings.Info.links_ts,
            "",
            strings.Info.links_website,
            "",
            strings.Info.links_public_steam,
            "",
            strings.Info.links_private_steam
        ))

        # Add authors page
        paginator.add_page(Page(
            strings.Info.authors_welcome,
            "",
            strings.Info.authors_bertalicious,
            strings.Info.authors_white_noise,
            "",
            strings.Info.authors_support,
            "",
            strings.Info.authors_link
        ))

        # Save organised pages to session
        self.pages = paginator.pages


class InformationCog(commands.Cog):
    """
    Information Cog is a discord extension providing a set of DoF-related informational commands and listeners.
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        Listener providing a way to listen to a new member joining DoF discord, to welcome them properly.
        """
        Log.info(f"{member.display_name} joined DoF discord for the first time")
        await self.bot.channels["chat"].send(strings.Info.welcome.format(member.mention))

    @commands.command()
    async def info(self, ctx: commands.Context):
        """
        Info command is used to display bot and DoF-related information, as well as a basic bot tutorial.
        """
        member = ctx.author

        Log.debug(f"Detected !info command used by {member.display_name}")
        await InfoSession.start(ctx, "Information")

    @commands.command()
    @commands.has_role("Defender")
    async def version(self, ctx: commands.Context):
        """
        Version command is a Defender-only command used to display the current version of the bot.
        """
        member: discord.Member = ctx.author

        Log.debug(f"Detected !version command used by {member.display_name}")
        Log.debug(f"{member.display_name}'s roles are {(role.name for role in member.roles)}")
        await ctx.send(embed=MessageEmbed(f"{__title__} v{__version__}"))

    @version.error
    async def version_handler(self, ctx: commands.Context, error: discord.DiscordException):
        """
        Custom handler needed to handle the custom error - the user should be informed about an invalid character.
        """
        if isinstance(error, commands.MissingRole):
            Log.debug(f"Caught missing role error - {error}")
            await ctx.send(embed=MessageEmbed(str(error), negative=True))
        else:
            raise


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(InformationCog(bot))
