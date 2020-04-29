"""
bannerlord character Cog
===============

Module storing bannerlord character functionality.
Allows you to receive a certain character code depending on the user's input.

TODO 1. Get the command
2. Get the command working with and without parameters to print a different message
3. Get some sample faces in the code
4. Get the error message (face not found)
5. Verify the command works as expected (output ok and error-case ok)
6. Figure out formatting

"""

import discord
import asyncio
import itertools
import contextlib
from discord.ext import commands
from .. import strings
from .apply import ApplicationCog
from .help import HelpQueryNotFound
from ..constants import *
from .. import strings
from ..bot import Bot
from ..logger import Log


class bl_character(commands.Cog):
    """
        Character cog provides html codes for characters in bannerlord

        Commands
        --------

            * bl_character - starts the module, providing the current available characters depending on the user's input gender
        """

    def __init__(self, ctx: commands.Context, command: str = ""):
        super().__init__()

    @commands.command()
    async def bl_character(self, ctx: commands.Context, command: str = ""):
        if command:
            if command and getattr(strings.Bl_Characters, command):
                await ctx.send(getattr(strings.Bl_Characters.section, command))
            else:
                await ctx.send("Character name not found! Please check spelling.")
        else:

            await ctx.send(strings.Bl_Characters.introduction)


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(bl_character(bot))