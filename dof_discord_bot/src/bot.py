"""
Dof Discord Bot
===============

Module storing the bot master class - an extended version of Discord's commands bot.
"""
import typing
import discord
from discord.ext import commands
from .logger import Log
from .utils import MemberApplication
from .constants import COMMANDS_ORDER


class Bot(commands.Bot):
    """
    Dof discord bot class, storing all crucial functionality of the bot.

    Functions
    ---------

    The following list shortly summarises each function:

        * channels - get guild channels
        * applications - get applications
        * on_ready - inform about successfully logging in, and discover channels
        * _discover_channels - helper to find all guild-related channels and save them
        * _load_extensions - load the cogs

    Usage
    -----

    You should create the bot and run it with a token, as follows:

        Bot(command_prefix="!").run(TOKEN)
    """

    def __init__(self, command_prefix: str):
        super().__init__(command_prefix, activity=discord.Game(name="Commands: !help"))
        self._applications = dict()
        self._channels = dict()
        self._load_extensions()
        self._verify_commands_order()

    def _load_extensions(self):
        """
        Function used to load all cogs.
        """
        self.load_extension("dof_discord_bot.src.cogs.help")
        self.load_extension("dof_discord_bot.src.cogs.info")
        self.load_extension("dof_discord_bot.src.cogs.apply")
        Log.info("Extensions loaded")

    def _verify_commands_order(self):
        """
        Function used to check if the order of all commands has been specified, and alphabetically sort any un-ordered
        commands.
        """
        command_names = {cmd.name for cmd in self.commands}

        # Check that all commands have been "registered" in the ordering list
        difference = command_names.difference(set(COMMANDS_ORDER))
        if difference:
            Log.warning(f"The order of some commands has not been specified. Please specify the order of {difference} "
                        f"in constants.py - otherwise the commands will be added to the end of the list alphabetically")
            for command in sorted(difference):
                COMMANDS_ORDER.append(command)

    @property
    def channels(self) -> typing.Dict[str, discord.TextChannel]:
        """
        Getter to retrieve a mapping of channel name to channel instance.
        """
        return self._channels

    @property
    def applications(self) -> typing.Dict[discord.Member, MemberApplication]:
        """
        Getter to retrieve a mapping of member instance to application instance.
        """
        return self._applications

    def _discover_channels(self):
        """
        Helper function used to discover all channels and store them in a dict.
        """
        for channel in self.get_all_channels():
            self._channels[channel.name] = channel

    async def on_ready(self):
        """
        Upon logging, the bot will inform about it's user name and id, as well as discover all guild channels.
        """
        Log.info(f"Logged on as {self.user}")
        self._discover_channels()
