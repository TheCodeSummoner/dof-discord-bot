"""
TODO
"""
from dof_discord_bot.src import Bot, COMMAND_PREFIX, TOKEN
from __meta__ import \
    NAME as _NAME, \
    VERSION as _VERSION, \
    DESCRIPTION as _DESCRIPTION, \
    LEAD as _LEAD, \
    EMAIL as _EMAIL, \
    URL as _URL

__name__ = _NAME
__version__ = _VERSION
__description__ = _DESCRIPTION
__lead__ = _LEAD
__email__ = _EMAIL
__url__ = _URL


def run():
    """
    TODO
    """
    Bot(COMMAND_PREFIX).run(TOKEN)
