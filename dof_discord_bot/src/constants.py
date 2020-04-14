"""
Constants and other static values.
"""
import os as _os

# Declare path to the root folder (dof-discord-bot)
ROOT_DIR = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), "..", ".."))

# Declare path to the source root folder (dof_discord_bot)
DOF_DISCORD_BOT_DIR = _os.path.join(ROOT_DIR, "dof_discord_bot")

# Declare paths to the main folders
SRC_DIR = _os.path.join(DOF_DISCORD_BOT_DIR, "src")
LOG_DIR = _os.path.join(DOF_DISCORD_BOT_DIR, "log")
TESTS_DIR = _os.path.join(ROOT_DIR, "tests")

# Declare the command prefix - each command must have this prefix in front in order to be considered a command
COMMAND_PREFIX = "!"

# Declare the maximum number of the lines for the !help command
MAX_HELP_LINES = 8

# Declare the amount of seconds to wait until help session is deleted
HELP_SESSION_TIMEOUT = 60

with open(_os.path.join(ROOT_DIR, "token.txt")) as f:
    TOKEN = f.read().strip()