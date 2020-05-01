"""
Character Cog
=============

Module storing character code fetching functionality.
"""
import discord
from discord.ext import commands
from .. import strings
from ..utils import Session, LinePaginator
from ..constants import MAX_CHARACTER_LINES
from ..bot import Bot
from ..logger import Log

# Fetch the characters by checking if the class annotations start with the face code specific string
CHARACTERS = {char[0] for char in strings.Characters if char[1].startswith("<BodyProperties")}


class CharacterNotFound(discord.DiscordException):
    """
    Raised when the character-fetching query doesn't match any of the supported characters.
    """
    def __init__(self, arg: str):
        super().__init__(arg)


class CharacterSession(Session):
    """
    Character Session allowing retrieving the Bannerlord character codes.
    """

    async def build_pages(self):
        """
        Builds predefined pages and puts them into the paginator.
        """
        paginator = LinePaginator(prefix="", suffix="", max_lines=MAX_CHARACTER_LINES)

        # Add the introduction and the available characters header
        paginator.add_line(strings.Characters.introduction + "\n")
        paginator.add_line(strings.Characters.available_characters)

        # Add (formatted) names
        for name in sorted(CHARACTERS):
            paginator.add_line("• " + name.capitalize())

        # Save organised pages to the session
        self.pages = paginator.pages


class CharacterCog(commands.Cog):
    """
    Character Cog is a discord extension providing a certain bannerlord character face based on the user's input name.
    """
    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command()
    async def character(self, ctx: commands.Context, name: str = ""):
        """
        Provides a character code (you can copy the code into the character edition screen in Bannerlord).

        Some examples of the command:

           1. !character -> explains how to get a character code and which names are available
           2. !character <name> -> returns the specific character code using the input name
        """
        if name:

            # Make sure commands such as "!character Rhagaea" work
            name = name.lower()

            # Embed the character code in a nicely visible "box"
            if name in CHARACTERS:
                embed = discord.Embed()
                embed.colour = discord.Colour.green()
                embed.title = getattr(strings.Characters, name)
                await ctx.send(embed=embed)
            else:
                await self.character_handler(ctx, CharacterNotFound(strings.Characters.invalid_character.format(name)))
        else:
            await CharacterSession.start(ctx, strings.Characters.title)

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
