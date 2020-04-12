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
        await self.bot.channels["chat"].send(strings.Info.welcome.format(member.mention))

    @commands.command()
    async def info(self, ctx: commands.Context):
        """
        Info command is used to display DoF-related information.
        """
        member = ctx.author

        Log.debug(f"Detected !info command used by {member.display_name}")
        await ctx.send("Sorry! The command is still under construction :(")


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(InformationCog(bot))
