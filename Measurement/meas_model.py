from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QFileDialog
from Instruments.Initializer import InstrumentInitializer
from Instruments.rsa5000vna_parcer import RSA506N_S21_Parser
from .helper_functions import read_csv_file

import os
import json
import numpy as np
import time
import csv
from pathlib import Path

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementThread(QThread):
    """Set measurement process in a separate thread"""
    finished_signal = pyqtSignal()
    
    def __init__(self, meas_model):
        super().__init__()
        self.parent = meas_model
        
    def run(self):
        try:
            self.parent.start_measurement()  
        except Exception as e:
            logger.error(f"Measurement process error: {e}")
        finally:
            self.finished_signal.emit()

class MeasurementModel(QObject):
    data_changed = pyqtSignal(dict)  # Signal to notify data changes
    equipment_changed = pyqtSignal(dict)
    settings_changed = pyqtSignal(dict)
    s21_file_changed = pyqtSignal(dict)
    meas_status = pyqtSignal(str)
    progress_bar = pyqtSignal(int)
    settings_filename = 'meas_settings'
    settings_folder = 'Settings'
    s21_folder = 'S21files'
    settings = dict()
    s21_gen_det = None
    s21_gen_sa = None
    
    meas_data = []

    def __init__(self):
        super().__init__()

        self.gen = None
        self.sa = None
        self.osc = None

        self.initializer = InstrumentInitializer()
        self.initializer.finished.connect(self.init_instruments)

    def start_initialization(self):
        """Start the instrument initialization process"""
        if not self.initializer.isRunning():
            self.initializer.start()

    def init_instruments(self, gen, sa, osc, error):
        """Handle completion of instrument initialization"""
        if error:
            logger.debug('MeasModel_init_complete with error:', error)
            return
        
        if gen is not None:
            self.gen = gen
            logger.debug(f'MeasModel: init {self.gen}')
            self.equipment_changed.emit({'gen': gen})
        if sa is not None:
            self.sa = sa
            logger.debug(f'init_sa: {self.sa}')
            self.equipment_changed.emit({'sa': sa})
        if osc is not None:
            self.osc = osc
            logger.debug(f'init_osc: {self.osc}')
            self.equipment_changed.emit({'osc': osc})


        # TODO: emit the data_changed signal with the initialized instruments
        
    def offline_mode(self, mode):
        if mode:
            self.initializer.offline_debug = True
        else:    
            self.initializer.offline_debug = False

    def load_settings_from_file(self):
        logger.debug('MeasModel: load settings from file')
        settings = self.open_settings_file()
        if not settings == {}:
            self.settings = settings
            self.settings_changed.emit(self.settings)

    def load_settings(self, default=False):
        type = 'default ' if default else ''
        logger.debug(f"MeasModel: load {type}settings")
        settings =  dict()
        path = f"{self.settings_folder}/{self.settings_filename}{'_default' if default else ''}.json"
        try:
            with open(path, 'r') as f:
                settings = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {type}settings from {path}: {e}")

        if not settings == {}:
            self.settings = settings
            self.settings_changed.emit(self.settings) 

    def load_default_settings(self):
        self.load_settings(default=True)
 

    def open_settings_file(self):
        path, _ = QFileDialog.getOpenFileName(
            caption="Load settings file",
            directory=self.settings_folder,
            filter="JSON files (*.json)"
        )
        settings =  dict()
        if path:
            try:
                with open(path, 'r') as f:
                    settings = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load settings from {path}: {e}")
        else:
            logger.warning(f"No file selected")
        
        return settings
    
    def save_settings(self):
        with open(f"{self.settings_folder}/{self.settings_filename}.json", 'w') as f:
            json.dump(self.settings, f, indent=4)
            self.settings_changed.emit(self.settings)

    def load_s21_gen_sa(self):
        try:
            filename = 's21_gen_sa.trs'        
            self.s21_gen_sa = self.parse_s21_file(filename)
            self.s21_file_changed.emit({'s21_gen_sa' : filename})
        except Exception as e:
            logger.warning(f"Failed to load S21 file: {e}")

    def load_s21_gen_det(self):
        try:
            filename = 's21_gen_det.trs'        
            self.s21_gen_det = self.parse_s21_file(filename)
            self.s21_file_changed.emit({'s21_gen_det' : filename})
        except Exception as e:
            logger.warning(f"Failed to load S21 file: {e}")

    def parse_s21_file(self, filename):
        parser = RSA506N_S21_Parser(os.path.join(self.s21_folder, filename))
        data = parser.parse_file()
        return (data['frequency'], data['magnitude_db'])
    
    def get_data_from_frequency(self, frequency):
        data = []
        for row in self.meas_data:
            if self.equal_frequencies(row[0], frequency):
                data.append(row)
        return data

    def equal_frequencies(self, frequency1, frequency2):
        return abs(frequency1 - frequency2) < 0.01e6
    
    def start_measurement_process(self):
        abort = False
        equipment = [self.gen] #TODO: fix equipment
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

    def start_measurement(self):
        logger.info(f"Starting measurement")
        self.meas_status.emit('Start')

        self.meas_data = []
        self.stop_requested = False

        freq_min, freq_max, freq_points = self.settings['RF_frequencies']
        level_min, level_max, level_points = self.settings['RF_levels']
        
        if freq_max < 1e-9:
            freq_max = freq_min
            freq_points = 1

        frequencies = np.linspace(freq_min, freq_max, freq_points)
        levels = np.linspace(level_min, level_max, level_points)

        self.setup_devices()
        
        self.gen.rf_on()

        self.measurement_loop(frequencies, levels)
        self.progress_bar.emit(100)
        self.data_changed.emit({'data': self.meas_data})
        self.gen.rf_off()
        self.gen.set_min_level()


  
    def measurement_loop(self, frequencies, levels):
        max_len = len(frequencies)*len(levels)
        iter_obj = iter(range(0, max_len))

        # Main measurement loop
        for frequency in frequencies:
            self.data_changed.emit({'frequency': frequency})
            if self.is_stop():
                break
            
            self.set_wide_band()

            self.gen.set_frequency(frequency)
            self.sa.set_center_freq(frequency)
            self.gen.set_level(max(levels))

            time.sleep(0.1) # wait for frequency to be set
                
            self.sa.start_single_measurement()
            self.sa.delay_after_start()
            

            if self.settings['Precise']:
                if self.is_stop():
                        break

                self.sa.find_peak_max()
                self.sa.set_center_freq(self.sa.get_peak_freq())
                self.set_narrow_band()
                time.sleep(0.1) # wait for frequency to be set

                self.sa.start_single_measurement()
                self.sa.delay_after_start()

            for level in reversed(levels): # TODO: fix reversed
                value = int((next(iter_obj)/max_len)*100)
                self.progress_bar.emit(value)
                logger.debug(f"Frequency: {frequency/1e6:.2f} MHz; Level: {level:.2f} dBm")

                if self.is_stop():
                        break
                
                self.gen.set_level(level)
                self.osc.ready_for_acquisition()
                time.sleep(0.2)
                # Start measurement
                self.sa.start_single_measurement()
                self.sa.delay_after_start()
                self.osc.trigger_force()
                 
                while self.osc.is_acquiring(): # Waiting for finish measurement
                    time.sleep(0.1)

                spectrum_data = self.sa.get_trace_data()
                _, osc_data = self.osc.get_waveform_data()
                mean_osc_value = np.mean(osc_data)

                while self.check_osc_range(mean_osc_value):
                    if self.is_stop():
                        break

                    self.osc.ready_for_acquisition()
                    time.sleep(0.2)
                    self.osc.trigger_force() # Start measurement

                    while self.osc.is_acquiring(): # Waiting for finish measurement
                        time.sleep(0.1)

                    _, osc_data = self.osc.get_waveform_data()
                    mean_osc_value = np.mean(osc_data)

                # TODO: measurement from new Y scale
                # max_value = 1
                # limit = 0
                max_value = max(spectrum_data)
                mean_value = np.mean(spectrum_data)
                limit = mean_value + 6 # +6 dBm

                if max_value > limit:
                    point =  [frequency, level, max_value, mean_osc_value]
                    self.meas_data.append(point)
                    self.data_changed.emit({'point': point})
                else:
                    logger.warning(f"Measured signal at ({frequency} Hz, {level} dBm) is less than limit ({limit} dBm)")
    
    # decorator
    def is_stop(self):
        """Check if stop is requested and emit status if so"""
        if self.stop_requested:
            self.meas_status.emit('Stop')
            return True
        return False
    
    def stop_measurement_process(self):
        self.stop_requested = True

    def save_results(self):
        filename, _ = QFileDialog.getSaveFileName(
            caption="Save results",
            directory=os.path.join('results.csv'),
            filter="CSV files (*.csv)"
        )
        if filename:
            file_header = 'Gen Frequency (Hz), Gen Level (dBm), SA Level (dBm), Osc Voltage (V), S21 Gen-Sa (dB), S21 Gen-Det (dB), Det Level (dBm)'
            np.savetxt(filename, self.meas_data, delimiter=',', header=file_header) # Frequency, Level, Value, Mean Osc Value
            logger.info(f"Results saved to {filename}")
        else:
            logger.warning(f"No file selected")

    def recalc_data(self):
        """Recalculate data via measured S21 parameters"""
        recalc_data = []
        for point in self.meas_data:
            frequency = point[0]
            level = point[1]
            sa_level = point[2]
            osc_voltage = point[3]
            s21_gen_sa = self.get_s21(frequency, self.s21_gen_sa)
            s21_gen_det = self.get_s21(frequency, self.s21_gen_det)
            det_level = (sa_level + s21_gen_sa) - s21_gen_det

            recalc_point = [frequency, level, sa_level, osc_voltage, s21_gen_sa, s21_gen_det, det_level]
            recalc_data.append(recalc_point)

        self.data_changed.emit({'recalc_data': recalc_data})
        self.meas_data = recalc_data

    def get_s21(self, frequency, s21):
        pass
    

    def setup_devices(self):
        self.gen.factory_preset()
        self.gen.set_min_level()

        self.sa.set_swept_sa()
        self.sa.set_ref_level(self.settings['REF_level'])
        self.sa.set_sweep_time(self.settings['SWEEP_time'])
        self.sa.set_sweep_points(self.settings['SWEEP_points'])
        self.sa.trace_clear_all()
        self.sa.set_format_trace_bin()

        self.osc.reset()
        time.sleep(2)
        self.osc.get_settings_from_device()

        self.osc.channel_off(1) # CH1 is default channel
        channel = self.settings['Channel']
        self.osc.select_channel(channel)
        if self.settings['Impedance_50Ohm']:
            self.osc.set_50Ohm_termination()
        if self.settings['Coupling_DC']:
            self.osc.set_coupling('DC')
        self.osc.set_vertical_scale(1) # 1V/div
        self.osc.set_vertical_position(0)
        self.osc.channel_on(channel)
        self.osc.set_bandwidth('FULL')
        if self.settings['High_res']:
            self.osc.set_high_res_mode()
        self.osc.set_horizontal_scale(self.settings['HOR_scale'])
        self.osc.set_horizontal_position(0)

        self.osc.set_measurement_source(channel)
        self.osc.set_measurement_type('AMPLITUDE')

        self.osc.set_trigger_type('EDGE')
        self.osc.set_trigger_source(channel)
        self.osc.set_trigger_level(0)

        self.osc.stop_after_sequence()
        self.osc.set_data_source(channel)
        self.osc.set_data_points(10000)
        self.osc.set_binary_data_format()

        time.sleep(0.1)
        

    def set_wide_band(self):
        self.sa.set_span(self.settings['SPAN_wide'])
        self.sa.set_rbw(self.settings['RBW_wide'])
        self.sa.set_vbw(self.settings['VBW_wide'])

    def set_narrow_band(self):
        self.sa.set_span(self.settings['SPAN_narrow'])
        self.sa.set_rbw(self.settings['RBW_narrow'])
        self.sa.set_vbw(self.settings['VBW_narrow'])


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
        self.meas_status.emit('Finish')
        logger.info(f"Measurement finished")


        