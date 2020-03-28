"""
TODO: Docs
"""
import discord
from discord.ext import commands
from ..bot import Bot


class ApplicationCog(commands.Cog):
    """
    TODO: Docs, proper commands
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self._bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """
        TODO: Docs, proper code
        """
        print(member.display_name, "joined Dof Discord")

    @commands.command()
    async def apply(self, ctx, *, member: discord.Member = None):
        """
        TODO: Docs, proper code
        """
        member = member or ctx.author

        await self._bot.channels["bot-testing"].send(f"{member.display_name} has used !apply command")


def setup(bot: commands.Bot):
    """
    TODO: Docs
    """
    bot.add_cog(ApplicationCog(bot))
