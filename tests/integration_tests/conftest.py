"""
Configuration module containing pytest-specific hooks.
"""
import os
import logging
from . import helpers
from _pytest.config import Config as PyTestConfig
from dof_discord_bot.src.logger import Log
from dof_discord_bot.src import logger


def _reconfigure_logging():
    """
    Helper function used to redirect all logging into the tests-specific log folder.

    Accesses the private method of `logger` to avoid repeating the code.
    """
    # Clear existing logs
    for file_name in os.listdir(helpers.LOG_DIR):
        if file_name.endswith(".log"):
            os.remove(os.path.join(helpers.LOG_DIR, file_name))

    # noinspection PyProtectedMember
    logger._configure(log_directory=helpers.LOG_DIR)
    Log._logger = logging.getLogger("dof-discord-bot")
    Log.info("Logging has been reconfigured")


def pytest_configure(config: PyTestConfig):
    """
    Configuration hook which reconfigures the logging and calls the global setup function.
    """
    _reconfigure_logging()
    helpers.setup()
    Log.info("Pytest configuration hook finished successfully")


def pytest_unconfigure(config: PyTestConfig):
    """
    Configuration hook which calls the global teardown function.
    """
    helpers.teardown()
    Log.info("Pytest unconfiguration hook finished successfully")

    # An explicit kill of current process to ensure clean exit in case of errors when stopping the code
    os.kill(os.getpid(), 9)
