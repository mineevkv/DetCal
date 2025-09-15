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
    connection_finished = pyqtSignal()  # New signal for connection completion

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
            logger.debug("Stopping existing connect thread")
            self.connect_thread.quit()
            self.connect_thread.wait()
            self.connect_thread.deleteLater()
            self.connect_thread = None

        # Create new thread and keep a strong reference
        logger.debug("Creating new ConnectThread")
        self.connect_thread = ConnectThread(self)
        
        # Store the connection in a variable to prevent garbage collection
        self.connect_thread.connection_result.connect(self.handle_connection_result)
        self.connect_thread.finished.connect(self.on_connect_thread_finished)
        
        self.connect_thread.start()
        logger.debug("ConnectThread started")

    def handle_connection_result(self, success):
        """Handle the connection result from the thread"""
        logger.debug(f"Connection result received: {success}")
        self.initialized = success
        if success:
            self.get_model()
        
        # Emit state changed
        self.state_changed.emit({
            'ip': self.ip,
            'connected': self.initialized,
            'model': self.model
        })
        
        logger.debug("Connection process completed")
        self.connection_finished.emit()

    def on_connect_thread_finished(self):
        """Clean up the thread when it finishes"""
        logger.debug("Connect thread finished, cleaning up")
        if self.connect_thread:
            self.connect_thread.deleteLater()
            self.connect_thread = None

class ConnectThread(QThread):
    connection_result = pyqtSignal(bool)  # Signal with connection success status

    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        logger.debug("ConnectThread initialized")

    def __del__(self):
        """Clean up the thread when it's deleted"""
        logger.debug("ConnectThread deleted, cleaning up")
        if self.isRunning():
            self.quit()
            self.wait()
        

    def stop(self):
        """Stop the thread"""
        self.quit()
        logger.debug("ConnectThread stopping")

    def run(self):
        logger.debug("ConnectThread running")
        self.stop()
        return
    
    
        # success = False
        # try:
        #     logger.debug(f"ConnectThread running - attempting to connect to {self.parent.ip}")
        #     visa_string = VisaCom.get_visa_string_ip(self.parent.ip)
        #     logger.debug(f"VISA string: {visa_string}")
            
        #     self.parent.instr = VisaCom.get_visa_resource(visa_string)
        #     if self.parent.instr:
        #         success = True
        #         self.parent.initialized = True
        #         # Test communication to verify connection
        #         try:
        #             idn = self.parent.get_idn()
        #             if idn:
        #                 self.parent.get_model()
        #                 logger.info(f"Connected to instrument at {self.parent.ip}")
        #             else:
        #                 success = False
        #                 logger.error(f"Could not communicate with instrument at {self.parent.ip}")
        #                 self.parent.instr = None
        #                 self.parent.initialized = False
        #         except Exception as e:
        #             logger.error(f"Error during IDN query: {e}")
        #             success = False
        #             self.parent.instr = None
        #             self.parent.initialized = False
        #     else:
        #         logger.error(f"Failed to get visa resource for {self.parent.ip}")
        #         success = False
                
        # except pyvisa.errors.VisaIOError as e:
        #     logger.error(f"VisaIOError connecting to instrument at {self.parent.ip}: {e}")
        #     self.parent.instr = None
        #     self.parent.initialized = False
        #     self.parent.model = 'None'
        #     success = False
        # except Exception as e:
        #     logger.error(f"Unexpected error connecting to instrument: {e}")
        #     self.parent.instr = None
        #     self.parent.initialized = False
        #     self.parent.model = 'None'
        #     success = False
        # finally:
        #     # Emit the result signal
        #     logger.debug(f"About to emit connection_result: {success}")
        #     self.connection_result.emit(success)
        #     logger.debug("connection_result emitted")



    