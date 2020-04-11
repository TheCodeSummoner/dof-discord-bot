"""
Application Cog
===============

Module storing DoF member application related functionality.
"""
import discord
from discord.ext import commands
from .. import strings
from ..bot import Bot
from ..logger import Log
from ..utils import MemberApplication
from ..constants import COMMANDS


class ApplicationCog(commands.Cog):
    """
    Application Cog is a discord extension providing a set of application-related commands and listeners.

    Listeners
    ---------

        * on_message - Listen to direct messages and collect application information

    Commands
    --------

        * apply - Start a new DoF member application or display information about the current one
        * submit - Submit a finished application (uses _submit_application function)
        * cancel - Cancel an in-progress application
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self._bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        Listener providing a way to listen to a conversation once an application was started.

        The functionality is as follows:

            1. If an application is started, the message is treated as an answer to the question
            2. If the application wasn't yet finished, the answer is registered
            3. If the application was finished (or has finished with the last answer), relevant message is displayed
            4. If still relevant, next question is displayed
        """
        member: discord.Member = message.author

        # Ignore commands
        if message.content in COMMANDS:
            return

        if message.channel.type == discord.ChannelType.private:
            Log.debug(f"Received a direct message from {member.display_name}")

            # Check if the message is application-related
            if member in self._bot.applications:
                if not self._bot.applications[member].finished:
                    self._bot.applications[member].add_answer(message.content)

                # Once last question was answered, prepare current application for a review and ask for confirmation
                if self._bot.applications[member].finished:
                    Log.debug(f"Application by {member.display_name} completed")
                    await member.send(strings.MEMBER_APPLICATION_COMPLETED
                                      .format(self._bot.applications[member].answers))
                else:
                    await member.send(f"{self._bot.applications[member].question}")

    @commands.dm_only()
    @commands.command()
    async def apply(self, ctx, *, member: discord.Member = None):
        """
        Apply command is used to start a new member application, or display progress of the current one.

        Current steps are as follows:

            1. If application hasn't yet started, a new application is created and first question asked
            2. If application is already in progress but not finished, progress is displayed and question repeated
            3. If application is in progress and finished, submission request message is displayed
        """
        member = member or ctx.author
        Log.debug(f"Detected !apply command used by {member.display_name}")

        if member not in self._bot.applications:
            Log.info(f"Received new application request from {member.display_name}")
            await member.send(strings.NEW_MEMBER_APPLICATION.format(member.display_name))
            self._bot.applications[member] = MemberApplication(member)
            await member.send(f"{self._bot.applications[member].question}")
        else:
            if self._bot.applications[member].finished:
                await member.send(strings.MEMBER_APPLICATION_COMPLETED
                                  .format(self._bot.applications[member].answers))
            else:
                await member.send(strings.CHECK_APPLICATION_PROGRESS
                                  .format(self._bot.applications[member].progress, len(MemberApplication.questions),
                                          self._bot.applications[member].question))

    @apply.error
    async def apply_handler(self, ctx, error: discord.DiscordException):
        """
        Since apply is a direct-message-only command, an error handler is required to respond to the command calls
        outside of a DM context.
        """
        member = ctx.author

        if isinstance(error, commands.PrivateMessageOnly):
            Log.debug(f"Detected !apply command in a non-dm context, from {member.display_name}")
            await member.send(strings.NOT_APPLICATION_DM.format("!apply", "start"))

    @commands.dm_only()
    @commands.command()
    async def submit(self, ctx, *, member: discord.Member = None):
        """
        Submit command is used to submit a finished application.

        Current steps are as follows:

            1. If application isn't finished, relevant help message is displayed
            2. If application is finished, it is then formatted and submitted to the applications channel
        """
        member = member or ctx.author
        Log.debug(f"Detected !submit command used by {member.display_name}")

        if member in self._bot.applications and self._bot.applications[member].finished:
            Log.info(f"Received application submission request from {member.display_name}")

            await self._submit_application(member)
            await member.send(strings.APPLICATION_SUBMITTED.format(member.display_name))
            del self._bot.applications[member]
        else:
            await member.send(strings.APPLICATION_UNFINISHED.format(member.display_name))

    @submit.error
    async def submit_handler(self, ctx, error: discord.DiscordException):
        """
        Since submit is a direct-message-only command, an error handler is required to respond to the command calls
        outside of a DM context.
        """
        member = ctx.author

        if isinstance(error, commands.PrivateMessageOnly):
            Log.debug(f"Detected !submit command in a non-dm context, from {member.display_name}")
            await member.send(strings.NOT_APPLICATION_DM.format("!submit", "submit"))

    @commands.dm_only()
    @commands.command()
    async def cancel(self, ctx, *, member: discord.Member = None):
        """
        Cancel command is used to cancel an in-progress application.

        Current steps are as follows:

            1. If application isn't started, relevant help message is displayed
            2. If application is started, it is then cancelled and removed from the applications dictionary
        """
        member = member or ctx.author
        Log.debug(f"Detected !cancel command used by {member.display_name}")

        if member in self._bot.applications:
            Log.info(f"Received application cancellation request from {member.display_name}")
            await member.send(strings.APPLICATION_CANCELLED.format(member.display_name))
            del self._bot.applications[member]
        else:
            await member.send(strings.APPLICATION_NOT_STARTED.format(member.display_name))

    @cancel.error
    async def cancel_handler(self, ctx, error: discord.DiscordException):
        """
        Since cancel is a direct-message-only command, an error handler is required to respond to the command calls
        outside of a DM context.
        """
        member = ctx.author

        if isinstance(error, commands.PrivateMessageOnly):
            Log.debug(f"Detected !cancel command in a non-dm context, from {member.display_name}")
            await member.send(strings.NOT_APPLICATION_DM.format("!cancel", "cancel"))

    async def _submit_application(self, member: discord.Member):
        """
        Helper method to format and send an application to the relevant channel.
        """
        await self._bot.channels["applications"].send(
            strings.SUBMIT_APPLICATION.format(member.display_name, self._bot.applications[member].answers))


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(ApplicationCog(bot))
