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
        await self.bot.channels["chat"].send(strings.Info.welcome.format(member.display_name))

    @commands.command()
    async def info(self, ctx: commands.Context, *, member: discord.Member = None):
        """
        Cancel command is used to cancel an in-progress application.

        Current steps are as follows:

            1. If application isn't started, relevant help message is displayed
            2. If application is started, it is then cancelled and removed from the applications dictionary
        """
        member = member or ctx.author
        Log.debug(f"Detected !info command used by {member.display_name}")
        await ctx.send("Sorry! The command is still under construction :(")


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(InformationCog(bot))
