"""
Application Cog
===============TODO

Module storing DoF member application related functionality.
"""
import discord
from discord.ext import commands
from .. import strings
from ..bot import Bot
from ..logger import Log
from ..utils import MemberApplication


class ApplicationCog(commands.Cog):
    """
    Application Cog is a discord extension providing a set of application-related commands and listeners.

    Listeners TODO
    ---------

        * on_message - Listen to direct messages and collect application information

    Commands
    --------

        * apply - Start a new DoF member application or display information about the current one
        * submit - Submit a finished application (uses submit_application function)
        * cancel - Cancel an in-progress application
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

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
        if message.content.startswith("!") and message.content[1:] in self.bot.all_commands.keys():
            return

        if message.channel.type == discord.ChannelType.private:
            Log.debug(f"Received a direct message from {member.display_name}")

            # Check if the message is application-related
            if member in self.bot.applications:
                if not self.bot.applications[member].finished:
                    self.bot.applications[member].add_answer(message.content)

                # Once last question was answered, prepare current application for a review and ask for confirmation
                if self.bot.applications[member].finished:
                    Log.debug(f"Application by {member.display_name} completed")
                    await member.send(strings.Application.completed
                                      .format(self.bot.applications[member].answers))
                else:
                    await member.send(f"{self.bot.applications[member].question}")

    @commands.command()
    async def apply(self, ctx: commands.Context):
        """
        Apply command is used to start a new member application, or display progress of the current one.

        Current steps are as follows:

            1. If application hasn't yet started, a new application is created and first question asked
            2. If application is already in progress but not finished, progress is displayed and question repeated
            3. If application is in progress and finished, submission request message is displayed
        """
        member = ctx.author
        Log.debug(f"Detected !apply command used by {member.display_name}")

        # Apply command is a dm-only command. Not using dm_only check to allow other checks in help command.
        if ctx.guild is not None:
            Log.debug(f"Detected !apply command in a non-dm context, from {member.display_name}")
            await member.send(strings.Application.dm_only.format("!apply", "start"))
            return

        if member not in self.bot.applications:
            Log.info(f"Received new application request from {member.display_name}")
            await member.send(strings.Application.new_application.format(member.display_name))
            self.bot.applications[member] = MemberApplication(member)
            await member.send(f"{self.bot.applications[member].question}")
        else:
            if self.bot.applications[member].finished:
                await member.send(strings.Application.completed
                                  .format(self.bot.applications[member].answers))
            else:
                await member.send(strings.Application.check_progress
                                  .format(self.bot.applications[member].progress, len(MemberApplication.questions),
                                          self.bot.applications[member].question))

    @commands.command()
    async def submit(self, ctx: commands.Context):
        """
        Submit command is used to submit a finished application.

        Current steps are as follows:

            1. If application isn't finished, relevant help message is displayed
            2. If application is finished, it is then formatted and submitted to the applications channel
        """
        member = ctx.author
        Log.debug(f"Detected !submit command used by {member.display_name}")

        # Submit command is a dm-only command. Not using dm_only check to allow other checks in help command.
        if ctx.guild is not None:
            Log.debug(f"Detected !submit command in a non-dm context, from {member.display_name}")
            await member.send(strings.Application.dm_only.format("!submit", "submit"))
            return

        if member in self.bot.applications and self.bot.applications[member].finished:
            Log.info(f"Received application submission request from {member.display_name}")

            await self.submit_application(member)
            await member.send(strings.Application.submitted.format(member.display_name))
            del self.bot.applications[member]
        else:
            await member.send(strings.Application.unfinished.format(member.display_name))

    @commands.command()
    async def cancel(self, ctx: commands.Context):
        """
        Cancel command is used to cancel an in-progress application.

        Current steps are as follows:

            1. If application isn't started, relevant help message is displayed
            2. If application is started, it is then cancelled and removed from the applications dictionary
        """
        member = ctx.author
        Log.debug(f"Detected !cancel command used by {member.display_name}")

        # Cancel command is a dm-only command. Not using dm_only check to allow other checks in help command.
        if ctx.guild is not None:
            Log.debug(f"Detected !cancel command in a non-dm context, from {member.display_name}")
            await member.send(strings.Application.dm_only.format("!cancel", "cancel"))
            return

        if member in self.bot.applications:
            Log.info(f"Received application cancellation request from {member.display_name}")
            await member.send(strings.Application.cancelled.format(member.display_name))
            del self.bot.applications[member]
        else:
            await member.send(strings.Application.not_started.format(member.display_name))

    async def submit_application(self, member: discord.Member):
        """
        Helper method to format and send an application to the relevant channel.
        """
        await self.bot.channels["applications"].send(
            strings.Application.submit.format(member.display_name, self.bot.applications[member].answers))


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(ApplicationCog(bot))
