import logging
from typing import Iterable, TypedDict, override, NotRequired

from termcolor import colored
import termcolor._types


# Type hint for styling based on termcolor.colored arguments
class _TermColorStyle(TypedDict):
    color: NotRequired[termcolor._types.Color | None]
    on_color: NotRequired[termcolor._types.Highlight | None]
    attrs: NotRequired[Iterable[termcolor._types.Attribute] | None]
    no_color: NotRequired[bool | None]
    force_color: NotRequired[bool | None]


# Default color mapping for specific log levels
# Warning: opinionated style
_STYLES: dict[int, _TermColorStyle] = {
    logging.DEBUG: {"color": "cyan", "on_color": None, "attrs": ["bold"]},
    logging.INFO: {"color": "green", "on_color": None, "attrs": None},
    logging.WARNING: {"color": "yellow", "attrs": ["underline"]},
    logging.ERROR: {"color": "red", "on_color": None},
    logging.CRITICAL: {"color": "red", "on_color": "on_yellow", "attrs": ["bold"]},
}

# Custom stream handler class that colors the entire log line based on log level.
class ColoredStreamHandler(logging.StreamHandler):
    """
    Custom stream handler class that colors the entire log line based on log level.

    Args:
        colors (dict[int, _TermColorStyle]): A dictionary mapping log levels to color names.
        *args: Variable length argument list for the parent class.
        **kwargs: Arbitrary keyword arguments for the parent class.
    """
    def __init__(self, styles: dict[int, _TermColorStyle] | None = _STYLES, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set the colors dictionary, default to an empty dict if not provided
        self.styles = styles if styles is not None else {}

    def _get_style_for_level(self, levelno: int) -> _TermColorStyle:
        """Determine the appropriate style based on the log level."""
        # Sort the log levels in descending order to find the closest matching level
        sorted_levels = sorted(self.styles.keys(), reverse=True)

        for level in sorted_levels:
            if levelno >= level:
                return self.styles[level]
            
        # Default to no color if no match is found
        return {"color": None, "on_color": None, "attrs": None}
    
    @override
    def emit(self, record: logging.LogRecord):
        try:
            # Format the log message
            message = self.format(record)

            # Get the style based on the log level
            style = self._get_style_for_level(record.levelno)

            if style.get("force_color"):
                self.stream.write(message + self.terminator)

            else:
                color = style.get("color", None)
                on_color = style.get("on_color", None)
                attrs = style.get("attrs", None)

                # Apply the color, highlight, and attributes using termcolor.colored
                if style.get("force_color", False) or (color or on_color or attrs):
                    message = colored(message, color=color, on_color=on_color, attrs=attrs)
                    
                self.stream.write(message + self.terminator)

            self.flush()

        except Exception:
            self.handleError(record)


if __name__ == "__main__":
    # * Sample usage and demonstration of a colored logger

    # Set up a logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    # Create a handler with the level-to-style mapping
    colored_handler = ColoredStreamHandler()

    # Create a formatter
    formatter = logging.Formatter(
        "[%(asctime)s.%(msecs)03d] [%(name)s/%(levelname)s] [%(module)s:%(funcName)s:%(lineno)s]: %(message)s", 
        datefmt="%d%b%Y %H:%M:%S"
    )

    # Set the formatter to the created custom handler
    colored_handler.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(colored_handler)

    # Test the logging with standard log levels
    logger.debug('This is a debug message.')
    logger.info('This is an info message.')
    logger.warning('This is a warning message.')
    logger.error('This is an error message.')

    try:
        num = 1/0
    except Exception as e:
        logger.exception(f"This is an exception message: {e}")

    logger.critical('This is a critical message.')