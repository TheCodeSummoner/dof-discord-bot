"""
TODO: Docs
"""
import discord
from discord.ext import commands
from ..bot import Bot
from ..logger import Log
from ..utils import MemberApplication
from ..constants import COMMANDS


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
        Log.debug(f"{member.display_name} joined DoF discord for the first time")

        # TODO: Put this message into a different channel
        await self._bot.channels["bot-testing"].send(f"Welcome to DoF discord, {member.display_name}! Please type !help"
                                                     f" to learn more about the clan and possible commands!")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        """
        TODO: Docs, proper code
        """
        member: discord.Member = message.author

        # Ignore commands
        if message.content in COMMANDS:
            return

        if message.channel.type == discord.ChannelType.private:
            Log.debug(f"Received a direct message from {member.display_name}")

            # Check if the message is application-related
            if member in self._bot.applications:
                self._bot.applications[member].add_answer(message.content)

                # Once last question was answered, prepare current application for a review and ask for confirmation
                if self._bot.applications[member].finished:
                    Log.debug(f"Application by {member.display_name} completed")
                    await member.send(f"You have completed the application - here is what you've written:\n"
                                      f"{self._bot.applications[member].answers}\n"
                                      f"Would you like to submit this application? Type !submit to submit it or "
                                      f"!cancel to cancel the application")
                else:
                    await member.send(f"{self._bot.applications[member].next_question}")

    @commands.dm_only()
    @commands.command()
    async def apply(self, ctx, *, member: discord.Member = None):
        """
        TODO: Docs, proper code
        """
        member = member or ctx.author
        Log.debug(f"Detected !apply command used by {member.display_name}")

        if member not in self._bot.applications:
            Log.info(f"Received new application request from {member.display_name}")
            await member.send(f"Thank you for being interested in joining DoF, {member.display_name} :)\n"
                              f"Please answer each question to submit an application (don't worry, you will have a "
                              f"chance to review your application before submission).\n"
                              f"You can cancel your application at any time by typing \"!cancel\".\n"
                              f"You can check your application progress at any time by typing \"!apply\".")
            self._bot.applications[member] = MemberApplication(member)
            await member.send(f"{self._bot.applications[member].next_question}")
        else:
            await member.send(f"You are currently on step {self._bot.applications[member].progress} out of "
                              f"{len(MemberApplication.questions)}.")

    @apply.error
    async def apply_handler(self, ctx, error: discord.DiscordException):
        """
        TODO: Docs
        """
        member = ctx.author

        if isinstance(error, commands.PrivateMessageOnly):
            Log.debug(f"Detected !apply command in a non-dm context, from {member.display_name}")
            await member.send("Hi! I have noticed you've tried to use the !apply command, but it can only be used in a "
                              "direct message. If you would like to start a DoF application, please type the command "
                              "again here.")

    @commands.dm_only()
    @commands.command()
    async def submit(self, ctx, *, member: discord.Member = None):
        """
        TODO: Docs, proper code
        """
        member = member or ctx.author
        Log.debug(f"Detected !submit command used by {member.display_name}")

        if member in self._bot.applications and self._bot.applications[member].finished:
            Log.info(f"Received application submission request from {member.display_name}")

            await self._submit_application(member)
            await member.send(f"Application from {member.display_name} submitted")
            del self._bot.applications[member]
        else:
            await member.send(f"Couldn't find a finished application from {member.display_name} - please check you "
                              f"have completed an application by using the !apply command")

    @submit.error
    async def submit_handler(self, ctx, error: discord.DiscordException):
        """
        TODO: Docs
        """
        member = ctx.author

        if isinstance(error, commands.PrivateMessageOnly):
            Log.debug(f"Detected !submit command in a non-dm context, from {member.display_name}")
            await member.send("Hi! I have noticed you've tried to use the !submit command, but it can only be used in a"
                              " direct message. If you would like to submit a DoF application, please type the command "
                              "again here.")

    @commands.dm_only()
    @commands.command()
    async def cancel(self, ctx, *, member: discord.Member = None):
        """
        TODO: Docs, proper code
        """
        member = member or ctx.author
        Log.debug(f"Detected !cancel command used by {member.display_name}")

        if member in self._bot.applications:
            Log.info(f"Received application cancellation request from {member.display_name}")
            await member.send(f"Application from {member.display_name} successfully cancelled")
            del self._bot.applications[member]
        else:
            await member.send(f"Couldn't find a started application from {member.display_name} - please check you "
                              f"have started an application by using the !apply command")

    @cancel.error
    async def cancel_handler(self, ctx, error: discord.DiscordException):
        """
        TODO: Docs
        """
        member = ctx.author

        if isinstance(error, commands.PrivateMessageOnly):
            Log.debug(f"Detected !cancel command in a non-dm context, from {member.display_name}")
            await member.send("Hi! I have noticed you've tried to use the !cancel command, but it can only be used in a"
                              " direct message. If you would like to cancel a DoF application, please type the command "
                              "again here.")

    async def _submit_application(self, member: discord.Member):
        """
        TODO: Docs
        """
        await self._bot.channels["applications"].send(f"New application from {member.display_name}:\n\n"
                                                      f"{self._bot.applications[member].answers}")


def setup(bot: commands.Bot):
    """
    TODO: Docs
    """
    bot.add_cog(ApplicationCog(bot))
