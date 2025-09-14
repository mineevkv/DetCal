from Instruments.scpi_instr import Instrument

import time
import numpy as np

from System.logger import get_logger
logger = get_logger(__name__)

# Default setup

FREQ = 1e9               # 100 МHz
LEVEL = -50              # -100 dBm

class DSG830(Instrument):

    max_level = 20
    min_level = -110
     
    def __init__(self, ip=0, visa_usb=0):
        super().__init__(ip, visa_usb)

        if not self.is_initialized():
            return
        
        self.type = 'Microwave Generator'

        # self.default_setup()

    def default_setup(self):
        if not self.is_initialized():
            return  
        self.set_frequency(FREQ)
        self.set_level(LEVEL)

        time.sleep(0.1)

    # Frequency control (FREQ)  

    def set_frequency(self, frequency):
        if self.is_initialized():
             self.send(f":FREQuency {frequency}")
             self.state_changed.emit({'frequency': frequency})
        

    def get_frequency(self):
        if self.is_initialized():
            return float(self.send(":FREQuency?"))
    
    # Level of output signal power (LEVEL)

    def set_level(self, level):
        """
        Set the output level in dBm
        """
        if not self.is_initialized():
            return

        if level <=self.max_level and level >= self.min_level:
            self.send(f":LEV {level}dBm")
            self.state_changed.emit({'level': level})
        else:
            logger.warning("Output level out of range")

    def get_level(self):
        if self.is_initialized():
            return float(self.send(":LEV?"))

    # Turn ON/OFF the output signal (RF/on)

    def get_output_state(self):
        """
        Query the on/off state of the RF output
        """
        if self.is_initialized():      
            return int(self.send(":OUTPut?"))
    
    def rf_on(self):
        if self.is_initialized():
            self.send(":OUTPut ON")
            self.state_changed.emit({'rf': True})

    def rf_off(self):
        if self.is_initialized():
            self.send(":OUTPut OFF")
            self.state_changed.emit({'rf': False})