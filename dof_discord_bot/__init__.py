"""
TODO
"""
from dof_discord_bot.src import Bot, COMMAND_PREFIX, TOKEN

__name__ = "dof-discord-bot"
__version__ = "1.4.0"
__description__ = "Defenders of Faith's discord bot"
__lead__ = "Florianski Kacper"
__email__ = "kacper.florianski@gmail.com"
__url__ = "https://github.com/TheCodeSummoner/dof-discord-bot"


def run():
    """
    TODO
    """
    Bot(COMMAND_PREFIX).run(TOKEN)
