# This module is a wrapper built for logging module of Python. This module 
# provides a setup_logger() function to easily setup a logger on use with other 
# modules of your project. By default, the logger will log to the console via 
# std.out. You can also specify a file to log to by setting the file parameter 
# to the path of the file.
# 
# Tested on Python 3.11.0 and requires termcolor for colored stream output
# support.
#  
# Default log record format is as follows:
# [<datetime>] [<level>] [<name>] [<filename>:<function>:<lineno>] - <message>
# 
# Example usage:
# >>> from logger import setup_logger
# >>> my_logger = setup_logger(name="my_logger", file="my_log.log")
# >>> my_logger.debug("Hello world!")

"""
This module provides a `setup_logger()` function to easily setup a logger to use
on your project. Supports colored stream output via `termcolor`.
"""

# TODO Support configurable colors for `setup_logger()`
# TODO Add a new logging.LogRecord attribute called `minifiedPath` that shows
# TODO ... the minified path to the current file being logged, i.e.:
# TODO ... `/home/user/my_file.py` becomes `/h/u/my_file.py`

import logging
from typing import TextIO
from sys import stdout
from pathlib import Path

from termcolor import colored  # tested on version 2.2.0


__author__ = "Azriell Bautista"
__email__ = "azri.ell@yahoo.com"
__version__ = "1.0.0"
    

# This dictionary maps the logging level to the color format used in ColoredFormatter
LOGGING_COLORS = {
    logging.NOTSET: dict(color="grey"),
    logging.DEBUG: dict(color="magenta", attrs=["bold"]),
    logging.INFO: dict(color="blue"),
    logging.WARNING: dict(color="yellow"),
    logging.ERROR: dict(color="red"),
    logging.CRITICAL: dict(color="white", on_color="on_red", attrs=["bold"]),
}


# A custom formatter that allows coloring of the log messages.
class ColoredFormatter(logging.Formatter):
    """A custom formatter that allows coloring of the log messages.

    The log messages will be colored based on the level of the message.

    Args:
        fmt (str, optional): Format of the logs.
        datefmt (str, optional): Date format of the logs.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Formats the log record.

        Args:
            record (logging.LogRecord): Log record to be formatted.

        Returns:
            str: Formatted log record.
        """
        
        # Set the color of the log message based on the level of the message
        formatter = logging.Formatter(
            colored(self._fmt, **LOGGING_COLORS.get(record.levelno, {})), 
            self.datefmt
        )

        return formatter.format(record)
    

# The setup_logger() function sets up a basic logger with general use configurations
def setup_logger(
    name: str | None = None,
    *,
    level: int = logging.DEBUG,
    stream: TextIO | None = stdout,
    colored_stream: bool = True,
    file: str | Path | None = None,
    fmt: str = "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] "
               "[%(filename)s:%(funcName)s:%(lineno)s] - %(message)s",
    datefmt: str = "%Y-%m-%d %H:%M:%S",
    propagate: bool = True,
    parent: logging.Logger | None = None,
    disabled: bool = False,
) -> logging.Logger:
    """Creates a logger with the given name.

    The logger will log to the given stream (sys.stdout) by default and to a 
    file, if given. The log level will be set to logging.DEBUG be default.
    Silently disable the logger by setting disabled=True.

    Args:
        name (str, optional): Name of the logger. If None is provided, root is 
            used. Defaults to None.
        level (int, optional): Level of the logs. Defaults to logging.DEBUG.
        stream (TextIO | None, optional): Stream the logs will be written to. 
            Defaults to sys.stdout.
        colored_stream (bool, optional): Whether the logs on stream will be
            colored. Defaults to True. If False, the logs will not be colored.
        file (str | Path | None, optional): Name of the file the logs will be 
            written to. If None is provided, no file will be written to. 
            Defaults to None.
        fmt (str, optional): Format of the logs.
        datefmt (str, optional): Date format of the logs.
        propagate (bool, optional): Propagate the logs to the parent logger.
            Defaults to True.
        parent (logging.Logger, optional): Parent logger. Defaults to None.
        disabled (bool, optional): Silently disables the logger by adding a 
            logging.NullHandler() handler to the logger if True. Defaults to 
            False.

    Returns:
        logging.Logger: The logger.
        
    Raises:
        ValueError: If the stream is not a file-like object.
    """

    logger = logging.getLogger(name)

    # Silently disable the logger if disabled=True and return the logger
    # immediately. Add a NullHandler() handler to the logger.
    if disabled:
        logger.addHandler(logging.NullHandler())
        return logger

    logger.setLevel(level)
    logger.propagate = propagate
    logger.parent = parent

    # Setup the stream formatter to use colored stream if colored_stream=True.
    # Otherwise, use the default formatter.
    stream_formatter = ColoredFormatter(fmt, datefmt) \
                       if colored_stream \
                       else logging.Formatter(fmt, datefmt)

    if stream is not None:
        # Validate if stream is a file-like object by checking if it has a write 
        # method. If not, raise a TypeError.
        if not(hasattr(stream, "write") and callable(getattr(stream, "write"))):
            raise TypeError("stream must be a file-like object")
              
        # Set the stream handler to use the stream formatter.
        stream_handler = logging.StreamHandler(stream)
        # Set the appropriate formatter for the stream handler and then add the 
        # handler to the logger. 
        stream_handler.setFormatter(stream_formatter)
        logger.addHandler(stream_handler)

    if file is not None:
        # If file is not a string or a Path object, raise a TypeError. 
        if not isinstance(file, (str, Path)):
            raise TypeError("file must be a string or a Path object")
        
        # If file is a string, convert it to a Path object.
        if isinstance(file, str):
            file = Path(file)

        # If file is empty or is a directory, raise a ValueError.
        if not file or file.is_dir():
            raise ValueError("file cannot be an empty path or a directory")
            
        # Create file handler and set the formatter.
        file_handler = logging.FileHandler(file, mode="a+")
        file_handler.setFormatter(logging.Formatter(fmt, datefmt))
        logger.addHandler(file_handler)

    return logger


if __name__ == "__main__":
    # Print the docstring of the setup_logger function.
    print(setup_logger.__doc__)
       
    # Setup a logger that writes to the stream and file, with colored stream
    # enabled (default is True).
    logger = setup_logger(__name__, file=".log")
    
    # Test the logger for different logging levels, note the colors on console.
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")