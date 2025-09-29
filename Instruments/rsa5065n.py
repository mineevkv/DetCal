from Instruments.scpi_instr import Instrument
import numpy as np
import time


from System.logger import get_logger
logger = get_logger(__name__)


class RSA5065N(Instrument):

    def __init__(self, ip):
        super().__init__(ip)
        self.type = 'Spectrum Analyzer'


    @Instrument.device_checking
    def get_trace_data(self):
        try:
            return self.instr.query_binary_values(":TRACe:DATA? TRACE1", 
                               datatype='f', 
                               container=np.ndarray,
                               is_big_endian=True)
        except Exception as e:
            logger.error(f"Error reading trace data: {e}")

    # Frequency (FREQ)
    @Instrument.device_checking
    def set_center_freq(self, freq):  
        self.send(f":SENSE:FREQUENCY:CENTER {freq}")
        self.state_changed.emit({'CENTER_FREQ': freq})

    @Instrument.device_checking
    def get_center_freq(self):
        return float(self.send(f":SENSE:FREQUENCY:CENTER?"))
        
    @Instrument.device_checking
    def get_start_freq(self):
        return float(self.send(f":FREQuency:STARt?"))

    @Instrument.device_checking
    def get_stop_freq(self):
        return float(self.send(f":FREQuency:STOP?"))
        
    # Span (SPAN)
    @Instrument.device_checking
    def set_span(self, span):
        self.send(f":SENSE:FREQUENCY:SPAN {span}")
        self.state_changed.emit({'SPAN': span})

    @Instrument.device_checking
    def get_span(self):
        return float(self.send(f":SENSe:FREQuency:SPAN?"))

    # Amplitude (AMPT)
    @Instrument.device_checking
    def set_ref_level(self, ref_level=0):
        self.send(f":DISPlay:WINDow:TRACe:Y:SCALe:RLEVel {ref_level}")
        self.state_changed.emit({'REF_LEVEL': ref_level})

    # Bandwidth (BW)
    @Instrument.device_checking
    def set_rbw(self, rbw):
        self.send(f":SENSE:BANDWIDTH:RESOLUTION {rbw}")
        self.state_changed.emit({'RBW': rbw})

    @Instrument.device_checking
    def set_vbw(self, vbw):
        self.send(f":SENSE:BANDWIDTH:VIDEO {vbw}")
        self.state_changed.emit({'VBW': vbw})

    # Trace (Trace)
    @Instrument.device_checking
    def set_trace_format(self, trace_format):
        self.send(f":FORMat:TRACe:DATA {trace_format}")
        self.state_changed.emit({'TRACE_FORMAT': trace_format})

    @Instrument.device_checking
    def trace_clear_all(self):
        self.send(f":TRACe:CLEar:ALL")

    # Sweep (Sweep)
    @Instrument.device_checking
    def set_sweep_time(self, sweep_time):
        self.send(f":SENSE:SWEEP:TIME {sweep_time}")
        self.state_changed.emit({'SWEEP_TIME': sweep_time})

    @Instrument.device_checking
    def get_sweep_time(self):
        return float(self.send(f":SENSe:SWEep:TIME?"))

    @Instrument.device_checking
    def set_sweep_points(self, sweep_points):
        self.send(f":SENSE:SWEEP:POINTS {sweep_points}")
        self.state_changed.emit({'SWEEP_POINTS': sweep_points})

    @Instrument.device_checking
    def get_sweep_points(self):
        return int(self.send(f":SENSe:SWEep:POINts?"))

    @Instrument.device_checking
    def set_single_sweep(self):
        self.send(":INITiate:CONTinuous OFF")
        self.state_changed.emit({'SINGLE_SWEEP': True, 'CONTINUOUS_SWEEP': False})

    @Instrument.device_checking
    def set_continuous_sweep(self):
        self.send(":INITiate:CONTinuous ON")
        self.state_changed.emit({'SINGLE_SWEEP': False, 'CONTINUOUS_SWEEP': True})

    # Single measurement (Single)
    @Instrument.device_checking
    def start_single_measurement(self):
        """
        Emulations pressing the front panel 'Single' button
        """
        self.set_single_sweep()
        self.send(":TRIGger:SEQuence:SOURce IMMediate")
        self.send(":INITiate:IMMediate")

    # Peak processing (Peak)
    @Instrument.device_checking
    def find_peak_max(self, marker_number=1):
        self.send(f":CALCulate:MARKer{marker_number}:MAXimum:MAX")

    @Instrument.device_checking
    def get_peak_freq(self, marker_number=1):
        return float(self.send(f":CALCulate:MARKer{marker_number}:X?"))

    @Instrument.device_checking
    def get_peak_level(self, marker_number=1):
        return float(self.send(f":CALCulate:MARKer{marker_number}:Y?"))

    # Format
    @Instrument.device_checking
    def set_format_trace_bin(self):
        """
        Set trace format data output to binary (REAL 32,  byte order: normal)
        """

        self.send(":FORMat:TRACe:DATA REAL,32")
        self.send(":FORMat:BORDer NORMal")
        self.state_changed.emit({'TRACE_FORMAT': 'REAL 32'})

    # Configure
    @Instrument.device_checking
    def get_configure(self):
        """
        Returns the current measurement function
        """
        return self.send(":CONFigure?")
    
    @Instrument.device_checking
    def set_swept_sa(self):
        """
        Switches the analyzer to the swept SA mode
        """
        if 'SAN' not in self.get_configure():
            self.send(":CONFigure:SANalyzer")
            self.state_changed.emit({'CONFIGURE': 'Spectrum Analyzer'}) 

    @Instrument.device_checking
    def delay_after_start(self, delay_time=None):
        if delay_time is None:
            delay_time = self.get_sweep_time()*2 + 0.3
        time.sleep(delay_time)



    

