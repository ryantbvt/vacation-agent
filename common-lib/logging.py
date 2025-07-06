import logging
import time

_logger = None

def init_logger(name=None):
    '''
    Description: Initializes logger

    Args:
        name (str): The name for the logger, typically __name__ from the calling module

    Returns: logging.Logger
    '''
    global _logger
    if _logger is None:
        # Create a formatter with a custom date and time format
        formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(pathname)s][%(funcName)s] | %(message)s', datefmt='%Y-%m-%d %H:%M:%S UTC')
        formatter.converter = time.gmtime

        # Create a stream handler and set the formatter
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)

        # Create a logger instance using the provided name or fallback to __name__
        logger_name = name if name is not None else __name__
        _logger = logging.getLogger(logger_name)
        _logger.addHandler(stream_handler)
        _logger.setLevel(logging.INFO)

    return _logger