from Instruments.visacom import VisaCom
import numpy as np
import pyvisa
from PyQt6.QtCore import QObject, pyqtSignal

from System.logger import get_logger
logger = get_logger(__name__)
import time

class Instrument(VisaCom, QObject):
    """Abstract class for SCPI Instrument"""
    state_changed = pyqtSignal(dict)  # Signal to notify settings changes

    def __init__(self, ip=0, visa_usb=0):
        VisaCom.__init__(self)
        QObject.__init__(self) 
        
        self.set_ip(ip)
        self.initialized = False
        self.model = 'None'
        self.type = 'No Instrument'

        self.connect()

    def __del__(self):
        if self.instr is not None:
            self.instr.close()
            logger.info(f"Disconnected from {self.model} at {self.ip}")

    def is_initialized(self):
        return self.initialized and self.instr is not None
    
    # decorator
    @staticmethod
    def device_checking(func):
        """
        Decorator to check if device is connected and initialized
        """
        def wrapper(self, *args, **kwargs):
            if self.is_initialized():
                return func(self, *args, **kwargs)
            logger.error("Device is not initialized")
        return wrapper
    
    def get_idn(self):
        return self.send("*IDN?")
    
    def reset(self):
        self.send("*RST")
        time.sleep(2)
    
    def get_model(self):
        idn = self.get_idn()
        _, self.model, _, _ = idn.split(',')

    def set_ip(self, ip):
        self.ip = ip
        self.state_changed.emit({'ip': self.ip})

    def get_ip(self):
        if self.is_initialized():
            return self.ip
        else:
            return None

    def connect(self):
        if not self.is_initialized():
            try:
                self.instr = VisaCom.get_visa_resource(VisaCom.get_visa_string_ip(self.ip))
                self.initialized = True
                self.get_model()
                logger.info(f"Connected to instrument at {self.ip}")
            except pyvisa.errors.VisaIOError:
                logger.error(f"Error connecting to instrument at {self.ip}")
                self.instr = None
                self.initialized = False 
        else:
            logger.info(f"Instrument at {self.ip} is already connected")

    


    