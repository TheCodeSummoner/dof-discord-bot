"""
Tests associated with the !version command.
"""
import asyncio
import pytest
import time
import dof_discord_bot
from . import helpers
from dof_discord_bot.src.logger import Log


@helpers.threaded_async
async def test_returns_current_version(timeout: int = 30, delay: int = 3):
    """
    Simply calling the command should result in bot's current version being printed.
    """
    await helpers.get_test_channel().send("!version")

    current_time = time.time()
    while True:
        if time.time() - current_time > timeout:
            pytest.fail("Timed out waiting for response to the !version command")
        else:
            message = helpers.get_test_channel().last_message
            if message and message.author.name == "DofDevBotApplication":
                assert message.embeds[0].title == f"{dof_discord_bot.__title__} v{dof_discord_bot.__version__}"
                break

        Log.debug("Waiting for the response to the !version command to appear")
        await asyncio.sleep(delay)
