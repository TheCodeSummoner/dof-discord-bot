"""
Tests associated with the !version command.
"""
import time
import pytest
from . import helpers
from dof_discord_bot.src.logger import Log


def test_returns_current_version(timeout: int = 10, delay: int = 3):
    """
    Simply calling the command should result in bot's current version being printed.
    """
    helpers.call(helpers.get_test_channel().send("!version"))

    current_time = time.time()
    while True:
        if time.time() - current_time > timeout:
            pytest.fail("Timed out waiting for response to the !version command")
        else:
            message = helpers.get_test_channel().last_message
            if message and message.author.name == "DofDevBotApplication":
                assert 0 == 0  # TODO: Check content
                break

        Log.debug("Waiting for the response to the !version command to appear")
        time.sleep(delay)
