"""
Helper module storing the class to be used within the logging config files.

Additionally, amends the following logging record fields to give more relevant information:

    - `filename' - file from where the message was logged
    - `function' - function within which the message was logged
    - `lineno' - line number of the log statement
"""
import logging
import inspect
import os

ROOT_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))


def get_frame():
    """
    Return the frame (see the `inspect' module for details) that called the logging function.
    """
    stack = inspect.stack()[::-1]

    # Traverse backwards through the stack to find the first frame that has the filename "logger.py". The frame
    # following that is the calling frame.
    while stack:
        frame = stack.pop()
        if os.path.basename(frame.filename) == "logger.py":

            # If logged within logger.py or failed to find it, return the last caller frame.
            try:
                return stack.pop()[0]
            except IndexError:
                return frame


class VerboseFileHandler(logging.FileHandler):
    """
    Helper handler class used for logging configuration.

    Any emit to a RestrictedFileHandler is also passed to this, so it is all the levels combined.
    """

    def __init__(self, filename, *args, **kwargs):
        logging.FileHandler.__init__(self, filename, *args, **kwargs)

    def emit(self, record):
        """
        Overridden function modified so any logging call is put into the verbose file.
        """
        caller = inspect.getframeinfo(get_frame())
        record.filename = os.path.relpath(caller.filename, ROOT_DIR)
        record.function = caller.function
        record.lineno = caller.lineno

        return logging.FileHandler.emit(self, record)
