from Instruments.visacom import get_visa_resource, send_scpi_command, get_visa_string_ip
import numpy as np
import pyvisa

from System.logger import get_logger
logger = get_logger(__name__)
import time

class Instrument:
    """
    Abstract class for SCPI Instrument
    """
    def __init__(self,  ip=0, visa_usb=0):
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

    def get_idn(self):
        return send_scpi_command(self.instr, "*IDN?")
    
    def reset(self):
        send_scpi_command(self.instr, "*RST")
        time.sleep(2)
    
    def get_model(self):
        idn = self.get_idn()
        _, self.model, _, _ = idn.split(',')

    def set_ip(self, ip):
        self.ip = ip

    def connect(self):
        if not self.is_initialized():
            try:
                self.instr = get_visa_resource(get_visa_string_ip(self.ip))
                self.initialized = True
                self.get_model()
                logger.info(f"Connected to instrument at {self.ip}")
            except pyvisa.errors.VisaIOError:
                logger.error(f"Error connecting to instrument at {self.ip}")
                self.instr = None
                self.initialized = False 
        else:
            logger.info(f"Instrument at {self.ip} is already connected")

    


    