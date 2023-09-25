# This module is a wrapper built for logging module of Python. This module
# provides a setup_logger() function to easily setup a logger on use with other
# modules of your project. By default, the logger will log to the console via
# std.out. You can also specify a file to log to by setting the file parameter
# to the path of the file.
#
# Tested on Python 3.11.0 and optionally requires termcolor (tested on 2.2.0) 
# for colored stream output support.
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

import logging
from typing import TextIO, Callable
from sys import stdout
from pathlib import Path


# Make termcolor an optional dependency.
# Try to import colored from termcolor, else set colored to None.
# The setup_logger() function will check if colored is available and will raise
# ModuleNotFoundError if it is not available.
try:
    from termcolor import colored
except ModuleNotFoundError:
    colored = None
    
    
__author__ = "Azriell Bautista"
__email__ = "azri.ell@yahoo.com"
__version__ = "1.1.0"
    

# _FMT and _DATEFMT are the default format and date format of the logger used
# in this module.
_FMT = "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] " \
       "[%(shortPathname)s:%(funcName)s:%(lineno)s] - %(message)s"
_DATEFMT = "%Y-%m-%d %H:%M:%S"

# The log messages will be colored based on the level of the message.
# To change colors of a log message, you can do the following:
#
# >>> import logging
# >>> from logger import _LOGGING_COLORS
# >>> _LOGGING_COLORS.update({ logging.DEBUG: dict(color="green") })
# >>> from logger import setup_logger
# >>> my_logger = setup_logger(name="my_logger", colored_stream=True)
# >>> my_logger.debug("I am now a green debug log.")
_LOGGING_COLORS = {
    logging.NOTSET: dict(color="grey"),
    logging.DEBUG: dict(color="magenta", attrs=["bold"]),
    logging.INFO: dict(color="blue"),
    logging.WARNING: dict(color="yellow"),
    logging.ERROR: dict(color="red"),
    logging.CRITICAL: dict(color="white", on_color="on_red", attrs=["bold"]),
}

# Sets the maximum number of preceding directories to be shown for the 
# %(shortPathname)s log record attribute.
_MAX_FOLDERS = 2


# A custom formatter for logging messages.
class CustomFormatter(logging.Formatter):
    """A custom formatter for logging messages.

    Additinal log record attributes:
        %(minifiedPath)s - Minifies the pathname attribute of the LogRecord of 
            the current file being logged, i.e.: the path a long path like 
            /home/user/project/src/my_module.py becomes /h/u/p/s/my_module.py
            
        %(shortFilename)s - Shortens the filename attribute of the LogRecord to
            less than 20 characters including the extension, i.e.: a file named
            very_long_module_filename.py becomes ver~dule_filename.py
            
        %(shortPathname)s - Shortens the pathname attribute of the LogRecord by
            ommitting first few folders of the path and show only the nearest
            folder name, i.e.: /home/user/project/src/my_module.py becomes
            (...)project/src/my_module.py
            
    Args:
        fmt (str, optional): Format of the logs.
        datefmt (str, optional): Date format of the logs.
    """
    def __init__(self, fmt: str = _FMT, datefmt: str = _DATEFMT, colored_stream: bool = False) -> None:
        super().__init__(fmt, datefmt)
        
        self.colored_stream = colored_stream
        # Insert check for termcolor here to be reusable by others.
        if self.colored_stream:
            # Check if termcolor is available.
            _raise_exception_if_no_termcolor(colored)
        
    def format(self, record: logging.LogRecord) -> str:
        """Formats the given record. Add additional records here.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: The formatted record.
        """
        # Create minifiedPath record attribute.
        path_parts = Path(record.pathname).resolve().parts
        sep: str = __import__("os").path.sep
        minified_path = sep.join([part[0] for part in path_parts[:-1]] + [path_parts[-1]])
        setattr(record, "minifiedPath", minified_path)
            
        # Create shortFilename record attribute.
        short_filename = f"{fname[:3]}~{fname[-16:]}" \
                            if len(fname := record.filename) > 20 \
                            else fname
        setattr(record, "shortFilename", short_filename)
        
        # Create shortPath record attribute.        
        short_pathname = "(...)" + sep.join(path_parts[-_MAX_FOLDERS - 1:]) \
                         if len(path_parts) > _MAX_FOLDERS \
                         else record.pathname
        setattr(record, "shortPathname", short_pathname)
            
        # If termcolor is available, add color to the custom formatter.
        if self.colored_stream:
            formatter = logging.Formatter(
                colored(self._fmt, **_LOGGING_COLORS.get(record.levelno, {})),
                self.datefmt
            )
                
            return formatter.format(record)
        
        return super().format(record)


# The setup_logger() function sets up a basic logger with general use configurations
def setup_logger(
    name: str | None = None,
    *,
    level: int = logging.DEBUG,
    stream: TextIO | None = stdout,
    colored_stream: bool = False,
    file: str | Path | None = None,
    fmt: str = _FMT,
    datefmt: str = _DATEFMT,
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
            colored. Defaults to False. If True, the logs will be colored.
            Requires termcolor module to be installed.
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
        ModuleNotFoundError: If the termcolor module is not installed and 
            colored_stream=True.
        TypeError: If the file is not a string or a Path object.
        ValueError: If the stream is not a file-like object.
        ValueError: If the file is empty or is a directory.
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

    # Check if `termcolor` module is installed. If not, raise a ModuleNotFoundError.
    if colored_stream:
        _raise_exception_if_no_termcolor(colored)

    # Setup the stream formatter to use colored stream if colored_stream=True.
    # Otherwise, use the default formatter.
    stream_formatter = CustomFormatter(fmt, datefmt, colored_stream)

    if stream is not None:
        # Validate if stream is a file-like object by checking if it has a write
        # method. If not, raise a TypeError.
        # Alternative is to check stream is an instance of io.TextIOWrapper.
        if not (hasattr(stream, "write") and callable(getattr(stream, "write"))):
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


def _raise_exception_if_no_termcolor(colored: Callable | None) -> None:
    """Raises a ModuleNotFoundError if termcolor is not installed.

    Args:
        colored (Callable | None): The termcolor.colored() function.
    """
    
    # Check if termcolor is installed. If not, raise a ModuleNotFoundError.
    if colored is None:
        raise ModuleNotFoundError(
            "colored_stream=True requires the `termcolor` module to be installed"
        )
    if not callable(colored):
        raise TypeError("colored must be a callable")

if __name__ == "__main__":
    # Print the docstring of the setup_logger function
    print(setup_logger.__doc__)

    # Setup a logger that writes to the stream and file
    logger = setup_logger(__name__, file=".log")

    # Test the logger for different logging levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Setup a logger that writes to the stream only, with colored_stream=True
    # If `termcolor` is not installed, the following should raise a ModuleNotFoundError
    colored_logger = setup_logger("colored_logger", colored_stream=True)
    
    # Test the colored_logger for different logging levels
    # Note the colors on console
    colored_logger.debug("This is a colored debug message.")
    colored_logger.info("This is a colored info message.")
    colored_logger.warning("This is a colored warning message.")
    colored_logger.error("This is a colored error message.")
    colored_logger.critical("This is a colored critical message.")
    