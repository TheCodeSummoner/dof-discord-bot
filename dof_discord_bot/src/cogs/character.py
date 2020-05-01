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

        # Fetch the characters by checking if the class annotations start with the face code specific string
        self.characters = {char[0] for char in strings.Characters if char[1].startswith("<BodyProperties")}

    @commands.command()
    async def character(self, ctx: commands.Context, name: str = ""):
        """
        Face command provides character after short explanation what the user needs to do.

        Some examples of the command:

        # TODO: Outdated! Fix it!
           1. !character -> explains the user how to get a face and which names are available
           2. !character name -> returns the specific face for the input name

        """
        if name:
            if name in self.characters:
                await ctx.send(getattr(strings.Characters, name))
            else:
                await self.character_handler(ctx, CharacterNotFound(strings.Characters.invalid_query.format(name)))
        else:
            # TODO: See message regarding this in strings.py - should be multiple messages instead (but we can reformat
            #  this once we create a session) - so treat this as low priority
            await ctx.send(strings.Characters.introduction)

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
