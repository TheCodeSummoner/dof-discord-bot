"""
Module storing the bot master class - an extended version of Discord's commands bot.
"""
import typing
import discord
from discord.ext import commands
from .logger import Log
from .utils import MemberApplication, MessageEmbed
from .constants import COMMANDS_ORDER
from . import strings


class Bot(commands.Bot):
    """
    Dof discord bot class, storing all crucial functionality of the bot.

    You should create the bot and run it with a token, as follows:

        Bot(command_prefix="!").run(TOKEN)
    """

    def __init__(self, command_prefix: str):
        super().__init__(command_prefix, activity=discord.Game(name="Commands: !help"))
        self._applications = dict()
        self._channels = dict()
        self._load_extensions()
        self._verify_commands_order()
        self._channels_being_updated = set()

    def _load_extensions(self):
        """
        Function used to load all cogs.
        """
        self.load_extension("dof_discord_bot.src.cogs.help")
        self.load_extension("dof_discord_bot.src.cogs.info")
        self.load_extension("dof_discord_bot.src.cogs.apply")
        self.load_extension("dof_discord_bot.src.cogs.character")
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
    def channels(self) -> typing.Dict[str, typing.Union[discord.TextChannel, discord.VoiceChannel]]:
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

    @property
    def guild(self) -> discord.Guild:
        """
        Getter to retrieve DoF Discord server.
        """
        return self.guilds[0]

    def _discover_channels(self):
        """
        Helper function used to discover all channels and store them in a dict.
        """
        for channel in self.get_all_channels():

            # Add channels directly - no need to add the lists of text and voice channels
            if channel.name not in {"Text Channels", "Voice Channels"}:
                self._channels[channel.name] = channel

    async def on_ready(self):
        """
        Upon logging, the bot will inform about its user name and id, as well as discover all guild channels.
        """
        Log.info(f"Logged on as {self.user}")
        self._discover_channels()

    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: typing.Union[discord.VoiceChannel, discord.TextChannel]):
        """
        Listener used to keep the channels dictionary up to date and avoid name clashes.
        """
        if channel.name in self._channels:
            Log.error(f"Attempted to create an already existing channel - name clash detected for {channel}")
            await self.channels["dof-general"].send(embed=MessageEmbed(
                strings.General.failed_create_channel.format(channel), negative=True))
            self._channels_being_updated.add(channel)
            await channel.delete()
        else:
            Log.info(f"Channel {channel} created")
            self._channels[channel.name] = channel

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: typing.Union[discord.VoiceChannel, discord.TextChannel]):
        """
        Listener used to keep the channels dictionary up to date.
        """
        Log.info(f"Channel {channel} deleted")

        # Make sure to only delete the channels that aren't part of reverting the creation process
        if channel not in self._channels_being_updated:
            del self._channels[channel.name]
        else:
            self._channels_being_updated.remove(channel)

    @commands.Cog.listener()
    async def on_guild_channel_update(self, before: typing.Union[discord.VoiceChannel, discord.TextChannel],
                                      after: typing.Union[discord.VoiceChannel, discord.TextChannel]):
        """
        Listener used to keep the channels dictionary up to date and avoid name clashes.
        """
        # Avoid handling channel updates started by this function
        if after in self._channels_being_updated:
            self._channels_being_updated.remove(after)
            return

        # Exit early if the name hasn't been changed - safe to update
        if after.name == before.name:
            Log.info(f"Channel {before} updated")
            self._channels[before.name] = after
            return

        # Revert any changes that create name clashes by editing the channel name to what it was
        if after.name in self._channels:
            Log.error(f"Attempted to rename {before} channel to {after} - {after} already exists")
            await self.channels["dof-general"].send(embed=MessageEmbed(
                strings.General.failed_rename_channel.format(before, after), negative=True))
            self._channels_being_updated.add(after)
            await after.edit(name=before.name, reason=strings.General.update_reason)
            self._channels[before.name] = after
        else:
            Log.info(f"Channel {before} updated to {after}")
            self._channels[after.name] = after
            del self._channels[before.name]
