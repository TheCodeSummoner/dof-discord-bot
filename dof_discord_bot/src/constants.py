"""
Static values.
"""
import os
import sys
import yaml
import dotenv

# Declare path to the root folder (dof-discord-bot)
ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", ".."))

# Declare path to the source root folder (dof_discord_bot)
DOF_DISCORD_BOT_DIR = os.path.join(ROOT_DIR, "dof_discord_bot")

# Declare paths to the main folders
SRC_DIR = os.path.join(DOF_DISCORD_BOT_DIR, "src")
LOG_DIR = os.path.join(DOF_DISCORD_BOT_DIR, "log")
RES_DIR = os.path.join(DOF_DISCORD_BOT_DIR, "res")
TESTS_DIR = os.path.join(ROOT_DIR, "tests")

# Declare allowed file handler names, and path to the logging configuration file
LOG_CONFIG_FILE_PATH = os.path.join(RES_DIR, "log-config.json")
LOG_FILE_HANDLERS = {"logging.FileHandler", "dof_discord_bot.res.restricted_file_handler.RestrictedFileHandler",
                     "dof_discord_bot.res.verbose_file_handler.VerboseFileHandler"}


if os.path.exists(os.path.join(RES_DIR, "strings.yaml")):
    with open(os.path.join(RES_DIR, "strings.yaml"), encoding="UTF-8") as f:
        CONFIG_YAML = yaml.safe_load(f)
else:
    print(f"Couldn't find strings.yaml file at {RES_DIR}", file=sys.stderr)
    sys.exit(1)

# Hard code the root section as the yaml file is only used for strings resources
YAML_STRINGS_ROOT_FIELD = "strings"

# Load environment variables
dotenv.load_dotenv(os.path.join(DOF_DISCORD_BOT_DIR, ".env"))

# Retrieve the token - either it will be an environment variable, or will be in the text file
TOKEN = os.getenv("DOF_TOKEN", "")
if not TOKEN:
    if os.path.exists(os.path.join(RES_DIR, "token")):
        with open(os.path.join(RES_DIR, "token")) as f:
            TOKEN = f.read().strip()
    else:
        print(f"Missing token - either declare \"DOF_TOKEN\" environment variable or include the token in the "
              f"\"token\" file at \"{os.path.join(RES_DIR, 'token')}\"", file=sys.stderr)
        sys.exit(1)

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
