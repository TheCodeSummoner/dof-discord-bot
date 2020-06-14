"""
Helper file used to expose common constructs and setup/teardown relevant items on each run.
"""
import os as _os
import sys as _sys
import time as _time
import asyncio as _asyncio
import threading as _threading
import random as _random
import string as _string
import typing as _typing
import discord as _discord
from discord.ext import commands as _commands

# Make sure dof_discord_bot package can be found
_sys.path.append(_os.path.join(_os.path.dirname(__file__), "..", ".."))
from dof_discord_bot.src.bot import Bot as _Bot  # noqa
from dof_discord_bot.src.constants import COMMAND_PREFIX as _PREFIX, TOKEN as _DOF_BOT_TOKEN  # noqa
from dof_discord_bot.src.logger import Log as _Log  # noqa


# Declare some useful directories
_TEST_CHANNEL_NAME = "test-" + "".join(_random.choice(_string.ascii_lowercase) for _ in range(16))
TESTS_DIR = _os.path.join(_os.path.dirname(__file__), "..")
INTEGRATION_TESTS_DIR = _os.path.join(TESTS_DIR, "integration_tests")
LOG_DIR = _os.path.join(TESTS_DIR, "log")

# Initialise the bot instances
dof_bot = _Bot(_PREFIX)
testing_bot = _commands.Bot("")

# Find the testing bot token in the environment
_TESTING_BOT_TOKEN = _os.getenv("DOF_TESTING_TOKEN", "")
if not _TESTING_BOT_TOKEN:
    print(f"Missing token - please declare \"DOF_TESTING_TOKEN\" environment variable", file=_sys.stderr)


async def process_commands_by_bot(message):
    """
    This is an overridden version of discord's `process_commands` method, to allow handling commands invoked by the
    testing bot.
    """
    ctx = await dof_bot.get_context(message)
    await dof_bot.invoke(ctx)

# This override must be done to make sure that the actual bot listens to commands typed by the testing bot
dof_bot.process_commands = process_commands_by_bot


def setup():
    """
    Global setup function.
    """
    _Log.info("Setting up testing environment")
    _run_bots()
    _create_testing_channel()
    _Log.info("Environment set up")


def teardown():
    """
    Global teardown function.
    """
    _Log.info("Tearing down testing environment")
    _remove_testing_channel()
    _stop_bots()
    _Log.info("Environment torn down")


def call(future: _typing.Coroutine):
    """
    Helper function used to resolve future in a thread-safe manner.
    """
    _asyncio.run_coroutine_threadsafe(future, testing_bot.loop).result()


def get_test_channel() -> _discord.TextChannel:
    """
    Helper function to return the test channel
    """
    return testing_bot.get_channel(dof_bot.channels[_TEST_CHANNEL_NAME].id)


def _run_bots(timeout: int = 60, delay: int = 3):
    """
    Run both bots simultaneously and wait for them to connect.

    This function may timeout after `timeout` seconds if the bots don't start, and will monitor the state of the
    connections every `delay` seconds.
    """
    async def _connect(bot: _commands.Bot, token: str):
        """
        Helper function used to wrap the `start` and `close` commands as a single function.
        """
        try:
            await bot.start(token)
        finally:
            await bot.close()

    def _connect_bots(loop: _asyncio.AbstractEventLoop):
        """
        Helper function used to create tasks and run the bots in an async loop.
        """
        dof_bot_run_task = loop.create_task(_connect(dof_bot, _DOF_BOT_TOKEN))
        testing_bot_run_task = loop.create_task(_connect(testing_bot, _TESTING_BOT_TOKEN))
        loop.run_until_complete(_asyncio.gather(dof_bot_run_task, testing_bot_run_task))

    _Log.info("Waiting for bots to start")
    _threading.Thread(target=_connect_bots, args=(_asyncio.get_event_loop(),)).start()

    current_time = _time.time()
    while not dof_bot.is_ready() and not testing_bot.is_ready():
        if _time.time() - current_time > timeout:
            _Log.error("Timed out waiting for bots to start")
            return

        _Log.debug(f"Starting bots, dof-bot state - ready: {dof_bot.is_ready()}, closed: {dof_bot.is_closed()}")
        _Log.debug(f"Starting bots, testing-bot state - ready: {testing_bot.is_ready()}, closed: {testing_bot.is_closed()}")
        _time.sleep(delay)

    _Log.info("Both bots started and running")


def _stop_bots(timeout: int = 60, delay: int = 3):
    """
    Send the stop
    """
    _Log.info("Waiting for bots to close")

    # Await `close()` in a thread-safe manner
    _asyncio.run_coroutine_threadsafe(dof_bot.close(), dof_bot.loop).result()
    _asyncio.run_coroutine_threadsafe(testing_bot.close(), testing_bot.loop).result()

    current_time = _time.time()
    while not dof_bot.is_closed() and not testing_bot.is_closed():
        if _time.time() - current_time > timeout:
            _Log.error("Timed out waiting for bots to close")
            return

        _Log.debug(f"Stopping bots, dof-bot state - ready: {dof_bot.is_ready()}, closed: {dof_bot.is_closed()}")
        _Log.debug(f"Stopping bots, testing-bot state - ready: {testing_bot.is_ready()}, closed: {testing_bot.is_closed()}")
        _time.sleep(delay)

    _Log.info("Both bots closed")


def _create_testing_channel():
    """
    Function used to create a discord channel which will be used for integration testing
    """
    call(dof_bot.guild.create_text_channel(_TEST_CHANNEL_NAME, reason="Created for development (testing) purposes."))


def _remove_testing_channel():
    """
    Function used to remove the channel used for integration testing.
    """
    call(dof_bot.channels[_TEST_CHANNEL_NAME].delete())


