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



class MDO34(Instrument):

    def __init__(self, ip, visa_usb):
        super().__init__(ip, visa_usb)

        self._selected_channel = 1

        self.type = 'Oscilloscope'
        # self.default_setup()

    def default_setup(self): 
        pass

    def channel_on(self, channel=None):
        if channel is None:
            channel=self._selected_channel

        send(self.instr, f'SELECT:CH{channel} ON')

    def channel_off(self, channel=None):
        if channel is None:
            channel=self._selected_channel

        send(self.instr, f'SELECT:CH{channel} OFF')

    def select_channel(self, channel=None):
        channel_map = {
            1: 'CH1',
            2: 'CH2', 
            3: 'CH3', 
            4: 'CH4'
        }
        
        reverse_map = {v: k for k, v in channel_map.items()}
        
        if channel in channel_map:
            self._selected_channel = channel
        elif channel in reverse_map:
            self._selected_channel = reverse_map[channel]
        else:
            logger.error(f"Unknown channel: {channel}")
            raise ValueError(f"Unknown channel: {channel}")
        
    def set_coupling(self, coupling='DC'):
        send(self.instr, f'CH{self._selected_channel}:COUP {coupling}')

    def set_y_scale(self, scale=1):
        """Vertical scale in voltages"""
        send(self.instr, f'CH{self._selected_channel}:SCALE {scale}')

    def set_y_offset(self, offset=0):
        """Vertical offset in voltages"""
        send(self.instr, f'CH{self._selected_channel}:OFFSET {offset}')

    def set_bandwidth(self, bandwidth='FULL'):
        """Low-pass bandwidth limit filter for channel"""
        send(self.instr, f'CH{self._selected_channel}:BANDWIDTH {bandwidth}')

    def set_horizontal_scale(self, scale='1V'):
        """Horizontal scale in seconds"""
        send(self.instr, f'HORIZONTAL:SCALE {scale}')

    def set_horizontal_position(self, position=0):
        send(self.instr, f'HORIZONTAL:POSITION {position}')

    def set_measurement_source(self, source):
        if source is None:
            source=self._selected_channel
        send(self.instr, f'MEASUREMENT:IMMED:SOURCE CH{self._selected_channel}')

    def set_measurement_type(self, type='AMPLITUDE'):
        send(self.instr, f'MEASUREMENT:IMMED:TYPE {type}')

    def set_trigger_type(self, type='EDGE'):
        send(self.instr, f'TRIGGER:A:TYPE {type}')

    def set_trigger_source(self, source=None):
        if source is None:
            source=self._selected_channel
        send(self.instr, f'TRIGGER:A:EDGE:SOURCE {source}')

    def set_trigger_level(self, level=0):
        send(self.instr, f'TRIGGER:A:LEVEL {level}')

    def set_50Ohm_termination(self):
        self.set_termination('FIFty')

    def set_1MOhm_termination(self):
        self.set_termination('MEG')

    def set_termination(self, termination):
        """FIFty|MEG"""
        send(self.instr, f'CH{self._selected_channel}:TERMINATION {termination}')

    def stop_after_sequence(self):
        send(self.instr, 'ACQUIRE:STOPAFTER SEQUENCE')

    def ready_for_acquisition(self):
        send(self.instr, 'ACQUIRE:STATE ON')

    def trigger_force(self):
        send(self.instr, 'TRIGger FORCe')

    def is_acquiring(self):
        response = bool(int(send_scpi_command(self.instr, 'ACQUIRE:STATE?')))
        return response
    
    def set_data_source(self,source=None):
        if source is None:
            source=self._selected_channel
        send(self.instr, f'DATA:SOURCE CH{source}')

    def set_data_points(self,points=1000):
        send(self.instr, 'DATA:START 1')
        send(self.instr, f'DATA:STOP {points}')

    def set_binary_data_format(self):
        send(self.instr, 'DATA:WIDTH 2') # 2 bytes per point
        send(self.instr, 'DATA:ENCDG RPBinary') # Signed integer binary

    def parse_wfmoutpre_response(self, response):
        """
            Parce responce from WFMOUTPRE
        """
        parts = response.strip().split(';')
        
        #TODO fix this code

        # Создаем словарь с параметрами
        params = {
            'BYT_NR': int(parts[0]),          # 2 - количество байт на точку
            'BIT_NR': int(parts[1]),          # 16 - количество бит на точку
            'ENCODING': parts[2],             # BINARY - кодирование
            'BN_FMT': parts[3],               # RP - формат данных
            'BYT_OR': parts[4],               # MSB - порядок байт
            'DESC': parts[5].strip('"'),      # "Ch4, DC coupling..." - описание
            'NR_PT': int(parts[6]),           # 10000 - количество точек
            'WFMTYPE': parts[7],              # Y - тип волны
            'X_DISPLAY_FORMAT': parts[8],     # LINEAR - формат отображения X
            'XUNIT': parts[9].strip('"'),     # "s" - единицы измерения X
            'XINCR': float(parts[10]),        # 1.0000E-6 - шаг по X (1 мкс)
            'XZERO': float(parts[11]),        # 0.0E+0 - начальное значение X
            'PT_OFF': int(parts[12]),         # 0 - смещение точек
            'YUNIT': parts[13].strip('"'),    # "V" - единицы измерения Y
            'YMULT': float(parts[14]),        # 15.6250E-6 - множитель Y (15.625 мкВ)
            'YZERO': float(parts[15]),        # 32.7680E+3 - нулевое значение Y (32.768 В)
            'YOFF': float(parts[16]),         # 0.0E+0 - смещение Y
            'HORIZ_UNIT': parts[17],          # TIME - единицы горизонтальной оси
            'VERT_UNIT': parts[18],           # ANALOG - единицы вертикальной оси
            'PROBECAL': float(parts[19]),     # 0.0E+0 - калибровка пробника
            'PROBEDEF': float(parts[20]),     # 0.0E+0 - дефолтное значение пробника
            'PROBESN': float(parts[21])       # 0.0E+0 - серийный номер пробника
        }
    
        return params

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

        ymult = float(send(self.instr,'WFMOUTPRE:YMULT?'))
        yzero = float(send(self.instr,'WFMOUTPRE:YZERO?'))
        yoff = float(send(self.instr,'WFMOUTPRE:YOFF?'))
        xincr = float(send(self.instr,'WFMOUTPRE:XINCR?'))
        xzero = float(send(self.instr,'WFMOUTPRE:XZERO?'))

        return ymult, yzero, yoff, xincr, xzero
    
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
    
    def set_high_res_mode(self):
        send(self.instr, 'ACQuire:MODe HIRes')
    
    def set_sample_mode(self):
        send(self.instr, 'ACQuire:MODe SAMple')
    




    
        

