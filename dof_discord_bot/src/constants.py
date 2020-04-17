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
RES_DIR = _os.path.join(DOF_DISCORD_BOT_DIR, "res")
TESTS_DIR = _os.path.join(ROOT_DIR, "tests")

# Declare the command prefix - each command must have this prefix in front in order to be considered a command
COMMAND_PREFIX = "!"

# Declare the maximum number of the lines for the !help command
MAX_HELP_LINES = 8

# Declare the amount of seconds to wait until help session is deleted
HELP_SESSION_TIMEOUT = 60

# Declare some emojis
DELETE_EMOJI = "\U0001f5d1"
FIRST_PAGE_EMOJI = "\u23EE"
PREVIOUS_PAGE_EMOJI = "\u2B05"
NEXT_PAGE_EMOJI = "\u27A1"
LAST_PAGE_EMOJI = "\u23ED"

with open(_os.path.join(RES_DIR, "token.txt")) as f:
    TOKEN = f.read().strip()

# Bannerlord Characters female

FEMALE_Chars = "Rhagaea\nIra\nElys\nIdrun\nMonchug\nUnqid\nAbagai\nAlynneth\nChalia\nLiena\nAnidha\nDebana\nHelea\n" \
               "Phaea\nSora\nPhenoria\nALCAEA\nALLYNETH\nASELA\nCHALIA\nDEBANA\nELYS\nHELEA\nLYSICA\nMINA\nNYWIN\n" \
               "PHAEA\nPHENORIA\nSIGA\nSORA\nSVANA\nZOANA"