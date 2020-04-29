"""
TODO: Match other cogs exact formatting, docs are important and should be maintained in the same way

TODO: See the warning message when you run the code - this should be self-explanatory and quickly fix-able

bannerlord character Cog
===============

Module storing bannerlord character functionality.
Allows you to receive a certain character code depending on the user's input.

TODO
1. Get the command
2. Get the command working with and without parameters to print a different message
3. Get some sample faces in the code
4. Get the error message (face not found)
5. Verify the command works as expected (output ok and error-case ok)
6. Figure out formatting

"""
# TODO: Remove unused imports
import discord
import inspect
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


class CharacterNotFound(discord.DiscordException):
    """
    Raised when the character-fetching query doesn't match any of the supported characters.
    """
    def __init__(self, arg: str):
        super().__init__(arg)


# TODO: Classes in Python are in CamelCase convention, I would also change the name to just be Character (we know it's
#  a Bannerlord character, or possibly give it an entirely different name (?)
class bl_character(commands.Cog):
    # TODO: Match the format of the docstring to the other cog's docstrings, make sure you don't go over the character
    #  limit, and the indentation is correct
    """
        Character cog provides html codes for characters in bannerlord

        Commands
        --------

            * bl_character - starts the module, providing the current available characters depending on the user's input gender
        """

    # TODO: Signature of this function is wrong, see other cogs
    def __init__(self, ctx: commands.Context, command: str = ""):
        super().__init__()

        # Fetch the characters by checking if the class annotations start with the face code specific string
        self.characters = {char[0] for char in strings.Bl_Characters if char[1].startswith("<BodyProperties")}

    # TODO: I would consider changing the name of this command, to either "character" or maybe even shorter, "face", not
    #  really sure. "command" argument should be changed to something more meaningful, such as "name" - to represent
    #  what the other argument actually is (note the command is used as !bl_character <name>, so it would make sense
    #  to call it "name")
    @commands.command()
    async def bl_character(self, ctx: commands.Context, command: str = ""):
        if command:
            if command in self.characters:
                await ctx.send(getattr(strings.Bl_Characters, command))
            else:
                await self.bl_character_handler(ctx, CharacterNotFound(strings.Bl_Characters.invalid_query.format(command)))
        else:
            # TODO: See message regarding this in strings.py - should be multiple messages instead (but we can reformat
            #  this once we create a session) - so treat this as low priority
            await ctx.send(strings.Bl_Characters.introduction)

    @bl_character.error
    async def bl_character_handler(self, ctx: commands.Context, error: discord.DiscordException):
        """
        Custom handler needed to handle the custom error - the user should be informed about an invalid character.
        """
        if isinstance(error, CharacterNotFound):
            Log.debug(f"Caught invalid character error - {error}")
            embed = discord.Embed()
            embed.colour = discord.Colour.red()
            embed.title = str(error)
            await ctx.send(embed=embed)
        else:
            raise


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(bl_character(bot))
