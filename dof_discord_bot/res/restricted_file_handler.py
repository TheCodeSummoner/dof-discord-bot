"""
Helper module storing the class to be used within the logging config files.
"""
import logging


class RestrictedFileHandler(logging.FileHandler):
    """
    Extends a classic file handler by restricting the logging messages to contain only the specified level.

    .. note::
        Due to circular imports, it is impossible to place this class in the `logger` module.
    """

    def __init__(self, filename, *args, **kwargs):
        logging.FileHandler.__init__(self, filename, *args, **kwargs)

    def emit(self, record):
        """
        Overridden function modified to only log records of a matching level.
        """
        return logging.FileHandler.emit(self, record) if record.levelno == self.level else None
