import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name, log_file, level=logging.INFO):
    """Function setup as many loggers as you want"""
    # Make sure parent directory exists
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create handlers
    s_handler = logging.StreamHandler()
    f_handler = RotatingFileHandler(filename=log_file, maxBytes=1000000, backupCount=5)

    # Create formatter and add it to handlers
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    s_handler.setFormatter(formatter)
    f_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(s_handler)
    logger.addHandler(f_handler)

    return logger
