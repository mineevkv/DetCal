from abc import ABC, abstractmethod


from System.logger import get_logger

logger = get_logger(__name__)


class SignalHandler(ABC):
    """Abstract class for signal handlers."""

    def __init__(self) -> None:
        pass

    @abstractmethod
    def init(self) -> None:
        pass

    @abstractmethod
    def handler(self, message: dict) -> None:
        pass
