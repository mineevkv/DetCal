from Instruments.scpi_instr import Instrument
import numpy as np
import logging
import time
import pyvisa

from System.logger import get_logger
logger = get_logger(__name__)

class MDO34(Instrument):

    channel_map = {
            1: 'CH1',
            2: 'CH2', 
            3: 'CH3', 
            4: 'CH4'
        }
    
    vertical_map = [1e-3, 2e-3, 5e-3, 1e-2, 2e-2, 5e-2, 1e-1, 2e-1, 5e-1, 1]
    
    def __init__(self, ip):
        super().__init__(ip)

        self._selected_channel = 1
        self.type = 'Oscilloscope'


    @property
    def selected_channel(self):
        return self._selected_channel
    
    @selected_channel.setter
    def selected_channel(self, channel):
        reverse_map = {v: k for k, v in self.channel_map.items()}
        
        if channel in self.channel_map:
            self._selected_channel = channel
        elif channel in reverse_map:
            self._selected_channel = reverse_map[channel]
    

    @Instrument.device_checking 
    def channel_on(self, channel=None):
        if channel is None:
            channel=self._selected_channel

        self.send(f'SELECT:CH{channel} ON')
        self.state_changed.emit({f'CH{channel}': True})

    @Instrument.device_checking 
    def channel_off(self, channel=None):
        if channel is None:
            channel=self._selected_channel

        self.send(f'SELECT:CH{channel} OFF')
        self.state_changed.emit({f'CH{channel}': False})

 

    @Instrument.device_checking 
    def select_channel(self, channel=None):
        reverse_map = {v: k for k, v in self.channel_map.items()}
        
        if channel in self.channel_map:
            self._selected_channel = channel
        elif channel in reverse_map:
            self._selected_channel = reverse_map[channel]
        else:
            logger.error(f"Unknown channel: {channel}")
            raise ValueError(f"Unknown channel: {channel}")

        self.send(f'SELECT:CH{self._selected_channel}')
        self.state_changed.emit({'SELECT_CH': self._selected_channel})

    @Instrument.device_checking
    def get_active_channels(self) -> dict:
        channel_state = dict()
        response = self.send(f'SELECT?').split(';') # response: 1;0;0;0;...;CH2

        for i, channel in enumerate(self.channel_map.values()):
            channel_state[channel] = bool(int(response[i]))
        return channel_state

    @Instrument.device_checking 
    def is_channel_on(self, channel):
        return self.send(f'SELECT:{channel}?')
    
    @Instrument.device_checking 
    def get_selected_channel(self): #response: CH1
        response = self.send(f'SELECT:CONTROl?')
        if response is not None and response.startswith('CH'):
            channel = int(response[2:])
            self.state_changed.emit({'SELECT_CH': channel})
            return channel
        return 0

    @Instrument.device_checking    
    def set_coupling(self, coupling='DC'):
        self.send(f'CH{self._selected_channel}:COUP {coupling}')
        self.state_changed.emit({'COUPLING': coupling})

    @Instrument.device_checking
    def set_vertical_scale(self, scale=1):
        """Vertical scale in voltages"""
        self.send(f'CH{self._selected_channel}:SCALE {scale}')
        self.state_changed.emit({'VERT_SCALE' : scale})

    @Instrument.device_checking
    def get_channel_parameters(self):
         """Returns the vertical parameters for channel"""
         return self.send(f'CH{self._selected_channel}?')

    @Instrument.device_checking
    def get_vertical_scale(self):
        return float(self.send(f'CH{self._selected_channel}:SCALE?'))

    @Instrument.device_checking
    def set_vertical_position(self, offset=0):
        """Vertical offset in voltages"""
        self.send(f'CH{self._selected_channel}:OFFSET {offset}')
        self.state_changed.emit({'VERT_POS' : offset})

    @Instrument.device_checking
    def get_vertical_position(self):
        return float(self.send(f'CH{self._selected_channel}:OFFSET?'))

    @Instrument.device_checking
    def set_bandwidth(self, bandwidth='FULL'):
        """Low-pass bandwidth limit filter for channel"""
        self.send(f'CH{self._selected_channel}:BANDWIDTH {bandwidth}')

    @Instrument.device_checking
    def set_horizontal_scale(self, scale='1s'):
        """Horizontal scale in seconds"""
        self.send(f'HORIZONTAL:SCALE {scale}')
        self.state_changed.emit({'HOR_SCALE' : scale})

    @Instrument.device_checking
    def get_horizontal_scale(self):
        return float(self.send(f'HORIZONTAL:SCALE?'))

    @Instrument.device_checking
    def set_horizontal_position(self, position=0):
        self.send(f'HORIZONTAL:POSITION {position}')
        self.state_changed.emit({'HOR_POS' : position})

    @Instrument.device_checking
    def get_horizontal_position(self):
        return float(self.send(f'HORIZONTAL:POSITION?'))

    @Instrument.device_checking
    def set_measurement_source(self, source):
        if source is None:
            source=self._selected_channel
        self.send(f'MEASUREMENT:IMMED:SOURCE CH{self._selected_channel}')

    @Instrument.device_checking
    def set_measurement_type(self, type='AMPLITUDE'):
        self.send(f'MEASUREMENT:IMMED:TYPE {type}')

    @Instrument.device_checking
    def set_trigger_type(self, type='EDGE'):
        self.send(f'TRIGGER:A:TYPE {type}')

    @Instrument.device_checking
    def set_trigger_source(self, source=None):
        if source is None:
            source=self._selected_channel
        self.send(f'TRIGGER:A:EDGE:SOURCE {source}')

    @Instrument.device_checking
    def set_trigger_level(self, level=0):
        self.send(f'TRIGGER:A:LEVEL {level}')

    @Instrument.device_checking
    def set_50Ohm_termination(self):
        self.set_termination('FIFty')

    @Instrument.device_checking
    def set_1MOhm_termination(self):
        self.set_termination('MEG')

    @Instrument.device_checking
    def set_termination(self, termination):
        """FIFty|MEG"""
        self.send(f'CH{self._selected_channel}:TERMINATION {termination}')
        self.state_changed.emit({'TERMINATION': termination})

    @Instrument.device_checking
    def get_termination(self):
        return self.send(f'CH{self._selected_channel}:TERMINATION?')
    
    def get_all_terminations(self):
        terminations = {}
        for channel in self.channel_map.values():
            terminations[channel] = self.send(f'{channel}:TERMINATION?')
        return terminations

    @Instrument.device_checking
    def stop_after_sequence(self):
        self.send('ACQUIRE:STOPAFTER SEQUENCE')

    @Instrument.device_checking
    def ready_for_acquisition(self):
        self.send('ACQUIRE:STATE ON')

    @Instrument.device_checking
    def trigger_force(self):
        self.send('TRIGger FORCe')

    @Instrument.device_checking
    def is_acquiring(self): 
        return bool(int(self.send('ACQUIRE:STATE?')))
    
    @Instrument.device_checking
    def set_data_source(self,source=None):
        if source is None:
            source=self._selected_channel
        self.send(f'DATA:SOURCE CH{source}')

    @Instrument.device_checking
    def set_data_points(self,points=1000):
        self.send('DATA:START 1')
        self.send(f'DATA:STOP {points}')

    @Instrument.device_checking
    def set_binary_data_format(self):
        self.send('DATA:WIDTH 2') # 2 bytes per point
        self.send('DATA:ENCDG RPBinary') # Signed integer binary

    @Instrument.device_checking
    def get_waveform_parameters(self):
        """
        Get waveform parameters

        Returns:
            ymult (float): vertical scale multiplying factor
            yzero (float): vertical offset of the destination reference waveform
            yoff (float): vertical offset of the source waveform
            xincr (float): point spacing in units of time (seconds)
            xzero (float): the time coordinate of the first data point
        """

        ymult = float(self.send('WFMOUTPRE:YMULT?'))
        yzero = float(self.send('WFMOUTPRE:YZERO?'))
        yoff = float(self.send('WFMOUTPRE:YOFF?'))
        xincr = float(self.send('WFMOUTPRE:XINCR?'))
        xzero = float(self.send('WFMOUTPRE:XZERO?'))

        return ymult, yzero, yoff, xincr, xzero
    
    @Instrument.device_checking
    def get_waveform_data(self):
        """
        Returns: waveform data as numpy ndarray: time_data, voltage_data
        """
        
        data = self.instr.query_binary_values('CURVE?', 
                                      datatype='H',  # 'H' for unsigned 16-bit integers
                                      container=np.ndarray,
                                      is_big_endian=True,  # MSB first from preamble
                                      expect_termination=True)
        
        ymult, yzero, yoff, xincr, xzero = self.get_waveform_parameters()
        
        # Convert data to voltage
        voltage_data = (data - yoff) * ymult + yzero
        # Create time array
        time_data = xzero + np.arange(len(voltage_data)) * xincr

        return time_data, voltage_data
    
    @Instrument.device_checking
    def set_high_res_mode(self):
        self.send('ACQuire:MODe HIRes')
        self.state_changed.emit({'ACQUIRE_MODE' : 'HIRES'})

    @Instrument.device_checking
    def get_aquire_mode(self):
        return self.send('ACQuire:MODe?')
    
    @Instrument.device_checking
    def set_sample_mode(self):
        self.send('ACQuire:MODe SAMple')
        self.state_changed.emit({'ACQUIRE_MODE': 'SAMPLE'})
    
    @Instrument.device_checking
    def get_settings_from_device(self):
        message = {
            'VERT_SCALE': self.get_vertical_scale(),
            'VERT_POS': self.get_vertical_position(),
            'HOR_SCALE': self.get_horizontal_scale(),
            'HOR_POS': self.get_horizontal_position(),
            'ACQUIRE_MODE': self.get_aquire_mode(),
            'SELECT_CH': self.get_selected_channel(),
            'TERMINATIONS': self.get_all_terminations(),
            }
        
        message = {**message, **self.get_active_channels()} #TODO: add selected channel

        self.state_changed.emit(message)
               

    

    






    
        

