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

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        TODO: Docs, proper code
        """
        if message.channel.type == discord.ChannelType.private:
            print(f"Received dm - {message}")
        else:
            print(f"Not a dm - {message}")

    @commands.dm_only()
    @commands.command()
    async def apply(self, ctx, *, member: discord.Member = None):
        """
        TODO: Docs, proper code
        """
        print(ctx)
        print(member)
        member = member or ctx.author
        print(member)

        try:
            await self._bot.channels["bot-testing"].send(f"{member.display_name} has used !apply command")
        except commands.PrivateMessageOnly as e:
            print(e)
            await member.send((f""))


def setup(bot: commands.Bot):
    """
    TODO: Docs
    """
    bot.add_cog(ApplicationCog(bot))
