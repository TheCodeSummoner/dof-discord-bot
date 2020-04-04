"""
TODO: Docs
"""
import os as _os

# Declare path to the root folder (dof-discord-bot)
ROOT_DIR = _os.path.normpath(_os.path.join(_os.path.dirname(__file__), ".."))

# Declare paths to the main folders
SRC_DIR = _os.path.join(ROOT_DIR, "src")
LOG_DIR = _os.path.join(ROOT_DIR, "log")
TESTS_DIR = _os.path.join(ROOT_DIR, "tests")

COMMAND_PREFIX = "!"
COMMANDS = [
    "!apply",
    "!cancel",
    "!submit"
]
TOKEN = ""
