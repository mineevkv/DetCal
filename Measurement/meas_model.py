from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QFileDialog
from Instruments.Initializer import InstrumentInitializer

import os
import json
import numpy as np
import time

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
    settings_changed = pyqtSignal(dict)
    meas_status = pyqtSignal(str)
    settings_filename = 'meas_settings'
    settings_folder = 'Settings'
    settings = dict()
    
    def __init__(self):
        super().__init__()

        self.gen = None
        self.sa = None
        self.osc = None

        self.initializer = InstrumentInitializer()
        self.initializer.instr_list.connect(self.init_instruments)

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
            self.data_changed.emit({'Gen': gen})
        if sa is not None:
            self.sa = sa
            self.data_changed.emit({'SA': sa})
        if osc is not None:
            self.osc = osc
            self.data_changed.emit({'Osc': osc})


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
        filename, _ = QFileDialog.getOpenFileName(
            caption="Load settings file",
            directory=self.settings_folder,
            filter="JSON files (*.json)"
        )
        settings =  dict()
        if filename:
            try:
                with open(filename, 'r') as f:
                    settings = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load settings from {filename}: {e}")
        else:
            logger.warning(f"No file selected")
        
        return settings
    
    def save_settings(self):
        with open(f"{self.settings_folder}/{self.settings_filename}.json", 'w') as f:
            json.dump(self.settings, f, indent=4)
            self.settings_changed.emit(self.settings)

    def start_measurement_process(self):
        abort = False
        equipment = [self.gen, self.sa]
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

        frequencies = np.linspace(*self.settings['RF_frequencies'])
        levels = np.linspace(*self.settings['RF_levels'])

        self.setup_devices()
        

        self.gen.rf_on()

        for frequency in frequencies:
            if self.stop_requested:
                self.meas_status.emit('Stop')
                break

            self.set_wide_band()

            self.gen.set_frequency(frequency)
            self.sa.set_center_freq(frequency)
            self.gen.set_level(max(levels))

            time.sleep(0.1) # wait for frequency to be set
                
            self.sa.start_single_measurement()
            time.sleep(self.sa.get_sweep_time()*2 + 0.3) # wait till measurement is done
            

            if self.settings['Precise']:
                if self.stop_requested:
                    self.meas_status.emit('Stop')
                    break

                self.sa.find_peak_max()
                self.sa.set_center_freq(self.sa.get_peak_freq())
                self.set_narrow_band()
                time.sleep(0.1) # wait for frequency to be set

                self.sa.start_single_measurement()
                time.sleep(self.sa.get_sweep_time()*2 + 0.3) # wait till measurement is done         

            for level in reversed(levels): # TODO: fix reversed
                if self.stop_requested:
                    self.meas_status.emit('Stop')
                    break
                self.gen.set_level(level)
                time.sleep(0.1) # wait for frequency to be set
                
                self.sa.start_single_measurement()
                time.sleep(self.sa.get_sweep_time()*2 + 0.3) # wait till measurement is done

                spectrum_data = self.sa.get_trace_data()
                
                max_value = max(spectrum_data)
                mean_value = np.mean(spectrum_data)
                limit = mean_value + 6 # +6 dBm

                if max_value > limit:
                    point =  [frequency, level, max_value]
                    self.meas_data.append(point)
                    self.data_changed.emit({'point': point})
                else:
                    logger.warning(f"Measured signal at ({frequency} Hz, {level} dBm) is less than limit ({limit} dBm)")
        self.data_changed.emit({'data': self.meas_data})
        self.gen.rf_off()
        self.gen.set_min_level()

    def stop_measurement_process(self):
        self.stop_requested = True

    def save_results(self):
        filename, _ = QFileDialog.getSaveFileName(
            caption="Save results",
            directory=os.path.join('results.csv'),
            filter="CSV files (*.csv)"
        )
        if filename:
            np.savetxt(filename, self.meas_data, delimiter=',') # Frequency, Level, Value
            logger.info(f"Results saved to {filename}")
        else:
            logger.warning(f"No file selected")

    def setup_devices(self):
        self.gen.factory_preset()
        self.gen.set_min_level()

        self.sa.set_swept_sa()
        self.sa.set_ref_level(self.settings['REF_level'])
        self.sa.set_sweep_time(self.settings['SWEEP_time'])
        self.sa.set_sweep_points(self.settings['SWEEP_time'])
        self.sa.trace_clear_all()
        self.sa.set_format_trace_bin()

        #setup osc

        time.sleep(0.1)
        

    def set_wide_band(self):
        self.sa.set_span(self.settings['SPAN_wide'])
        self.sa.set_rbw(self.settings['RBW_wide'])
        self.sa.set_vbw(self.settings['VBW_wide'])

    def set_narrow_band(self):
        self.sa.set_span(self.settings['SPAN_narrow'])
        self.sa.set_rbw(self.settings['RBW_narrow'])
        self.sa.set_vbw(self.settings['VBW_narrow'])


    def meas_finish_handler(self):
        self.meas_status.emit('Finish')
        logger.info(f"Measurement finished")


        