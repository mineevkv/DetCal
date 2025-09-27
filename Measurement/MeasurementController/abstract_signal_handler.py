from abc import ABC, abstractmethod


from System.logger import get_logger
logger = get_logger(__name__)

class SignalHandler(ABC):
    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def init (self):
        pass

    @staticmethod
    @abstractmethod
    def handler(self, message):
        pass


        

