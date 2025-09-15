from Instruments.visacom import VisaCom
import numpy as np
import pyvisa
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtCore import QThread

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

        
        self.connect_thread = None # Create thread but don't start it yet

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

        # Clean up any existing thread
        if self.connect_thread and self.connect_thread.isRunning():
            self.connect_thread.quit()
            self.connect_thread.wait()
            self.connect_thread.start()

        # Create new thread
        self.connect_thread = ConnectThread(self)
        self.connect_thread.finished.connect(self.connect_finished)
        self.connect_thread.start()

    def connect_finished(self):
        logger.debug("Connect thread finished")

class ConnectThread(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def run(self):
        try:
            self.parent.instr = VisaCom.get_visa_resource(VisaCom.get_visa_string_ip(self.parent.ip))
            self.parent.initialized = True
            self.parent.get_model()
            logger.info(f"Connected to instrument at {self.parent.ip}")
            
        except pyvisa.errors.VisaIOError:
            logger.error(f"Error connecting to instrument at {self.parent.ip}")
            self.parent.instr = None
            self.parent.initialized = False
            self.parent.model = 'None'

        self.parent.state_changed.emit({
            'ip': self.parent.ip,
            'connected': self.parent.initialized,
            'model': self.parent.model
        })

    


    