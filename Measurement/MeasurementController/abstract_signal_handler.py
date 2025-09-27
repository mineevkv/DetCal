from abc import ABC, abstractmethod


from System.logger import get_logger
logger = get_logger(__name__)

class SignalHandler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def init (self):
        pass

    @abstractmethod
    def handler(self, message):
        pass


        

