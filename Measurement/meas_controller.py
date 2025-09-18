from PyQt6.QtCore import QObject, QTimer
from .meas_model import MeasurementModel
from GUI.main_window import MainWindow
from .gen_controller import GenController
from .sa_controller import SAController
from .osc_controller import OscController

from GUI.palette import *

from System.logger import get_logger
logger = get_logger(__name__)




class MeasurementController(QObject):

    units = {'Hz' : 1, 'kHz': 1e3, 'MHz': 1e6, 'GHz': 1e9,
            'dBm': 1, 'dB': 1,
            'point': 1
            }
    
    # Key from json settings file : (name of lineEdit element, unit)
    gen_keys = { 
            'RF_frequencies' : ('freq', 'MHz'),
            'RF_levels' : ('level', 'dBm')
        }

    sa_keys = {
            'SPAN_wide' : ('span', 'MHz'),
            'RBW_wide' : ('rbw', 'kHz'),
            'VBW_wide' : ('vbw', 'kHz'),
            'REF_level' : ('ref_level', 'dB'),
            'SWEEP_points' : ('sweep_points', 'point'),
            'SPAN_narrow' : ('span_precise', 'MHz'),
            'RBW_narrow' : ('rbw_precise', 'kHz'),
            'VBW_narrow' : ('vbw_precise', 'kHz')
        }
    
    osc_keys = {}

    def __init__(self):
        super().__init__()

        self.model = MeasurementModel()
        self.view = MainWindow()

        self.connect_signals() # Must be before initialization
        self.model.offline_mode(0) # Set to True for offline testing without instruments
        self.model.start_initialization()
        self.model.load_settings()

        # self.connect_signals()
        # self.update_view()


    def connect_signals(self):
        self.init_model_signals()
        self.init_view_signals()
        self.init_timers_signals()
        # self.instruments_signals()




    def init_timers_signals(self):
        self.init_timer = QTimer()
        self.init_timer.setInterval(500) # 0.5 second
        self.init_timer.timeout.connect(self.close_init_window)

        self.settings_timer = QTimer()
        self.settings_timer.setInterval(3000) # 3 second
        self.settings_timer.timeout.connect(self.hide_settings_status)

    def init_model_signals(self):
        self.model.initializer.progress.connect(self.update_init_progress)
        self.model.initializer.finished.connect(self.initialization_complete)
        self.model.data_changed.connect(self.data_changed_handler)
        self.model.settings_changed.connect(self.settings_changed_handler)

    def init_view_signals(self):
        keys = ('save_settings',
                'load_settings',
                'set_default',
                'start',
                'stop',
                'save_result',
                'apply'
        )
        
        for key in keys:
                self.btn_clicked_connect(key, getattr(self, f'btn_{key}_click', None))

        self.view.meas.elem['precise_enabled'].stateChanged.connect(self.change_state_precise)

    def btn_clicked_connect(self,btn_name, btn_handler):
        if btn_handler is not None:
            self.view.meas.elem[f'btn_{btn_name}'].clicked.connect(btn_handler)


    def btn_save_settings_click(self):
        self.write_settings_to_model()
        self.model.save_settings()
        self.change_settings_status('Settings saved')

    def change_settings_status(self,status):
        elem = self.view.meas.elem['settings_status_label']
        elem.setText(status)
        elem.show()

        self.settings_timer.start()

    def hide_settings_status(self):
        elem = self.view.meas.elem['settings_status_label']
        elem.hide()

        self.settings_timer.stop()
        
        

    def write_settings_to_model(self):

        settings = self.model.settings
        elem = self.view.meas.elem

        for key, param in self.gen_keys.items():
            settings[key] = self.write_gen_settings_to_model(param)

        for key, param in self.sa_keys.items():
            settings[key] = self.write_sa_settings_to_model(param)

        settings['Precise'] = elem['precise_enabled'].isChecked()

    def write_gen_settings_to_model(self, param):
        elem_key, unit = param
        if unit in self.units:
             multiplier = self.units[unit]

        elem = self.view.meas.elem
        value_min = float(elem[f'{elem_key}_min_line'].text()) * multiplier
        value_max = float(elem[f'{elem_key}_max_line'].text()) * multiplier
        points = int(elem[f'{elem_key}_points_line'].text())

        return value_min, value_max, points

    def write_sa_settings_to_model(self, param):
        elem_key, unit = param
        if unit in self.units:
             multiplier = self.units[unit]
        return float(self.view.meas.elem[f'{elem_key}_line'].text()) * multiplier


    def btn_load_settings_click(self):
        self.model.load_settings_from_file()
        self.change_settings_status('Settings loaded')

    def btn_set_default_click(self):
        self.model.load_default_settings()
        self.change_settings_status('Default settings')
    
    def btn_start_click(self):
        self.model.start_measurement_process()
        
    
    def btn_stop_click(self):
            pass
    
    def btn_save_result_click(self):
            pass
    
    def btn_apply_click(self):
            pass
    

    def settings_changed_handler(self, message):
        # Gen settings
        for key, param in self.gen_keys.items():
            if key in message:
                self.update_gen_elem(message, key, param)

        # SA settings
        for key, param in self.sa_keys.items():
            if key in message:
                self.update_sa_elem(message[key], param)

        if 'Precise' in message:
            self.enable_precise(self.str_to_bool(message['Precise']))

        # Osc settings


    def str_to_bool(self, value):
        """Convert string to bool """
        if isinstance(value, str):
            value = value.lower()
            if value == 'true':
                return True
            elif value == 'false':
                return False
        return bool(value)

    def data_changed_handler(self, message):
        pass


    def update_gen_elem(self, message, mes_key, param):
        elem_key, unit = param
        if unit in self.units:
             dev = self.units[unit]

        value_min, value_max, points = message.get(f'{mes_key}', (None, None, None))
        elem = self.view.meas.elem
        elem[f'{elem_key}_min_line'].setText(self.remove_zeros(value_min/dev))
        elem[f'{elem_key}_max_line'].setText(self.remove_zeros(value_max/dev))
        elem[f'{elem_key}_points_line'].setText(self.remove_zeros(points))

    def update_sa_elem(self, value, param):
        elem_key, unit = param
        if unit in self.units:
             dev = self.units[unit]
        self.view.meas.elem[f'{elem_key}_line'].setText(self.remove_zeros(value/dev))

    def remove_zeros(self, input_string):
        """Remove trailing zeros from a string containing a decimal point"""
        if input_string is None:
            return
        
        input_string = str(input_string)
        if '.' in input_string:
            input_list = input_string.split('.')
            input_list[1] = input_list[1].rstrip('0')
            if input_list[1] == '':
                return input_list[0]
            input_string = '.'.join(input_list)
            
        return input_string
    
    def change_state_precise(self):
        """Precise checkbox handler"""
        if self.view.meas.elem['precise_enabled'].isChecked():
            self.enable_precise(True)
        else:
            self.enable_precise(False)

    def enable_precise(self, state):
        self.view.meas.elem['precise_enabled'].setChecked(state)
        keys = ('span_precise_label', 'span_precise_line',
                'rbw_precise_label', 'rbw_precise_line',
                'vbw_precise_label', 'vbw_precise_line')

        for key in keys:
            self.view.meas.elem[key].setEnabled(state)

    def update_init_progress(self, message):
        """Update progress message"""
        self.append_init_text(f"progress: {message}")
        logger.info(message)

    def initialization_complete(self, error):
        """Handle completion of instrument initialization"""

        if error:
            message = f"Instrument initialization failed: {str(error)}"
            logger.error(message)
            self.append_init_text(message, status="ERROR")
            self.view.init.status_label.setText("No instruments")
            self.view.init.progress_bar.setRange(0, 100)
            self.view.init.progress_bar.setValue(100)            
            self.init_timer.setInterval(100) # 0.1 seconds
            self.init_timer.start()
            return
        
        message = 'Initialization complete'
        self.append_init_text(message)
        logger.info(message)
        
        self.init_timer.start()

    def close_init_window(self):
        self.init_timer.stop()
        self.view.instr_sheet_show()
        self.view.init.cleanup()

        self.set_instr_controllers()
    
    def set_instr_controllers(self):
        try:
            if hasattr(self.model, 'gen') and self.model.gen:
                self.gen_controller = GenController(self.model.gen, self.view.gen)
            if hasattr(self.model, 'sa') and self.model.sa:
                self.sa_controller = SAController(self.model.sa, self.view.sa)
            if hasattr(self.model, 'osc') and self.model.osc:
                self.osc_controller = OscController(self.model.osc, self.view.osc)
        except AttributeError as e:
            logger.error(f"Failed to set instrument controllers: {e}")


    def append_init_text(self, text, status="INFO"):

        if status == "INFO":
            color = SURFGREEN
        elif status == "ERROR":
            color = RED
        elif status == "WARNING":
            color = YELLOW
        else:
            color = VIOLET

        self.view.init.text_browser.append(f"<span style='color: {color}'>{text}</span>")

    def run(self):
        logger.debug('GUI running')
        self.view.show()