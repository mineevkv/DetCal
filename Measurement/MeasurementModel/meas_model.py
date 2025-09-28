from PyQt6.QtCore import QObject, pyqtSignal
from Measurement.MeasurementModel.Initializer import InstrumentInitializer
from .file_manager import FileManager
from ..helper_functions import  get_s21, is_equal_frequencies
from Measurement.MeasurementModel.measurement_thread import MeasurementThread
from Measurement.MeasurementModel.devices_setup import DevicesSetup

from multipledispatch import dispatch
import numpy as np
import time

from System.logger import get_logger
logger = get_logger(__name__)


class MeasurementModel(QObject):
    data_changed = pyqtSignal(dict)  # Signal to notify data changes
    equipment_changed = pyqtSignal(dict) # Signal to notify initializing instruments
    settings_changed = pyqtSignal(dict) # Signal to notify settings changes
    s21_file_changed = pyqtSignal(dict) # Signal to notify S21 file uploading
    progress_status = pyqtSignal(str) # Signal to notify measurement progress status
    settings_filename = 'meas_settings'
    settings_folder = 'Settings'
    s21_folder = 'S21files'
    _settings = dict()
    s21_gen_det = None
    s21_gen_sa = None
    
    SA_TOLERANCE = 6 # SA measured level greater than noise level

    _meas_data = []

    

    def __init__(self):
        super().__init__()

        self.gen = None # Microwave generator
        self.sa = None # Spectrum analyzer
        self.osc = None # Oscilloscope

        self._offline_debug =  False # Set to True to simulate offline mode

        self.initializer = InstrumentInitializer()
        self.initializer.finished.connect(self.init_instruments)
        self.file_manager = FileManager(self)

    
    def offline_mode(self, mode: bool) -> bool:
        "Offline mode without instruments initializing"
        if mode:
            self._offline_debug = True
            self.progress_status.emit('OFFLINE')
        else:
            self._offline_debug = False

    def is_offline(self) -> bool:
        return self._offline_debug
        
        
    def instr_initialization(self) -> None:
        """Start the instrument initialization process"""
        if self.is_offline():
            logger.info("MeasModel init: Offline debug mode")
            return
        
        if not self.initializer.isRunning(): 
            self.initializer.start()

    def init_instruments(self, gen, sa, osc, error):
        """Handle completion of instrument initialization"""
        if error:
            logger.debug('MeasModel_init_complete with error:', error)
            return
        
        instruments = {
            'gen': gen,
            'sa': sa,
            'osc': osc,
        }
        for name, instr in instruments.items():
            if instr is not None:
                setattr(self, name, instr)
                logger.debug(f'MeasModel: init {self.__getattribute__(name)}')
                self.equipment_changed.emit({name: instr})


    def load_settings(self):
        self.file_manager.load_settings()
        self.file_manager.load_s21_files()


    def get_data_from_frequency(self, frequency):
        data = []
        for row in self._meas_data:
            if is_equal_frequencies(row[0], frequency):
                data.append(row)
        return data
    
    def start_measurement_process(self):
        """
        Measurement Initializations and preparations
        """
        abort = False
        equipment = [self.gen, self.sa, self.osc]
        for instr in equipment:
            if not instr.is_initialized():
                logger.warning(f"Instrument {instr.__class__.__name__} not initialized")
                abort = True

        if abort:
            logger.warning(f"Measurement aborted")
            return False
             
        self.meas_thread = MeasurementThread(self)
        self.meas_thread.finished_signal.connect(self.meas_finish_handler)
        self.meas_thread.start()
        return True

    def start_measurement_thread(self):
        """
        General measurement process.
        This method must be call from another thread
        """
        logger.info(f"Starting measurement")
        self.progress_status.emit('START')

        self._meas_data = []
        self._stop_requested = False

        freq_min, freq_max, freq_points = self._settings['RF_FREQUENCIES']
        level_min, level_max, level_points = self._settings['RF_LEVELS']

        frequencies = np.linspace(freq_min, freq_max, freq_points)
        levels = np.linspace(level_min, level_max, level_points)

        kwargs = {
            'gen': self.gen,
            'sa': self.sa,
            'osc': self.osc,
            'settings': self._settings
        }
        DevicesSetup.setup(**kwargs)
        self.measurement_loop(frequencies, levels) 
        self.data_changed.emit({'DATA': self._meas_data})


  
    def measurement_loop(self, frequencies, levels):
        max_len = len(frequencies)*len(levels)
        iter_obj = iter(range(0, max_len))

        self.gen_on()

        # Main measurement loop
        for frequency in frequencies:
            self.data_changed.emit({'FREQUENCY': frequency})
            if self.is_stop():
                break
            
            self.set_sa_wide_band()

            self.gen.set_frequency(frequency)
            self.sa.set_center_freq(frequency)
            self.gen.set_level(max(levels))

            time.sleep(0.1) # wait for frequency to be set
                
            self.sa.start_single_measurement()
            self.sa.delay_after_start()
            

            if self._settings['PRECISE']:
                if self.is_stop():
                        break

                self.sa.find_peak_max()
                self.sa.set_center_freq(self.sa.get_peak_freq())
                self.set_sa_narrow_band()
                time.sleep(0.1) # wait for frequency to be set

                self.sa.start_single_measurement()
                self.sa.delay_after_start()

            for level in reversed(levels): # TODO: fix reversed
                logger.debug(f"Frequency: {frequency/1e6:.2f} MHz; Level: {level:.2f} dBm")
                self.emit_progress(iter_obj, max_len)
                if self.is_stop():
                        break
                
                self.gen.set_level(level)

                sa_data, osc_data = self.single_measurement()
                mean_osc_value = self.osc_voltage_refinement(osc_data)
                max_sa_value = self.sa_level_checking(sa_data)

                if max_sa_value:
                    point =  [frequency, level, max_sa_value, mean_osc_value]
                    self._meas_data.append(point)
                    self.data_changed.emit({'POINT': point})
                else:
                    logger.warning(f"Measured signal at ({frequency} Hz, {level} dBm) is less than limit ({self.SA_TOLERANCE} dBm)")

        self.gen_off()
        self.emit_progress(100)
    
    @dispatch(int)
    def emit_progress(self, value):
        self.progress_status.emit({'PROGRESS':value})

    @dispatch(object, int)
    def emit_progress(self, iter_obj, max_len):
        value = int((next(iter_obj)/max_len)*100)
        self.progress_status.emit({'PROGRESS':value})

    def is_stop(self):
        """Check if stop is requested and emit status if so"""
        if self.stop_requested:
            self.progress_status.emit('STOP')
            return True
        return False
    
    def stop_measurement_process(self):
        self.stop_requested = True

    def single_measurement(self):
        # Start measurement
        self.osc.ready_for_acquisition()
        time.sleep(0.2)
        
        self.sa.start_single_measurement()
        self.sa.delay_after_start()
        self.osc.trigger_force()
            
        while self.osc.is_acquiring():
            if self.is_stop():
                break # Waiting for finish measurement
            time.sleep(0.1)

        spectrum_data = self.sa.get_trace_data()
        _, osc_data = self.osc.get_waveform_data()
        return spectrum_data, osc_data
        
    def osc_voltage_refinement(self, osc_data):
        mean_osc_value = np.mean(osc_data)

        while self.check_osc_range(mean_osc_value):
            if self.is_stop():
                break

            self.osc.ready_for_acquisition()
            time.sleep(0.2)
            self.osc.trigger_force() # Start measurement

            while self.osc.is_acquiring(): # Waiting for finish measurement
                if self.is_stop():
                    break 
                time.sleep(0.1)

            _, osc_data = self.osc.get_waveform_data()
            mean_osc_value = np.mean(osc_data)

        return mean_osc_value
    
    def sa_level_checking(self, spectrum_data):
        max_value = max(spectrum_data)
        mean_value = np.mean(spectrum_data)
        limit = mean_value + self.SA_TOLERANCE # +6 dBm

        if max_value > limit:
            return max_value
        else:
            return 0
        
    def gen_on(self):
        self.gen.rf_on()
        time.sleep(0.1)

    def gen_off(self):
        self.gen.rf_off()
        self.gen.set_min_level()

    def recalc_data(self):
        """Recalculate data via measured S21 parameters"""
        recalc_data = []
        for point in self._meas_data:
            frequency = point[0]
            level = point[1]
            sa_level = point[2]
            osc_voltage = point[3]
            s21_gen_sa = get_s21(frequency, self.s21_gen_sa)
            s21_gen_det = get_s21(frequency, self.s21_gen_det)
            det_level = (sa_level + s21_gen_sa) - s21_gen_det

            recalc_point = [frequency, level, sa_level, osc_voltage, s21_gen_sa, s21_gen_det, det_level]
            recalc_data.append(recalc_point)

        self.data_changed.emit({'RECALC_DATA': recalc_data})
        self._meas_data = recalc_data


    def set_sa_wide_band(self):
        self.sa.set_span(self._settings['SPAN_WIDE'])
        self.sa.set_rbw(self._settings['RBW_WIDE'])
        self.sa.set_vbw(self._settings['VBW_WIDE'])

    def set_sa_narrow_band(self):
        self.sa.set_span(self._settings['SPAN_NARROW'])
        self.sa.set_rbw(self._settings['RBW_NARROW'])
        self.sa.set_vbw(self._settings['VBW_NARROW'])


    def check_osc_range(self, value):
        """
        Check if oscilloscope vertical scale needs adjustment based on measured value.
        Returns True if scale was changed, False otherwise.
        """
        current_scale = self.osc.get_vertical_scale()
        vertical_map = self.osc.vertical_map
        current_idx = vertical_map.index(current_scale)
        
        
        if value > 3 * current_scale:
            # Move to next higher scale if available
            if  current_idx < len(vertical_map)-1:  # Not already at the highest scale
                new_scale = vertical_map[current_idx + 1]
                self.osc.set_vertical_scale(new_scale)
                logger.debug(f"Scale increased: {current_scale} -> {new_scale} (value: {value:.3f}V)")
                return True
        elif value < 1 * current_scale:
            # Move to next lower scale if available
            if current_idx > 0: 
                new_scale = vertical_map[current_idx - 1]
                self.osc.set_vertical_scale(new_scale)
                logger.debug(f"Scale decreased: {current_scale} -> {new_scale} (value: {value:.3f}V)")
                return True
        
        return False

   
    def meas_finish_handler(self):
        self.progress_status.emit('FINISH')
        logger.info(f"Measurement finished")


        