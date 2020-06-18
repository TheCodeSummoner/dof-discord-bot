"""
Tests associated with the !version command.
"""
import pytest
import dof_discord_bot
from . import helpers
from dof_discord_bot.src.logger import Log


@helpers.threaded_async
async def test_returns_current_version():
    """
    Simply calling the command should result in bot's current version being printed.
    """
    async def version_to_appear():
        """
        Make sure that the bot answers the command and current version is returned.
        """
        message = helpers.get_test_channel().last_message

        if message and message.author.name == "DofDevBotApplication":
            assert message.embeds[0].title == f"{dof_discord_bot.__title__} v{dof_discord_bot.__version__}"
            return True

        Log.debug("Waiting for the response to the !version command to appear")

    def or_fail():
        """
        Otherwise, fail the test.
        """
        pytest.fail("Timed out waiting for response to the !version command")

    await helpers.get_test_channel().send("!version")
    await helpers.wait_for(version_to_appear, or_fail)
