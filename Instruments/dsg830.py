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
     
    def __init__(self, ip, visa_usb):
        super().__init__(ip, visa_usb)
        self.type = 'Microwave Generator'

        # self.default_setup()

    def default_setup(self):
        if not self.is_initialized():
            return  
        self.set_frequency(FREQ)
        self.set_level(LEVEL)

        time.sleep(0.1)

    # Frequency control (FREQ)  
    @Instrument.device_checking
    def set_frequency(self, frequency):
        self.send(f":FREQuency {frequency}")
        
    @Instrument.device_checking
    def get_frequency(self):
        return float(self.send(":FREQuency?"))
    
    # Level of output signal power (LEVEL)
    @Instrument.device_checking
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

    @Instrument.device_checking
    def get_level(self):
        return float(self.send(":LEV?"))

    # Turn ON/OFF the output signal (RF/on)
    @Instrument.device_checking
    def get_output_state(self):
        """
        Query the on/off state of the RF output
        """
        if self.is_initialized():      
            return int(self.send(":OUTPut?"))

    @Instrument.device_checking
    def rf_on(self):
        self.send(":OUTPut ON")

    @Instrument.device_checking
    def rf_off(self):
        self.send(":OUTPut OFF")

    # Turn Modulation ON/OFF of the output signal (Mod/on)
    @Instrument.device_checking
    def get_modulation_state(self):
        return int(self.send(":SOURce:MODulation:STATe?"))
    
    @Instrument.device_checking
    def get_settings_from_device(self):

        self.state_changed.emit({
            'frequency': self.get_frequency(),
            'level': self.get_level(),
            'rf_state': self.get_output_state(),
            'mod_state': self.get_modulation_state()
            })
