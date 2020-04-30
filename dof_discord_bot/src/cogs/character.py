"""
Help Cog
========
Module storing help related functionality.

TODO
1. Get the command
2. Get the command working with and without parameters to print a different message
3. Get some sample faces in the code
4. Get the error message (face not found)
5. Verify the command works as expected (output ok and error-case ok)
6. Figure out formatting

TODO: See the warning message when you run the code - this should be self-explanatory and quickly fix-able

"""
import discord
from discord.ext import commands
from .. import strings, Bot
from ..logger import Log


class CharacterNotFound(discord.DiscordException):
    """
    Raised when the character-fetching query doesn't match any of the supported characters.
    """

    def __init__(self, arg: str):
        super().__init__(arg)


class CharacterCog(commands.Cog):
    """
       Character Cog is a discord extension providing a certain bannerlord character face based on the user's input name

       """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    # TODO: I would consider changing the name of this command, to either "character" or maybe even shorter, "face", not
    #  really sure. "command" argument should be changed to something more meaningful, such as "name" - to represent
    #  what the other argument actually is (note the command is used as !bl_character <name>, so it would make sense
    #  to call it "name")
    @commands.command()
    async def character(self, ctx: commands.Context, name: str = ""):
        """
               Face command provides character after short explanation what the user needs to do.

               Some examples of the command:

                   1. !face -> explains the user how to get a face and which names are available
                   2. !face name -> returns the specific face for the input name

               """
        if name:
            if name in self.name:
                await ctx.send(getattr(strings.Bl_Characters, name))
            else:
                await self.character_handler(ctx, CharacterNotFound(strings.Bl_Characters.invalid_query.format(name)))
        else:
            # TODO: See message regarding this in strings.py - should be multiple messages instead (but we can reformat
            #  this once we create a session) - so treat this as low priority
            await ctx.send(strings.Bl_Characters.introduction)

    @character.error
    async def character_handler(self, ctx: commands.Context, error: discord.DiscordException):
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
    bot.add_cog(CharacterCog(bot))
