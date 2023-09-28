# This module is a wrapper built for logging module of Python. This module
# provides a setup_logger() function to easily setup a logger on use with other
# modules of your project. By default, the logger will log to the console via
# std.out. You can also specify a file to log to by setting the file parameter
# to the path of the file.
#
# Also provides a timing decorator log_func_time() to log function execution time.
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
from functools import partial, wraps
from inspect import currentframe
from pathlib import Path
from sys import  exc_info, stdout
from time import perf_counter
from traceback import format_stack
from typing import Any, Callable, TextIO

# Make termcolor an optional dependency.
# Try to import colored from termcolor, else set colored to None.
# The _check_termcolor()  will check if termcolor.colored is available and will
# raise exception if it is not properly installed.
try:
    from termcolor import colored
except ModuleNotFoundError:
    pass  # Do nothing.
    
    
__author__ = "Azriell Bautista"
__email__ = "azri.ell@yahoo.com"
__version__ = "1.3.0"
    

# _FMT and _DATEFMT are the default format and date format of the logger used
# in this module.
_FMT = "[%(asctime)s.%(msecs)03d] [%(levelname)s] [%(name)s] " \
       "[%(filename)s:%(funcName)s:%(lineno)s] - %(message)s"
_DATEFMT = "%d%b%Y %H:%M:%S"

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
    logging.DEBUG: dict(color="magenta"),
    logging.INFO: dict(color="blue"),
    logging.WARNING: dict(color="yellow"),
    logging.ERROR: dict(color="red"),
    logging.CRITICAL: dict(color="white", on_color="on_red", attrs=["bold"]),
}

# Sets the maximum number of preceding directories to be shown for the 
# %(shortPathname)s log record attribute.
_MAX_FOLDERS = 2

# String used to replace the ommited paths
# Suggestions: "(...)", "...", "~"
_OMITTED_PATH_STR = "(...)"


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
            omitting first few folders of the path and show only the nearest
            folder names, i.e.: /home/user/project/src/my_module.py becomes
            (...)project/src/my_module.py
            
    Args:
        fmt (str, optional): Format of the logs.
        datefmt (str, optional): Date format of the logs.
    """
    def __init__(
        self, 
        fmt: str = _FMT, 
        datefmt: str = _DATEFMT, 
        colored_stream: bool = False,
    ) -> None:
        super().__init__(fmt, datefmt)
        
        self.colored_stream = colored_stream
        # Insert check for termcolor here to be reusable by others.
        if self.colored_stream:
            # Check if termcolor is available.
            _check_termcolor()
        
    def format(
        self, 
        record: logging.LogRecord,
    ) -> str:
        """Formats the given record. Add additional records here.

        Args:
            record (logging.LogRecord): The record to format.

        Returns:
            str: The formatted record.
        """
        # Create minifiedPath record attribute.
        path_parts = Path(record.pathname).resolve().parts
        # Path separator for Windows is '\', for POSIX is '/'.
        sep: str = __import__("os").path.sep 
        minified_path = sep.join([
            part[0] for part in path_parts[:-1]] + [path_parts[-1]
        ])
        setattr(record, "minifiedPath", minified_path)
            
        # Create shortFilename record attribute.
        short_filename = f"{fname[:3]}~{fname[-16:]}" \
                         if len(fname := record.filename) > 20 \
                         else fname
        setattr(record, "shortFilename", short_filename)
        
        # Create shortPath record attribute.        
        short_pathname = (_OMITTED_PATH_STR 
                          + sep.join(path_parts[-_MAX_FOLDERS - 1:]) \
                            if len(path_parts) > _MAX_FOLDERS \
                            else record.pathname)
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
        _check_termcolor()

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


# Logs the execution time of the given function.
def log_func_time(
    func: Callable| None = None,
    /, *, 
    logger: logging.Logger,
    show_args_kwargs: bool = False,
    show_result: bool = False,
    show_exception_traceback: bool = True,
    show_stack_info: bool = True,
) -> Callable | None:
    """Logs the execution time of the given function.

    Args:
        func (Callable| None): The function to be logged. If None is provided,
            this decorator will return a partial function that takes the function
            to be logged as the first argument.
        logger (logging.Logger): The logger to log the execution time.
        show_args_kwargs (bool, optional): Whether to log the function arguments
            and keyword arguments. Defaults to False.
        show_result (bool, optional): Whether to log the function result.
            Defaults to False. If True, the result will be logged.
        show_exception_traceback (bool, optional): Whether to log the exception
            traceback. Defaults to True.
        show_stack_info (bool, optional): Whether to log the stack info.
            Defaults to True.

    Returns:
        Callable | None: The function to be logged. If None is provided, this
            decorator will return a partial function that takes the function to
            be logged as the first argument.

    Raises:
        TypeError: If the logger is not a `logging.Logger`.
    """
    
    # Make sure that the logger is a `logging.Logger` object.
    if not isinstance(logger, logging.Logger):
        raise TypeError("Expected logger to be `logging.Logger` not "
                        f"`{type(logger).__name__}`.")
    
    # If func is None, return a partial function.
    if func is None:
        return partial(log_func_time, 
                       logger=logger, 
                       show_args_kwargs=show_args_kwargs,
                       show_result=show_result,
                       show_exception_traceback=show_exception_traceback,
                       show_stack_info=show_stack_info,)
            
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        """Wrapper function that logs the execution time of the given function.

        Args:
            *args: Positional arguments of the function to be logged.
            **kwargs: Keyword arguments of the function to be logged.

        Returns:
            Any: The result of the function to be logged.
        """

        # Initialize result with None
        # This is used to return the result of the function to be logged.
        result = None

        # Get the current frame and get the filename and line number of the caller.
        if frame := currentframe().f_back:
            pathname = frame.f_code.co_filename
            lineno = frame.f_lineno
        # Else set to unknown
        else:
            pathname = "<unknown>"
            lineno = -1

        # Create a logging.LogRecord object.
        # This is used to create the log message in contrast to calling logger.log()
        # since several record attributes will not reflect the correct values such
        # as the pathname, lineno, and func. 
        record = logging.LogRecord(name=logger.name, 
                                   level=logging.DEBUG,
                                   pathname=pathname,
                                   lineno=lineno,
                                   msg="",
                                   args=(),
                                   exc_info=None,
                                   func=func.__name__,
                                   sinfo=None,)
        
        # Show or hide the positional and keyword arguments on the logs.
        record.msg = f"Calling {func.__name__}()" 
        # Append args and kwargs values on the message if show_args_kwargs=True
        if show_args_kwargs: 
            record.msg += f" with {args=} and {kwargs=}"
        
        # Display the message above.
        logger.handle(record)

        # Start the timer
        start = perf_counter()
        
        # Call the function and get the result.
        try:
            result = func(*args, **kwargs)
            
        # If the function raises an exception, log the exception and set the
        # level of the log record to logging.ERROR.
        except Exception as e:
            # Get the exception traceback.
            # This is used to display the traceback in the logs.
            exc_type, exc_value, exc_traceback = exc_info()
            
            # If show_exception_traceback=False, the traceback will not be
            # displayed.
            if show_exception_traceback:
                record.exc_info = exc_type, exc_value, exc_traceback
                
            # If show_stack_info=False, the call stack will not be displayed.
            if show_stack_info:
                record.stack_info = "Call stack:\n" + "".join(format_stack()).rstrip()
            
            # Return the exception as the result of the function to be logged.
            result = e.with_traceback(exc_traceback)
            
            # Set an error message
            record.levelno = logging.ERROR
            record.levelname = logging.getLevelName(record.levelno)
            record.msg = f"{func.__name__}() did not finish due to " \
                         f"{type(e).__name__} exception: {str(e)}"
        
        # If the function did not raise an exception, log the execution time
        else:
            end = perf_counter()
            
            record.msg = f"{func.__name__}()"
            
            # Append args and kwargs values on the message if show_args_kwargs=True
            if show_args_kwargs:
                record.msg += f" with {args=}, {kwargs=}"
                
            # Append the result of the function if show_result=True
            if show_result:
                record.msg += f", {result=}"

            # Append the execution time
            record.msg += f" done in {end - start} seconds."

        # Display the message after execution.
        finally:
            logger.handle(record)
            
        return result

    return wrapper


# Raises a ModuleNotFoundError if termcolor is not installed.
def _check_termcolor() -> None:
    """Raises a ModuleNotFoundError if termcolor is not installed.

    Raises:
        ModuleNotFoundError: If termcolor is not installed.
        AttributeError: If colored() is not defined in the termcolor module.
        TypeError: If colored() is not a callable.
    """
    
    # Try to import termcolor.
    try:
        colored = __import__("termcolor").colored
        
    # Raise the following exceptions if termcolor is not installed properly.
    except ModuleNotFoundError as e:
        raise ModuleNotFoundError("The `termcolor` module is not installed.") from e
    except AttributeError as e:
        raise AttributeError("The `colored()` is not defined in the `termcolor` module.") from e
    
    if not callable(colored):
        raise TypeError("The function `colored()` is not callable. Are you sure you "
                        "have the correct `termcolor` module installed?")


if __name__ == "__main__":
    # Print the docstring of the setup_logger function
    print(setup_logger.__doc__)

    # Setup a logger that writes to the stream and file
    my_logger = setup_logger(__name__, file=".log")

    # Test the logger for different logging levels
    my_logger.debug("This is a debug message.")
    my_logger.info("This is an info message.")
    my_logger.warning("This is a warning message.")
    my_logger.error("This is an error message.")
    my_logger.critical("This is a critical message.")

    # Setup a logger that writes to the stream only, with colored_stream=True
    try: 
        colored_logger = setup_logger("colored_logger", colored_stream=True)
    # If `termcolor` is not installed, warn the user and do not setup the logger.
    except ModuleNotFoundError as e:
        my_logger.warning("The `termcolor` module is not installed.")
    # Test the colored_logger for different logging levels
    # Note the colors on console
    else:
        colored_logger.debug("This is a colored debug message.")
        colored_logger.info("This is a colored info message.")
        colored_logger.warning("This is a colored warning message.")
        colored_logger.error("This is a colored error message.")
        colored_logger.critical("This is a colored critical message.")
    