"""
Helper file containing setup/teardown relevant functions, also used to expose some common testing constructs.
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
import pytest as _pytest
import inspect as _inspect
from discord.ext import commands as _commands

# Make sure dof_discord_bot package can be found
_sys.path.append(_os.path.join(_os.path.dirname(__file__), "..", ".."))
from dof_discord_bot.src.bot import Bot as _Bot  # noqa
from dof_discord_bot.src.constants import COMMAND_PREFIX as _PREFIX, TOKEN as _DOF_BOT_TOKEN  # noqa
from dof_discord_bot.src.logger import Log as _Log  # noqa

# Find the testing bot token in the environment
_TESTING_BOT_TOKEN = _os.getenv("DOF_TESTING_TOKEN", "")
if not _TESTING_BOT_TOKEN:
    _pytest.exit(f"Missing token - please declare \"DOF_TESTING_TOKEN\" environment variable")

# Declare some useful directories
TESTS_DIR = _os.path.join(_os.path.dirname(__file__), "..")
INTEGRATION_TESTS_DIR = _os.path.join(TESTS_DIR, "integration_tests")
LOG_DIR = _os.path.join(TESTS_DIR, "log")

# Generate the testing channel name
_TEST_CHANNEL_NAME = "test-" + "".join(_random.choice(_string.ascii_lowercase) for _ in range(16))

# Initialise the bot instances
dof_bot = _Bot(_PREFIX)
testing_bot = _commands.Bot("")


async def process_commands_by_bot(message):
    """
    This is an overridden version of discord's `process_commands` method, to allow handling commands invoked by the
    testing bot.
    """
    ctx = await dof_bot.get_context(message)
    await dof_bot.invoke(ctx)

# This override must be done to make sure that the actual bot listens to commands typed by the testing bot
dof_bot.process_commands = process_commands_by_bot


def threaded_async(func: _typing.Callable):
    """
    Helper decorator used to resolve future in a thread-safe manner.
    """
    future: _typing.Coroutine = func()

    def _call():
        """
        Inner function used to resolve the future correctly.
        """
        return _asyncio.run_coroutine_threadsafe(future, testing_bot.loop).result()

    return _call


async def wait_for(func: _typing.Callable, on_timeout: _typing.Callable, timeout: int = 10, delay: int = 1):
    """
    Helper function used to wait for a function to complete or timeout if it takes to long.

    `func` is the function which will be called every loop cycle (waiting time between the cycles is defined by the
    `delay` argument), unless it takes more than `timeout` seconds, in which case the `on_timeout` function will be
    called and the loop will end.

    To terminate the loop early (and avoid timeout), return a value within `func`. If evaluation of this value is True,
    then that value will be returned. Similarly, result of `on_timeout` will be returned after `timeout` seconds.

    Note that the code can handle both synchronous and asynchronous `func` and `on_timeout` functions.
    """
    current_time = _time.time()
    while True:
        if _time.time() - current_time > timeout:
            if _inspect.iscoroutinefunction(on_timeout):
                return await on_timeout()
            else:
                return on_timeout()
        else:
            if _inspect.iscoroutinefunction(func):
                result = await func()
                if result:
                    return result
            else:
                result = func()
                if result:
                    return result
            await _asyncio.sleep(delay)


def setup():
    """
    Global setup function.
    """
    _Log.info("Setting up testing environment")
    _run_bots()
    if not _create_testing_channel():
        _stop_bots()
        _pytest.exit("Failed to create the test channel")
    _Log.info("Environment set up")


def teardown():
    """
    Global teardown function.
    """
    _Log.info("Tearing down testing environment")
    _remove_testing_channel()
    _stop_bots()
    _Log.info("Environment torn down")


def get_test_channel() -> _discord.TextChannel:
    """
    Helper function to return the test channel
    """
    return testing_bot.get_channel(dof_bot.channels[_TEST_CHANNEL_NAME].id)


def _run_bots(timeout: int = 15, delay: int = 3):
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
            _pytest.exit("Timed out waiting for bots to start")

        _Log.debug(f"Starting bots, dof-bot state - ready: {dof_bot.is_ready()}, closed: {dof_bot.is_closed()}")
        _Log.debug(f"Starting bots, testing-bot state - ready: {testing_bot.is_ready()}, closed: {testing_bot.is_closed()}")
        _time.sleep(delay)

    _Log.info("Both bots started and running")


def _stop_bots(timeout: int = 3, delay: int = 3):
    """
    Stop both bots

    This function may timeout after `timeout` seconds if the bots don't stop, and will monitor the state of the
    connections every `delay` seconds.
    """
    _Log.info("Waiting for bots to close")

    # Await `close()` in a thread-safe manner
    _asyncio.run_coroutine_threadsafe(dof_bot.close(), dof_bot.loop).result()
    _asyncio.run_coroutine_threadsafe(testing_bot.close(), testing_bot.loop).result()

    current_time = _time.time()
    while not dof_bot.is_closed() and not testing_bot.is_closed():
        if _time.time() - current_time > timeout:
            _Log.error("Timed out waiting for bots to close, manual cleanup may be needed")
            break

        _Log.debug(f"Stopping bots, dof-bot state - ready: {dof_bot.is_ready()}, closed: {dof_bot.is_closed()}")
        _Log.debug(f"Stopping bots, testing-bot state - ready: {testing_bot.is_ready()}, closed: {testing_bot.is_closed()}")
        _time.sleep(delay)

    _Log.info("Both bots closed")


@threaded_async
async def _create_testing_channel():
    """
    Function used to create a discord channel which will be used for integration testing
    """
    def channel_to_get_detected():
        """
        DoF bot must detect the channel creation.
        """
        return _TEST_CHANNEL_NAME in dof_bot.channels

    def or_fail_and_exit():
        """
        Can not continue testing at this point.
        """
        _Log.error("Timed out creating the test channel")

    _Log.info("Creating the test channel")
    await dof_bot.guild.create_text_channel(_TEST_CHANNEL_NAME, reason="Created for development (testing) purposes.")
    return await wait_for(channel_to_get_detected, or_fail_and_exit)


@threaded_async
async def _remove_testing_channel():
    """
    Function used to remove the channel used for integration testing.
    """
    _Log.info("Removing the test channel")
    await dof_bot.channels[_TEST_CHANNEL_NAME].delete()
