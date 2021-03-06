"""
Constants and other static values.
"""
import os as _os
import sys as _sys
import dotenv as _dotenv

# Declare path to the root folder (dof-discord-bot)
ROOT_DIR = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), "..", ".."))

# Declare path to the source root folder (dof_discord_bot)
DOF_DISCORD_BOT_DIR = _os.path.join(ROOT_DIR, "dof_discord_bot")

# Declare paths to the main folders
SRC_DIR = _os.path.join(DOF_DISCORD_BOT_DIR, "src")
LOG_DIR = _os.path.join(DOF_DISCORD_BOT_DIR, "log")
RES_DIR = _os.path.join(DOF_DISCORD_BOT_DIR, "res")
TESTS_DIR = _os.path.join(ROOT_DIR, "tests")

# Load environment variables
_dotenv.load_dotenv(_os.path.join(DOF_DISCORD_BOT_DIR, ".env"))

# Retrieve the token - either it will be an environment variable, or will be in the text file
TOKEN = _os.getenv("DOF_TOKEN", "")
if not TOKEN:
    if _os.path.exists(_os.path.join(RES_DIR, "token")):
        with open(_os.path.join(RES_DIR, "token")) as f:
            TOKEN = f.read().strip()
    else:
        print(f"Missing token - either declare \"DOF_TOKEN\" environment variable or include the token in the "
              f"\"token\" file at \"{_os.path.join(RES_DIR, 'token')}\"", file=_sys.stderr)
        exit(1)

# Declare the command prefix - each command must have this prefix in front in order to be considered a command
COMMAND_PREFIX = "!"

# Declare the order of commands to be displayed in the help message
COMMANDS_ORDER = [
    "info",
    "help",
    "version",
    "apply",
    "submit",
    "cancel",
    "character"
]

# Declare some emojis
DELETE_EMOJI = "\U0001f5d1"
FIRST_PAGE_EMOJI = "\u23EE"
PREVIOUS_PAGE_EMOJI = "\u2B05"
NEXT_PAGE_EMOJI = "\u27A1"
LAST_PAGE_EMOJI = "\u23ED"

# Declare some icons
DEFAULT_SESSION_ICON = "https://cdn.discordapp.com/emojis/512367613339369475.png"
BANNERLORD_CHARACTER_ICON = "https://cdn.discordapp.com/emojis/705858278005145601.png"

# Declare the maximum number of the lines for the !help command
MAX_HELP_LINES = 8

# Declare the constant to avoid capitalisation of some words in !character command
DONT_CAPITALISE = {"of", "the", "by"}

# Declare how many characters per line should be displayed in the !character command
CUSTOM_CHARACTERS_PER_LINE = 2
FEMALE_CHARACTERS_PER_LINE = 4
MALE_CHARACTERS_PER_LINE = 4

# Declare how much space a character should take in the !character command
CUSTOM_CHARACTER_SPACE = 30
FEMALE_CHARACTER_SPACE = 12
MALE_CHARACTER_SPACE = 12
