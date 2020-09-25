"""
Dof discord bot package - exposes some meta information and a helper command to run the code.
"""
import json
import os
from dof_discord_bot.src import Bot, constants

with open(os.path.join(constants.RES_DIR, "meta.json")) as f:
    metadata = json.load(f)

__title__ = metadata["__title__"]
__version__ = metadata["__version__"]
__description__ = metadata["__description__"]
__lead__ = metadata["__lead__"]
__email__ = metadata["__email__"]
__url__ = metadata["__url__"]


def run():
    """
    Run the bot (can be used from within the package).
    """
    Bot(constants.COMMAND_PREFIX).run(constants.TOKEN)


__all__ = [
    "__title__",
    "__version__",
    "__description__",
    "__lead__",
    "__email__",
    "__url__",
    "run"
]
