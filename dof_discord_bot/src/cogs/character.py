"""
Module storing character code fetching functionality.
"""
import discord
import typing
from discord.ext import commands
from .. import strings
from ..utils import Session, LinePaginator, MessageEmbed, Page
from ..constants import BANNERLORD_CHARACTER_ICON, DONT_CAPITALISE, \
    FEMALE_CHARACTER_SPACE, FEMALE_CHARACTERS_PER_LINE, \
    MALE_CHARACTER_SPACE, MALE_CHARACTERS_PER_LINE, \
    CUSTOM_CHARACTER_SPACE, CUSTOM_CHARACTERS_PER_LINE
from ..bot import Bot
from ..logger import Log


def split(iterable: typing.Iterable, chunks: int) -> typing.List[typing.List]:
    """
    Helper function to split an iterable into a number of chunks in a tuple.
    """
    new_items = [[]]
    for item in iterable:
        if len(new_items[-1]) == chunks:
            new_items.append([])
        new_items[-1].append(item)
    return new_items


# Fetch the characters by checking if the class annotations start with the character code specific string
CUSTOM_CHARACTERS = {char[0] for char in strings.CustomCharacters if char[1].startswith("<BodyProperties")}
FEMALE_CHARACTERS = {char[0] for char in strings.FemaleCharacters if char[1].startswith("<BodyProperties")}
MALE_CHARACTERS = {char[0] for char in strings.MaleCharacters if char[1].startswith("<BodyProperties")}

# Create lists which store the characters in smaller chunks, so that multiple characters can be displayed same line
CUSTOM_CHARACTERS_SPLIT = split(sorted(CUSTOM_CHARACTERS), CUSTOM_CHARACTERS_PER_LINE)
FEMALE_CHARACTERS_SPLIT = split(sorted(FEMALE_CHARACTERS), FEMALE_CHARACTERS_PER_LINE)
MALE_CHARACTERS_SPLIT = split(sorted(MALE_CHARACTERS), MALE_CHARACTERS_PER_LINE)


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
        paginator = LinePaginator(prefix="", suffix="", max_size=4096)

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
        paginator.add_line("```")
        for characters in CUSTOM_CHARACTERS_SPLIT:
            paginator.add_line("".join(f"{self._format_name(char):<{CUSTOM_CHARACTER_SPACE}}" for char in characters))
        paginator.add_line("```")
        paginator.close_page()

        paginator.add_line(strings.Characters.available_female_characters)
        paginator.add_line("```")
        for characters in FEMALE_CHARACTERS_SPLIT:
            paginator.add_line("".join(f"{self._format_name(char):<{FEMALE_CHARACTER_SPACE}}" for char in characters))
        paginator.add_line("```")
        paginator.close_page()

        paginator.add_line(strings.Characters.available_male_characters)
        paginator.add_line("```")
        for characters in MALE_CHARACTERS_SPLIT:
            paginator.add_line("".join(f"{self._format_name(char):<{MALE_CHARACTER_SPACE}}" for char in characters))
        paginator.add_line("```")

        # Save organised pages to the session
        self.pages = paginator.pages

    @staticmethod
    def _format_name(name: str):
        """
        Helper function used to format a name so it appears properly in the message.
        """
        return "• " + " ".join(part.capitalize() if part not in DONT_CAPITALISE else part for part in name.split("_"))


class CharacterCog(commands.Cog):
    """
    Character Cog is a discord extension providing a certain bannerlord character face based on the user's input name.
    """

    def __init__(self, bot: Bot):
        super().__init__()
        self.bot = bot

    @commands.command(aliases=["characters"])
    async def character(self, ctx: commands.Context, *name):
        """
        Provides a character code (you can copy the code into the character edition screen in Bannerlord).

        Some examples of the command:

           1. `!character` -> explains how to get a character code and which names are available
           2. `!character <name>` -> returns the specific character code using the input name
        """
        member = ctx.author
        Log.debug(f"Detected !character command used by {member.display_name}")

        if name:
            # Make sure commands such as "!character Rhagaea" or "!character Stannis Baratheon" work
            name_formatted = "_".join(part.lower() for part in name) if len(name) > 1 else name[0].lower()
            name = " ".join(part for part in name) if len(name) > 1 else name[0]
            Log.debug(f"Retrieving {name_formatted} preset for {member.display_name}")

            # Embed the character code in a nicely visible "box"
            if name_formatted in MALE_CHARACTERS:
                await ctx.send(embed=MessageEmbed(getattr(strings.MaleCharacters, name_formatted)))
            elif name_formatted in FEMALE_CHARACTERS:
                await ctx.send(embed=MessageEmbed(getattr(strings.FemaleCharacters, name_formatted)))
            elif name_formatted in CUSTOM_CHARACTERS:
                await ctx.send(embed=MessageEmbed(getattr(strings.CustomCharacters, name_formatted)))
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
