"""
Helper file containing setup/teardown relevant functions, as well as some common testing constructs.
"""
# pylint: disable=import-error, wrong-import-position
import os
import sys
import time
import asyncio
import inspect
import threading
import random
import string
import typing
import discord
import pytest
from discord.ext import commands

# Make sure dof_discord_bot package can be found and overrides any installed versions
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from dof_discord_bot.src.bot import Bot  # noqa
from dof_discord_bot.src.constants import COMMAND_PREFIX, TOKEN, RES_DIR  # noqa
from dof_discord_bot.src.utils import Log  # noqa

# Declare some useful directories
TESTS_DIR = os.path.join(os.path.dirname(__file__), "..")
INTEGRATION_TESTS_DIR = os.path.join(TESTS_DIR, "integration_tests")
LOG_DIR = os.path.join(TESTS_DIR, "log")

# Find the testing bot token in the environment
_TESTING_BOT_TOKEN = os.getenv("DOF_TESTING_TOKEN", "")
if not _TESTING_BOT_TOKEN:
    if os.path.exists(os.path.join(RES_DIR, "token-testing")):
        with open(os.path.join(RES_DIR, "token-testing")) as f:
            _TESTING_BOT_TOKEN = f.read().strip()
    else:
        pytest.exit(f"Missing token - either declare \"DOF_TESTING_TOKEN\" environment variable or include the token "
                    f"in the \"token-testing\" file at \"{os.path.join(RES_DIR, 'token-testing')}\"")

# Generate the testing channel name
_TEST_CHANNEL_NAME = "test-" + "".join(random.choice(string.ascii_lowercase) for _ in range(16))

# Initialise the bot instances
dof_bot = Bot(COMMAND_PREFIX)
testing_bot = commands.Bot("")


async def process_commands_by_bot(message):
    """
    Overridden version of discord's `process_commands` method, to allow handling commands invoked by the testing bot.
    """
    ctx = await dof_bot.get_context(message)
    await dof_bot.invoke(ctx)

# This override must be done to make sure that the actual bot listens to commands typed by the testing bot
dof_bot.process_commands = process_commands_by_bot


def threaded_async(func: typing.Callable):
    """
    Resolve future in a thread-safe manner.
    """
    future: typing.Coroutine = func()

    def _call():
        """
        Inner function used to resolve the future correctly.
        """
        return asyncio.run_coroutine_threadsafe(future, testing_bot.loop).result()

    return _call


async def wait_for(func: typing.Callable, on_timeout: typing.Callable, timeout: int = 10, delay: int = 1):
    """
    Wait for a function to complete or timeout if it takes too long.

    `func` is the function which will be called every loop cycle (waiting time between the cycles is defined by the
    `delay` argument), unless it takes more than `timeout` seconds, in which case the `on_timeout` function will be
    called and the loop will end.

    To terminate the loop early (and avoid timeout), return a value within `func`. If evaluation of this value is True,
    then that value will be returned. Similarly, result of `on_timeout` will be returned after `timeout` seconds.

    Note that the code can handle both synchronous and asynchronous `func` and `on_timeout` functions.
    """
    current_time = time.time()
    while True:
        if time.time() - current_time > timeout:
            if inspect.iscoroutinefunction(on_timeout):
                return await on_timeout()

            return on_timeout()

        if inspect.iscoroutinefunction(func):
            result = await func()
            if result:
                return result
        else:
            result = func()
            if result:
                return result
        await asyncio.sleep(delay)


def setup():
    """
    Global setup function.
    """
    Log.info("Setting up testing environment")
    _run_bots()
    if not _create_testing_channel():
        _stop_bots()
        pytest.exit("Failed to create the test channel")
    Log.info("Environment set up")


def teardown():
    """
    Global teardown function.
    """
    Log.info("Tearing down testing environment")
    _remove_testing_channel()
    _stop_bots()
    Log.info("Environment torn down")


def get_test_channel() -> discord.TextChannel:
    """
    Return the test channel.
    """
    return testing_bot.get_channel(dof_bot.channels[_TEST_CHANNEL_NAME].id)


def _run_bots(timeout: int = 15, delay: int = 3):
    """
    Run both bots simultaneously and wait for them to connect.

    This function may timeout after `timeout` seconds if the bots don't start, and will monitor the state of the
    connections every `delay` seconds.
    """
    async def _connect(bot: commands.Bot, token: str):
        """
        Wrap the `start` and `close` commands as a single function.
        """
        try:
            await bot.start(token)
        finally:
            await bot.close()

    def _connect_bots(loop: asyncio.AbstractEventLoop):
        """
        Create tasks and run the bots in an async loop.
        """
        dof_bot_run_task = loop.create_task(_connect(dof_bot, TOKEN))
        testing_bot_run_task = loop.create_task(_connect(testing_bot, _TESTING_BOT_TOKEN))
        loop.run_until_complete(asyncio.gather(dof_bot_run_task, testing_bot_run_task))

    Log.info("Waiting for bots to start")
    threading.Thread(target=_connect_bots, args=(asyncio.get_event_loop(),)).start()

    current_time = time.time()
    while not dof_bot.is_ready() and not testing_bot.is_ready():
        if time.time() - current_time > timeout:
            pytest.exit("Timed out waiting for bots to start")

        Log.debug(f"Starting bots, dof-bot state - ready: {dof_bot.is_ready()}, closed: {dof_bot.is_closed()}")
        Log.debug(f"Starting bots, testing-bot state - "
                   f"ready: {testing_bot.is_ready()}, closed: {testing_bot.is_closed()}")
        time.sleep(delay)

    Log.info("Both bots started and running")


def _stop_bots(timeout: int = 15, delay: int = 3):
    """
    Stop both bots.

    This function may timeout after `timeout` seconds if the bots don't stop, and will monitor the state of the
    connections every `delay` seconds.
    """
    Log.info("Waiting for bots to close")

    # Await `close()` in a thread-safe manner
    asyncio.run_coroutine_threadsafe(dof_bot.close(), dof_bot.loop).result()
    asyncio.run_coroutine_threadsafe(testing_bot.close(), testing_bot.loop).result()

    current_time = time.time()
    while dof_bot.is_ready() or testing_bot.is_ready():
        if time.time() - current_time > timeout:
            Log.error("Timed out waiting for bots to stop, manual cleanup may be needed")
            break

        Log.debug(f"Stopping bots, dof-bot state - ready: {dof_bot.is_ready()}, closed: {dof_bot.is_closed()}")
        Log.debug(f"Stopping bots, testing-bot state - "
                   f"ready: {testing_bot.is_ready()}, closed: {testing_bot.is_closed()}")
        time.sleep(delay)

    Log.info("Both bots stopped")


@threaded_async
async def _create_testing_channel():
    """
    Create a discord channel which will be used for integration testing.
    """
    def channel_to_get_detected():
        """
        Bot must detect the channel creation.
        """
        return _TEST_CHANNEL_NAME in dof_bot.channels

    def or_fail_and_exit():
        """
        Can't continue - testing without a dedicated test channel is impossible.
        """
        Log.error("Timed out creating the test channel")

    Log.info("Creating the test channel")
    await dof_bot.guild.create_text_channel(_TEST_CHANNEL_NAME, reason="Created for development (testing) purposes.")
    return await wait_for(channel_to_get_detected, or_fail_and_exit)


@threaded_async
async def _remove_testing_channel():
    """
    Remove the channel used for integration testing.
    """
    Log.info("Removing the test channel")
    await dof_bot.channels[_TEST_CHANNEL_NAME].delete()
