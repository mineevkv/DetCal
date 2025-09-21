from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QRadioButton
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
            's': 1, 'ms': 1e-3, 'us': 1e-6,
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
    
    osc_keys = {
            'HOR_scale' : ('hor_scale', 'ms')
        }

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
        self.settings_timer = QTimer()
        self.settings_timer.setInterval(3000) # 3 second
        self.settings_timer.timeout.connect(self.hide_settings_status)

        self.waiting_timer = QTimer()
        self.waiting_timer.setInterval(5000) # 5 second
        self.waiting_timer.timeout.connect(self.hide_waiting_status)

    def init_model_signals(self):
        self.model.data_changed.connect(self.data_signals_handler)
        self.model.equipment_changed.connect(self.equipment_signals_handler)
        self.model.settings_changed.connect(self.settings_signals_handler)
        self.model.meas_status.connect(self.meas_signals_handler)

    def init_view_signals(self):
        elem =self.view.meas.elem
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

        elem['precise_enabled'].stateChanged.connect(self.change_state_precise)
        elem['unlock_stop'].stateChanged.connect(self.unlock_stop_btn)

        for element in elem.values():
            if isinstance(element, QLineEdit):
                element.textChanged.connect(lambda _, object=element: self.line_edit_changed(object))
            elif isinstance(element, QRadioButton or QCheckBox):
                element.toggled.connect(lambda _, object=element: self.radiocheck_changed(object))
            elif isinstance(element, QCheckBox):
                element.toggled.connect(lambda _, object=element: self.radiocheck_changed(object))

    def refresh_obj_view(self, object_name):
        object_name.style().unpolish(object_name)
        object_name.style().polish(object_name)

    #Line edit handlers
    def line_edit_changed(self, object_name):
        object_name.setProperty('class', 'line_changed')
        self.refresh_obj_view(object_name)
        self.lock_start()


    def lock_start(self):
        elem = self.view.meas.elem
        self.view.meas.elem['btn_apply'].setEnabled(True)
        self.view.meas.elem['btn_start'].setEnabled(False)
        self.set_status_bar('Submit input parameters', 'WARNING')

    def unlock_start(self):
        elem = self.view.meas.elem
        elem['btn_apply'].setEnabled(False)
        elem['btn_start'].setEnabled(True)
        self.set_status_bar('Ready for measurement')

    def radiocheck_changed(self, object_name):
        elem = self.view.meas.elem
        if object_name is elem ['unlock_stop']:
            return
        object_name.setProperty('class', 'radiocheck_changed')
        self.refresh_obj_view(object_name)
        self.lock_start()
        

    def set_elements_unchanged(self):
        elem =self.view.meas.elem
        for element in elem.values():
            if isinstance(element, QLineEdit) or isinstance(element, QCheckBox) or isinstance(element, QRadioButton):
                element.setProperty('class', '')
                self.refresh_obj_view(element)
        self.unlock_start()

    def set_status_bar(self, text, status="INFO"):
        elem = self.view.meas.elem['status_bar_label']
        if status == "INFO":
            color = SURFGREEN
        elif status == "ERROR":
            color = RED
        elif status == "WARNING":
            color = YELLOW
        else:
            color = VIOLET

        elem.setText(text)
        elem.setStyleSheet(f"color: {color}")
        


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
        self.settings_timer.stop()
        elem = self.view.meas.elem['settings_status_label']
        elem.hide()
        
    def hide_waiting_status(self):
        self.waiting_timer.stop()
        elem = self.view.meas.elem['progress_label']
        elem.hide()
        
    def write_settings_to_model(self):
        settings = self.model.settings
        elem = self.view.meas.elem

        for key, param in self.gen_keys.items():
            settings[key] = self.write_gen_settings_to_model(param)

        for key, param in self.sa_keys.items():
            settings[key] = self.write_sa_settings_to_model(param)

        settings['Precise'] = elem['precise_enabled'].isChecked()

        for key, param in self.osc_keys.items():
            settings[key] = self.write_osc_settings_to_model(param)

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
             try:
                return float(self.view.meas.elem[f'{elem_key}_line'].text())* multiplier
             except ValueError:
                logger.warning(f"Invalid value for {elem_key}_line")
                raise
    
    def write_osc_settings_to_model(self, param):
        return self.write_sa_settings_to_model(param)


    def btn_load_settings_click(self):
        self.model.load_settings_from_file()
        self.change_settings_status('Settings loaded')

    def btn_set_default_click(self):
        self.model.load_default_settings()
        self.change_settings_status('Default settings')
    
    def btn_start_click(self):
        elem = self.view.meas.elem
        elem['unlock_stop'].setChecked(False)
        if self.model.start_measurement_process():
            elem['btn_save_result'].setEnabled(False)
            elem['btn_start'].hide()
            elem['btn_stop'].setEnabled(False)
            elem['btn_stop'].show()
            elem['progress_label'].setText('Waiting...')
            elem['progress_label'].show()
            self.set_status_bar('Measurement started')
        
    def btn_stop_click(self):
        elem = self.view.meas.elem
        elem['btn_stop'].setEnabled(False)
        elem['unlock_stop'].setChecked(False)
        self.model.stop_measurement_process()
        elem['progress_label'].setText('Stopped')
        self.waiting_timer.start()
    
    def btn_save_result_click(self):
        logger.debug('Save result')
        self.model.save_results()
        self.view.meas.elem['progress_label'].setText('Saved')
        self.view.meas.elem['progress_label'].show()
        self.waiting_timer.start()
  
    def btn_apply_click(self):
        logger.debug('Apply button clicked')
        try:
            self.write_settings_to_model()
            self.set_elements_unchanged()
            self.set_status_bar('Ready to measurement')
        except Exception as e:
            logger.error(f"Error applying settings: {e}")
            self.set_status_bar(f"Error applying settings: {e}", "ERROR")

    def str_to_bool(self, value):
        """Convert string to bool """
        if isinstance(value, str):
            value = value.lower()
            if value == 'true':
                return True
            elif value == 'false':
                return False
        return bool(value)

    def data_signals_handler(self, message):
        if 'data' in message:
            pass
        if 'point' in message:
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

    def update_osc_elem(self, value, param):
        self.update_sa_elem(value, param)

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
        is_checked = self.view.meas.elem['precise_enabled'].isChecked()
        self.enable_precise(is_checked)

    def enable_precise(self, state):
        self.view.meas.elem['precise_enabled'].setChecked(state)
        keys = ('span_precise_label', 'span_precise_line',
                'rbw_precise_label', 'rbw_precise_line',
                'vbw_precise_label', 'vbw_precise_line')

        for key in keys:
            self.view.meas.elem[key].setEnabled(state)

    def unlock_stop_btn(self):
        elem = self.view.meas.elem
        is_checked = elem['unlock_stop'].isChecked()
        elem['btn_stop'].setEnabled(is_checked)
        elem['unlock_stop'].setChecked(is_checked)


    def equipment_signals_handler(self, message):
        """Handle completion of SCPI-instrument objects initialization"""
        logger.debug('MeasController: equipment_changed_handler()')

        for instr, controller in (
            ('gen', GenController),
            ('sa', SAController),
            ('osc', OscController)
        ):
            if instr in message:
                try:
                    if hasattr(self.model, instr) and getattr(self.model, instr):
                        logger.debug(f'Create {controller.__name__}')
                        setattr(self, f'{instr}_controller',
                                controller(getattr(self.model, instr), getattr(self.view, instr)))
                except AttributeError as e:
                    logger.error(f"Failed to set instrument controllers: {e}")


    def settings_signals_handler(self, message):
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
        for key, param in self.osc_keys.items():
            if key in message:
                self.update_osc_elem(message[key], param)

        elem = self.view.meas.elem
        if "High_res" in message:
            elem['hight_res_box'].setChecked(message["High_res"])
        if "Impedance_50Ohm" in message:
            status = message["Impedance_50Ohm"]
            elem['rb_50ohm'].setChecked(status)
            elem['rb_meg'].setChecked(not status)
            
        if "Coupling_DC" in message:
            status = message["Coupling_DC"]
            elem['rb_dc'].setChecked(status)
            elem['rb_ac'].setChecked(not status)
        if 'Channel' in message:
            elem[f'rb_ch{message["Channel"]}'].setChecked(True)

        self.set_elements_unchanged()

    def meas_signals_handler(self, message):
        elem = self.view.meas.elem
        if 'Finish' in message:
            elem['btn_stop'].hide()
            elem['btn_start'].show()
            elem['btn_save_result'].setEnabled(True)
            elem['progress_label'].setText('Finished')
            elem.start()
        if 'Stop' in message:
            elem['btn_stop'].hide()
            elem['btn_start'].show()
            elem['btn_save_result'].setEnabled(True)


    def run(self):
        logger.debug('GUI running')
        self.view.show()