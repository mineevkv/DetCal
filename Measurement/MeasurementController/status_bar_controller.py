from System.logger import get_logger

logger = get_logger(__name__)

from GUI.palette import *


class StatusBarController:
    """Controller for the status bar in the GUI."""

    def __init__(self, elem: object) -> None:
        self.status_bar = elem

    @staticmethod
    def set_text(func: object) -> object:
        """Decorator to set the text of the status bar."""

        def wrapper(self, text: str) -> None:
            func(self, text)
            self.status_bar.setText(text)

        return wrapper

    @set_text
    def info(self, text: str) -> None:
        """Set the info text of the status bar."""
        self.status_bar.setStyleSheet(f"color: {SURFGREEN}")
        logger.debug(f"Status bar: {text}")

    @set_text
    def error(self, text: str) -> None:
        """Set the error text of the status bar."""
        self.status_bar.setStyleSheet(f"color: {RED}")
        logger.error(f"Status bar: {text}")

    @set_text
    def warning(self, text: str) -> None:
        """Set the warning text of the status bar."""
        self.status_bar.setStyleSheet(f"color: {YELLOW}")
        logger.warning(f"Status bar: {text}")

    @set_text
    def critical(self, text: str) -> None:
        """Set the critical text of the status bar."""
        self.status_bar.setStyleSheet(f"color: {VIOLET}")
        logger.critical(f"Status bar: {text}")
