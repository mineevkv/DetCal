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
            'dBm': 1,
            'point': 1
            }


    def __init__(self):
        super().__init__()

        self.model = MeasurementModel()
        self.view = MainWindow()

        self.connect_signals() # Must be before initialization
        self.model.offline_mode(1) # Set to True for offline testing without instruments
        self.model.start_initialization()

        # self.connect_signals()
        # self.update_view()


    def connect_signals(self):
        self.init_model_signals()
        self.init_view_signals()
        self.init_timer_signals()
        # self.instruments_signals()




    def init_timer_signals(self):
        self.init_timer = QTimer()
        self.init_timer.timeout.connect(self.close_init_window)

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

    def btn_clicked_connect(self,btn_name, btn_handler):
        if btn_handler is not None:
            self.view.meas.elem[f'btn_{btn_name}'].clicked.connect(btn_handler)

    def btn_save_settings_click(self):
            pass

    def btn_load_settings_click(self):
        self.model.load_settings_from_file()

    def btn_set_default_click(self):
            pass
    
    def btn_start_click(self):
            pass
    
    def btn_stop_click(self):
            pass
    
    def btn_save_result_click(self):
            pass
    
    def btn_apply_click(self):
            pass
    

    def settings_changed_handler(self, message):
        # elem = self.view.elem
        # Updating current measurement parameters
        gen_keys = {
            'RF_frequencies' : ('freq', 'MHz'),
            'RF_levels' : ('level', 'dBm')
        }

        for key, param in gen_keys.items():
            if key in message:
                self.update_gen_elem(message, key, param)

        sa_keys = {
            'SPAN' : ('span', 'MHz'),
            'RBW_wide' : ('rbw', 'kHz'),
            'VBW_wide' : ('vbw', 'kHz'),
            'REF_level' : ('ref_level', 'dBm'),
            'SWEEP_points' : ('sweep_points', 'point'),
            'SPAN_narrow' : ('span_precise', 'MHz'),
            'RBW_narrow' : ('rbw_precise', 'kHz'),
            'VBW_narrow' : ('vbw_precise', 'kHz')
        }

        for key, param in sa_keys.items():
            if key in message:
                self.update_sa_elem(message[key], param)
        # self.update_sa_elem('span', message['SPAN'])
        


    def data_changed_handler(self, message):
        pass


    def update_gen_elem(self, message, mes_key, param):
        elem_key, unit = param
        if unit in self.units:
             dev = self.units[unit]

        value_min, value_max, points = message.get(f'{mes_key}', (None, None, None))
        self.view.meas.elem[f'{elem_key}_min_line'.format(elem_key)].setText(str(value_min/dev))
        self.view.meas.elem[f'{elem_key}_max_line'.format(elem_key)].setText(str(value_max/dev))
        self.view.meas.elem[f'{elem_key}_points_line'.format(elem_key)].setText(str(points))

    def update_sa_elem(self, value, param):
        elem_key, unit = param
        if unit in self.units:
             dev = self.units[unit]
        self.view.meas.elem[f'{elem_key}_line'].setText(str(value/dev))

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
        self.init_timer.setInterval(500) # 0.5 second
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