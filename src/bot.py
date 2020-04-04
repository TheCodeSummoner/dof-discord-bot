"""
TODO: Docs
"""
import typing
import discord
from discord.ext import commands
from .logger import Log
from .utils import MemberApplication


class Bot(commands.Bot):
    """
    TODO: Docs
    """

    def __init__(self, command_prefix: str):
        super().__init__(command_prefix)
        self._applications = dict()
        self._channels = dict()
        self._load_extensions()

    def _load_extensions(self):
        """
        TODO: Docs
        """
        self.load_extension("src.cogs.apply")
        Log.info("Extensions loaded")

    @property
    def channels(self) -> typing.Dict[str, discord.TextChannel]:
        """
        TODO: Docs
        """
        return self._channels

    @property
    def applications(self) -> typing.Dict[discord.Member, MemberApplication]:
        """
        TODO: Docs
        """
        return self._applications

    def _discover_channels(self):
        """
        TODO: Docs
        """
        for channel in self.get_all_channels():
            self._channels[channel.name] = channel

    async def on_ready(self):
        """
        TODO: Docs
        """
        Log.info(f"Logged on as {self.user}")
        self._discover_channels()
