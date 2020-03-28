"""
TODO: Docs
"""
import typing
import discord
from discord.ext import commands


class Bot(commands.Bot):
    """
    TODO: Docs
    """

    def __init__(self, command_prefix: str):
        super().__init__(command_prefix)
        self._load_extensions()

    def _load_extensions(self):
        """
        TODO: Docs
        """
        self.load_extension("src.cogs.apply")

    @property
    def channels(self) -> typing.Dict[str, discord.TextChannel]:
        """
        TODO: Docs
        """
        return {
            "bot-testing": self.get_channel(693477969888411669)
        }

    async def on_ready(self):
        """
        TODO: Docs
        """
        print(f"Logged on as {self.user}!")
