"""
Information Cog
===============

Module storing DoF info-related and welcome functionalities.
"""
import discord
from discord.ext import commands
from .. import strings
from ..bot import Bot
from ..logger import Log
from ..utils import Session, Page, LinePaginator


class InfoSession(Session):
    """
    Info Session handling properly displaying info command contents in an interactive, per-user session.
    """
    async def build_pages(self):
        """
        Builds predefined pages and puts them into the paginator.
        """
        paginator = LinePaginator(prefix='', suffix='')

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

    Listeners
    ---------

        * on_member_join - Listen to new members joining DoF discord and greet them properly

    Commands
    --------

        * info - Start a new DoF member application or display information about the current one
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


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(InformationCog(bot))
