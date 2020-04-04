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

COMMAND_PREFIX = "!"
COMMANDS = [
    "!apply",
    "!cancel",
    "!submit"
]
TOKEN = ""
