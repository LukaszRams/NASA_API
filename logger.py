"""
Logger configuration
"""

import logging
from logging.handlers import RotatingFileHandler


class StreamFormatter(logging.Formatter):
    """
    Custom formatter for stream handling adding log colouring according to level
    """

    grey = "\x1b\033[37m"
    green = "\x1b\033[92m"
    yellow = "\x1b\033[33m"
    red = "\x1b\033[95m"
    magenta = "\x1b\033[91m"
    reset = "\x1b[0m"
    fmt: str = "%(asctime)-25s [  %(levelname)-10s] | %(threadName)s %(filename)s %(lineno)d | %(message)s"

    FORMATS = {
        logging.DEBUG: grey + fmt + reset,
        logging.INFO: green + fmt + reset,
        logging.WARNING: yellow + fmt + reset,
        logging.ERROR: magenta + fmt + reset,
        logging.CRITICAL: red + fmt + reset,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log message
        :param record: log record
        :return: formatted string
        """
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


def get_logger() -> logging.Logger:
    """
    Get custom app logger
    """
    logger = logging.getLogger("NASA API Logger")
    logger.setLevel(logging.DEBUG)

    # stream handling
    stream_formatter = StreamFormatter()
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(stream_formatter)
    logger.addHandler(stream_handler)

    # file handling
    file_formatter = logging.Formatter(StreamFormatter.fmt)
    file_handler = RotatingFileHandler("NASA_API.log", mode="a", maxBytes=100_000_000)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    return logger


app_logger = get_logger()
