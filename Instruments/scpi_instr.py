from Instruments.visacom import VisaCom
from functools import wraps
import numpy as np
import pyvisa
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtCore import QThread
from PyQt6.QtCore import pyqtSignal, QObject, Qt
from PyQt6.QtCore import QMutex
from abc import ABC, abstractmethod

from System.logger import get_logger
logger = get_logger(__name__)
import time


class ConnectThread(QThread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent

    def __del__(self):
        logger.debug(f"{self.__class__.__name__}: thread deleted")
        
    def run(self):
        try:
            self.parent.instr = VisaCom.get_visa_resource(VisaCom.get_visa_string_ip(self.parent.ip))
            if self.parent.instr is None:
                return
            self.parent.initialized = True
            self.parent.get_model()
            logger.info(f"Connected to instrument at {self.parent.ip}")
            
        except pyvisa.errors.VisaIOError:
            logger.error(f"Error connecting to instrument at {self.parent.ip}")
            self.parent.instr = None
            self.parent.initialized = False
            self.parent.model = 'None'
        finally:
            self.parent.state_changed.emit({
                'ip': self.parent.ip,
                'connected': self.parent.initialized,
                'model': self.parent.model,
                'type': self.parent.get_type(),
                'thread': self.parent.connect_thread
            })
            self.parent.get_settings_from_device()

class Instrument(VisaCom, QObject):
    """Abstract class for SCPI Instrument"""
    state_changed = pyqtSignal(dict)  # Signal to notify settings changes

    def __init__(self, ip, visa_usb):
        VisaCom.__init__(self)
        QObject.__init__(self) 
        self.initialized = False
        self.connect_thread = None
        self.ip = None
        self.model = 'None'
        self.type = 'No Instrument'

        self.set_ip(ip)
        # TODO: block access to instrument sheet if instrument is not from mylist

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
    
    @abstractmethod
    def get_settings_from_device(self):
        pass
    
    def get_idn(self):
        return self.send("*IDN?")
    
    def reset(self):
        self.send("*RST")
        self.state_changed.emit({'reset': True})
    
    def get_model(self):
        idn = self.get_idn()
        _, self.model, _, _ = idn.split(',')
    
    def get_type(self):
        return self.type

    def set_ip(self, ip):
        if ip is not None:
            self.ip = ip
            self.state_changed.emit({'ip': self.ip})

    def get_ip(self):
        if self.is_initialized():
            return self.ip
        else:
            return None
        

    def connect(self):
        if self.connect_thread is not None:
            logger.debug(f"{self.__class__.__name__}: connect already running")
            return

        self.connect_thread = ConnectThread(self)
        logger.debug(f"{self.__class__.__name__}: connect thread created")
        self.connect_thread.start()
        
        
    