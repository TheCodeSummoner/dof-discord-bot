"""
Configuration module containing pytest-specific hooks.
"""
# pylint: disable=import-error
import os
from _pytest.config import Config as PyTestConfig
from dof_discord_bot.src.utils import Log, configure_logging
from . import helpers


def _reconfigure_logging():
    """
    Redirect all logging into the tests-specific log folder.

    Accesses the private method of `logger` to avoid repeating the code.
    """
    # Clear existing logs
    for file_name in os.listdir(helpers.LOG_DIR):
        if file_name.endswith(".log"):
            os.remove(os.path.join(helpers.LOG_DIR, file_name))

    configure_logging(target_log_directory=helpers.LOG_DIR)
    Log.info("Logging has been reconfigured")


def pytest_configure(config: PyTestConfig):
    """
    Reconfigures the logging module and call the global setup function.
    """
    # pylint: disable=unused-argument
    _reconfigure_logging()
    helpers.setup()
    Log.info("Pytest configuration hook finished successfully")


def pytest_unconfigure(config: PyTestConfig):
    """
    Call the global teardown function.
    """
    # pylint: disable=unused-argument, protected-access
    helpers.teardown()
    Log.info("Pytest unconfiguration hook finished successfully")

    # An explicit "kill" of current process to ensure clean exit in case of errors when stopping the code
    os._exit(0)
