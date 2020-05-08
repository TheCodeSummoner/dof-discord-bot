"""
Dof discord bot package - exposes some meta information and a helper command to run the code.
"""
import json as _json
import os as _os
from dof_discord_bot.src import Bot as _Bot, COMMAND_PREFIX as _PREFIX, TOKEN as _TOKEN, RES_DIR as _RES_DIR

with open(_os.path.join(_RES_DIR, "meta.json")) as f:
    metadata = _json.load(f)

__title__ = metadata["__title__"]
__version__ = metadata["__version__"]
__description__ = metadata["__description__"]
__lead__ = metadata["__lead__"]
__email__ = metadata["__email__"]
__url__ = metadata["__url__"]


def run():
    """
    Helper function to easily run the bot.
    """
    _Bot(_PREFIX).run(_TOKEN)
