"""
Module storing character code fetching functionality.
"""
import discord
from discord.ext import commands
from .. import strings
from ..utils import Session, LinePaginator, MessageEmbed, Page
from ..constants import BANNERLORD_CHARACTER_ICON
from ..bot import Bot
from ..logger import Log

# Fetch the characters by checking if the class annotations start with the character code specific string
FEMALE_CHARACTERS = {char[0] for char in strings.FemaleCharacters if char[1].startswith("<BodyProperties")}
MALE_CHARACTERS = {char[0] for char in strings.MaleCharacters if char[1].startswith("<BodyProperties")}
CUSTOM_CHARACTERS = {char[0] for char in strings.CustomCharacters if char[1].startswith("<BodyProperties")}


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
        paginator = LinePaginator(prefix="", suffix="")

        # Add the introduction, then each section will have a separate header and list of characters
        paginator.add_page(Page(
            strings.Characters.introduction,
            "",
            strings.Characters.explanation,
            "",
            strings.Characters.example_success,
            "",
            "```" + strings.FemaleCharacters.rhagaea + "```"
        ))

        paginator.add_line(strings.Characters.available_custom_characters)
        for name in sorted(CUSTOM_CHARACTERS):
            paginator.add_line("• " + name.capitalize())
        paginator.close_page()

        paginator.add_line(strings.Characters.available_female_characters)
        for name in sorted(FEMALE_CHARACTERS):
            paginator.add_line("• " + name.capitalize())
        paginator.close_page()

        paginator.add_line(strings.Characters.available_male_characters)
        for name in sorted(MALE_CHARACTERS):
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

    @commands.command(aliases=["characters"])
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
            if name in MALE_CHARACTERS:
                await ctx.send(embed=MessageEmbed(getattr(strings.MaleCharacters, name)))
            elif name in FEMALE_CHARACTERS:
                await ctx.send(embed=MessageEmbed(getattr(strings.FemaleCharacters, name)))
            elif name in CUSTOM_CHARACTERS:
                await ctx.send(embed=MessageEmbed(getattr(strings.CustomCharacters, name)))
            else:
                await self.character_handler(ctx, CharacterNotFound(strings.Characters.invalid_character.format(name)))
        else:
            await CharacterSession.start(ctx, strings.Characters.title, icon=BANNERLORD_CHARACTER_ICON)

    @character.error
    async def character_handler(self, ctx: commands.Context, error: discord.DiscordException):
        """
        Custom handler needed to handle the custom error - the user should be informed about an invalid character.
        """
        if isinstance(error, CharacterNotFound):
            Log.debug(f"Caught invalid character error - {error}")
            await ctx.send(embed=MessageEmbed(str(error), negative=True))
        else:
            raise


def setup(bot: commands.Bot):
    """
    Standard setup, loads the cog.
    """
    bot.add_cog(CharacterCog(bot))
