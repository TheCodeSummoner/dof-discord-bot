"""
Logger
======

Module storing an implementation of a static log class and all values associated with it.

The config.json file stored within the log folder is used to configure most of the logging functionality.
"""
from .constants import LOG_DIR as _LOG_DIR
import logging as _logging
import logging.config as _config
import json as _json
import os as _os

_CONFIG_FILE_PATH = _os.path.join(_LOG_DIR, "config.json")
_FILE_HANDLERS = {"logging.FileHandler", "log.restricted_file_handler._RestrictedFileHandler",
                  "log.verbose_file_handler._VerboseFileHandler"}


class LogError(Exception):
    """
    A standard exception to handle log-related errors.
    """
    pass


def _configure(config_file_path: str = _CONFIG_FILE_PATH, log_directory: str = _LOG_DIR):
    """
    Helper function to configure the built-in logging module and retrieve a logger object.
    Uses a JSON configuration file.

    Providing `config_file_path` will result in reconfiguring the built-in logging functionalities, rather than
    specific logger's config - use with caution!
    """
    if not _os.path.exists(config_file_path):
        raise LogError(f"Failed to find the log config file at {config_file_path}")
    if not _os.path.exists(log_directory):
        raise LogError(f"The log directory does not exist - {log_directory}")

    try:
        with open(config_file_path, "r") as f:
            config = _json.load(f)

            # Extract the handlers and update the paths within them to use the correct folder
            for handler in (handlers := config["handlers"]):
                if handlers[handler]["class"] in _FILE_HANDLERS:
                    handlers[handler]["filename"] = _os.path.join(log_directory, handlers[handler]["filename"])

    except OSError as e:
        raise LogError(f"An error occurred while setting up the logging module - {e}")

    # Finally, load the configuration
    _logging.config.dictConfig(config)


class Log:
    """
    Static logging class which uses a Python's built-in logger object for the actual logging tasks.

    Uses the :class:`LogError` class to handle errors and let the calling function handle them.

    Functions
    ---------

    The following list shortly summarises each function:
        * reconfigure - a method to change the files' location
        * debug - a method to log a debug message
        * info - a method to log an info message
        * warning - a method to log a warning message
        * error - a method to log an error message

    Usage
    -----

    The class is static and should be used as follows::

        Log.debug("Debug message")
        Log.info("Info message")
        ...
    """
    _configure()
    _logger = _logging.getLogger("dof-discord-bot")

    @classmethod
    def debug(cls, message: str, *args, **kwargs):
        """
        Standard debug logging.
        """
        cls._logger.debug(message, *args, **kwargs)

    @classmethod
    def info(cls, message: str, *args, **kwargs):
        """
        Standard info logging.
        """
        cls._logger.info(message, *args, **kwargs)

    @classmethod
    def warning(cls, message: str, *args, **kwargs):
        """
        Standard warning logging.
        """
        cls._logger.warning(message, *args, **kwargs)

    @classmethod
    def error(cls, message: str, *args, **kwargs):
        """
        Standard error logging.
        """
        cls._logger.error(message, *args, **kwargs)
