import logging
import colorlog
import os

def setup_logging():
    formatter = colorlog.ColoredFormatter(
        "%(asctime)s %(log_color)s %(message)s",
        datefmt='%H:%M:%S',  # Define the date/time format
        reset=True,
        log_colors={
            'DEBUG':    'cyan',
            'INFO':     'green',
            'WARNING':  'yellow',
            'ERROR':    'red',
            'CRITICAL': 'red,bg_white',
        },
        secondary_log_colors={},
        style='%'
    )

    # Create handler
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)
    
    return handler

def get_logger(name):
    """Factory function to get a configured logger"""
    handler = setup_logging()
    logger = colorlog.getLogger(name)
    
    # Only add handler if it doesn't have one already
    if not logger.handlers:
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False  # Prevent duplicate logs from parent loggers
    
    return logger