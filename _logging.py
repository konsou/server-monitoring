import logging
import sys
from typing import Union

FORMAT_STRING = "[%(asctime)s] %(levelname)-8s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

try:
    import colorama

    COLORAMA_AVAILABLE = True
    colorama.init()
except ImportError:
    colorama = None
    COLORAMA_AVAILABLE = False


LogLevel = Union[
    logging.NOTSET,
    logging.DEBUG,
    logging.INFO,
    logging.WARNING,
    logging.ERROR,
    logging.CRITICAL,
]


class ColorFormatter(logging.Formatter):
    yellow = "\x1b[33m"
    red = "\x1b[31m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: FORMAT_STRING,
        logging.INFO: FORMAT_STRING,
        logging.WARNING: yellow + FORMAT_STRING + reset,
        logging.ERROR: red + FORMAT_STRING + reset,
        logging.CRITICAL: bold_red + FORMAT_STRING + reset,
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt=DATE_FORMAT)
        return formatter.format(record)


def configure_logger(
    log_file: str,
    level: LogLevel = logging.INFO,
    name: str = "server-monitoring",
    stdout: bool = True,
) -> logging.Logger:
    logging.basicConfig(
        format=FORMAT_STRING,
        datefmt=DATE_FORMAT,
        level=level,
        filename=log_file,
    )
    logger = logging.getLogger(name)
    if stdout:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(ColorFormatter())
        logger.addHandler(stdout_handler)
    return logger
