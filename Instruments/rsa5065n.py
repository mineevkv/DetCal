from Instruments.scpi_instr import Instrument
import numpy as np
import logging
import time
import pyvisa

from System.logger import get_logger
logger = get_logger(__name__)

# Default setup

CENTER_FREQ = 1.5e9        # 1.5 GHz (center between 1-2 GHz)
SPAN = 1e6                 # 1 GHz span (from 1-2 GHz)
REF_LEVEL = 0              # Reference level in dBm
RBW = 10e3                 # 10 kHz resolution bandwidth
VBW = 10e3                 # 10 kHz video bandwidth
SWEEP_TIME = 'AUTO ON'     # auto sweep time
SWEEP_POINTS = 1001        # Number of trace points


class RSA5065N(Instrument):

    def __init__(self, ip=0, visa_usb=0):
        super().__init__(ip, visa_usb)

        if not self.is_initialized():
            return 

        self.type = 'Spectrum Analyzer'

        self.default_setup()

    def default_setup(self):  
        self.set_swept_sa()
        
        self.set_center_freq(CENTER_FREQ)
        self.set_span(SPAN)
        self.set_ref_level(REF_LEVEL)
        self.set_rbw(RBW)
        self.set_vbw(VBW)
        self.set_sweep_time(SWEEP_TIME)
        self.set_sweep_points(SWEEP_POINTS)

        self.trace_clear_all()
        self.set_format_trace_bin()

        time.sleep(0.1)


    def get_trace_data(self):
        try:
            return self.instr.query_binary_values(":TRACe:DATA? TRACE1", 
                               datatype='f', 
                               container=np.ndarray,
                               is_big_endian=True)
        except Exception as e:
            logger.error(f"Error reading trace data: {e}")


    # Frequency (FREQ)
    def set_center_freq(self, freq):
        self.send(f":SENSE:FREQUENCY:CENTER {freq}")
        

    def get_start_freq(self):
        return float(self.send(f":FREQuency:STARt?"))

    def get_stop_freq(self):
        return float(self.send(f":FREQuency:STOP?"))
        

    # Span (SPAN)

    def set_span(self, span):
        self.send(f":SENSE:FREQUENCY:SPAN {span}")

    # Amplitude (AMPT)

    def set_ref_level(self, ref_level=0):
        self.send(f":DISPLAY:TRACE:Y:SCALE:RLEVEL {ref_level}")

    # Bandwidth (BW)

    def set_rbw(self, rbw):
        self.send(f":SENSE:BANDWIDTH:RESOLUTION {rbw}")

    def set_vbw(self, vbw):
        self.send(f":SENSE:BANDWIDTH:VIDEO {vbw}")

    # Trace (Trace)

    def set_trace_format(self, trace_format):
        self.send(f":FORMat:TRACe:DATA {trace_format}")

    def trace_clear_all(self):
        self.send(f":TRACe:CLEar:ALL")

    # Sweep (Sweep)

    def set_sweep_time(self, sweep_time):
        self.send(f":SENSE:SWEEP:TIME {sweep_time}")

    def get_sweep_time(self):
        return float(self.send(f":SENSe:SWEep:TIME?"))

    def set_sweep_points(self, sweep_points):
        self.send(f":SENSE:SWEEP:POINTS {sweep_points}")

    def get_sweep_points(self):
        return int(self.send(f":SENSe:SWEep:POINts?"))

    def set_single_sweep(self):
        self.send(":INITiate:CONTinuous OFF")

    def set_continuous_sweep(self):
        self.send(":INITiate:CONTinuous ON")

    # Single measurement (Single)
    
    def start_single_measurement(self):
        """
        Emulations pressing the front panel 'Single' button
        """
        self.set_single_sweep()
        self.send(":TRIGger:SEQuence:SOURce IMMediate")
        self.send(":INITiate:IMMediate")

    # Peak processing (Peak)
    def find_peak_max(self, marker_number=1):
        self.send(f":CALCulate:MARKer{marker_number}:MAXimum:MAX")

    def get_peak_freq(self, marker_number=1):
        return float(self.send(f":CALCulate:MARKer{marker_number}:X?"))

    def get_peak_level(self, marker_number=1):
        return float(self.send(f":CALCulate:MARKer{marker_number}:Y?"))

    # Format

    def set_format_trace_bin(self):
        """
        Set trace format data output to binary (REAL 32,  byte order: normal)
        """

        self.send(":FORMat:TRACe:DATA REAL,32")
        self.send(":FORMat:BORDer NORMal")

    # Configure

    def get_configure(self):
        """
        Returns the current measurement function
        """
        return self.send(":CONFigure?")
    
    def set_swept_sa(self):
        """
        Switches the analyzer to the swept SA mode
        """
        if 'SAN' not in self.get_configure():
            self.send(":CONFigure:SANalyzer") 



    

