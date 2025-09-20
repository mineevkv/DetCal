
from PyQt6.QtCore import QThread, pyqtSignal
from queue import Queue
import threading
import json

from Instruments.rsa5065n import *
from Instruments.dsg830 import *
from Instruments.mdo34 import *


from System.logger import get_logger
logger = get_logger(__name__)

class InstrumentInitializer(QThread):
    """Class for instrument initialization"""
    finished = pyqtSignal(object, object, object, object)  # emits (gen, sa, osc, error) 
    
    def __init__(self):
        super().__init__()
        self.offline_debug =  False # Set to True to simulate offline mode

        self.load_instr_ip_settings()

    def load_instr_ip_settings(self):
        ip_settings = self.load_instr_ip_from_file('Settings/instr_ip.json')
        for key, value in ip_settings.items():
            setattr(self, key, value)

    @staticmethod
    def load_instr_ip_from_file(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load instrument IPs from {filename}: {e}")
            return {}

    def run(self):
        if self.offline_debug:
            logger.info("Offline debug mode")
            return     
        try:
            instr = {
                'gen': DSG830(self.ip_DSG830),
                'sa': RSA5065N(self.ip_RSA5065N),
                'osc': MDO34(self.ip_MDO34),
            }
            self.finished.emit(instr['gen'], instr['sa'], instr['osc'], None)
        except Exception as e:
            self.finished.emit(None, None, None, e)
            logger.error(f"Failed to initialize instruments objects: {e}")
