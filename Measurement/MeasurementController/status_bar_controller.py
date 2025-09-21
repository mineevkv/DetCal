from System.logger import get_logger
logger = get_logger(__name__)

from GUI.palette import *

class StatusBarController():
    def __init__(self, elem):
        self.status_bar = elem

    @staticmethod
    def set_text(func):
        def wrapper(self, text):
            func(self, text)
            self.status_bar.setText(text)
        return wrapper
    
    @set_text
    def info(self, text):
        self.status_bar.setStyleSheet(f"color: {SURFGREEN}")
        logger.debug(f'Status bar: {text}')

    @set_text    
    def error(self, text):
        self.status_bar.setStyleSheet(f"color: {RED}")
        logger.error(f'Status bar: {text}')

    @set_text
    def warning(self, text):
        self.status_bar.setStyleSheet(f"color: {YELLOW}")
        logger.warning(f'Status bar: {text}')

    @set_text
    def critical(self, text):
        self.status_bar.setStyleSheet(f"color: {VIOLET}")
        logger.critical(f'Status bar: {text}')