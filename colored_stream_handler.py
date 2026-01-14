import logging
from typing import override


class ColoredStreamHandler(logging.StreamHandler):  # pyright: ignore[reportMissingTypeArgument]
    fmt_colors = {  # pyright: ignore[reportUnannotatedClassAttribute]
        logging.DEBUG: "\x1b[35m",
        logging.INFO: "\x1b[34m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m",
        logging.CRITICAL: "\x1b[37;41m",
    }

    @override
    def format(self, record: logging.LogRecord) -> str:
        log_msg = super().format(record)
        color = self.fmt_colors.get(record.levelno, "")

        return f"{color}{log_msg}\x1b[0m"


def main() -> None:
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    csh = ColoredStreamHandler()
    csh.setFormatter(
        logging.Formatter(
            "[%(asctime)s.%(msecs)d] [%(name)s:%(levelname)s] [%(filename)s:%(funcName)s:%(lineno)d] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    logger.addHandler(csh)

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")


if __name__ == "__main__":
    main()
