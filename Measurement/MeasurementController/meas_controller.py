from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QRadioButton
from ..meas_model import MeasurementModel
from GUI.main_window import MainWindow
from ..gen_controller import GenController
from ..sa_controller import SAController
from ..osc_controller import OscController
from ..helper_functions import remove_zeros, str_to_bool, refresh_obj_view, is_equal_frequencies
from .status_bar_controller import StatusBarController
from .write_settings import WriteSettings
from .signals_handlers import SettingsSignalHandler
from Documentations.protocol_creator import MeasurementProtocol
import csv
import json
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

        self.init_connect_signals() # Must be before initialization
        self.init_view_handlers()

        self.model.offline_mode(0) # Set to True for offline testing without instruments
        self.model.start_initialization()
        self.model.load_settings()
        self.model.load_s21_files()


    def init_connect_signals(self):
        self.init_model_signals()
        self.init_view_signals()
        self.init_timers_signals()


    def init_view_handlers(self):
        self.status_bar = StatusBarController(self.view.meas.elem['status_bar_label'])

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
        self.model.progress_bar.connect(self.status_bar_signals_handler)
        self.model.s21_file_changed.connect(self.s21_signals_handler)

    def init_view_signals(self):
        #Measurement sheet
        elem =self.view.meas.elem
        keys = ('save_settings',
                'load_settings',
                'set_default',
                'start',
                'stop',
                'save_result',
                'load_s21_gen_sa',
                'load_s21_gen_det',
                'apply'
        )
        
        for key in keys:
                self.btn_clicked_connect(key, getattr(self, f'btn_{key}_click', None))

        elem['precise_enabled'].stateChanged.connect(self.change_state_precise)
        elem['unlock_stop'].stateChanged.connect(self.unlock_stop_btn)
        elem['recalc_att'].stateChanged.connect(self.change_state_recalc)

        for element in elem.values():
            if isinstance(element, QLineEdit):
                element.textChanged.connect(lambda _, object=element: self.line_edit_changed(object))
            elif isinstance(element, QRadioButton or QCheckBox):
                element.toggled.connect(lambda _, object=element: self.radiocheck_changed(object))
            elif isinstance(element, QCheckBox):
                element.toggled.connect(lambda _, object=element: self.radiocheck_changed(object))

        #Infographic
        elem =self.view.plot.elem
        elem['freq_cobmo'].currentTextChanged.connect(self.selector_handler)
        elem['btn_protocol'].clicked.connect(self.btn_protocol_click)

   
    def selector_handler(self):
        selected_freq = self.view.plot.get_current_frequency()
        if selected_freq is None:
            return
        data = self.model.get_data_from_frequency(selected_freq)
        self.view.plot.plot_data_from_frequency(data)


    #Line edit handlers
    def line_edit_changed(self, object_name):
        object_name.setProperty('class', 'line_changed')
        refresh_obj_view(object_name)
        self.lock_start_btn()


    def lock_start_btn(self):
        elem = self.view.meas.elem
        elem['btn_apply'].setEnabled(True)
        elem['btn_start'].setEnabled(False)
        self.status_bar.warning('Submit input parameters')

    def unlock_start_btn(self):
        elem = self.view.meas.elem
        elem['btn_apply'].setEnabled(False)
        elem['btn_start'].setEnabled(True)
        self.status_bar.info('Ready to measurement')

    def radiocheck_changed(self, object_name):
        elem = self.view.meas.elem
        if object_name is elem ['unlock_stop']:
            return
        object_name.setProperty('class', 'radiocheck_changed')
        refresh_obj_view(object_name)
        self.lock_start_btn()
        
    def set_elements_unchanged(self):
        elem =self.view.meas.elem
        for element in elem.values():
            if isinstance(element, QLineEdit) or isinstance(element, QCheckBox) or isinstance(element, QRadioButton):
                element.setProperty('class', '')
                refresh_obj_view(element)
        self.unlock_start_btn()

    def btn_clicked_connect(self,btn_name, btn_handler):
        if btn_handler is not None:
            self.view.meas.elem[f'btn_{btn_name}'].clicked.connect(btn_handler)

    def btn_save_settings_click(self):
        WriteSettings.view_to_model(self)
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
        elem = self.view.meas.elem
        elem['progress_label'].setText('')

    def btn_load_settings_click(self):
        self.view.plot.clear_selector()
        self.model.load_settings_from_file()
        self.change_settings_status('Settings loaded')

    def btn_set_default_click(self):
        self.view.plot.clear_selector()
        self.model.load_default_settings()
        self.change_settings_status('Default settings')
    
    def btn_start_click(self):
        elem = self.view.meas.elem
        elem['unlock_stop'].setChecked(False)
        if self.model.start_measurement_process():
            self.lock_control_elem()
            elem['progress_label'].setText('Waiting...')
            elem['progress_label'].show()
            self.status_bar.info('Measurement in progress...')
        
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

    def btn_load_s21_gen_sa_click(self):
        self.model.load_s21_gen_sa()
        logger.debug('Load S21 Gen-SA file')

    def btn_load_s21_gen_det_click(self):
        self.model.load_s21_gen_det()
        logger.debug('Load S21 Gen-Det file')
  
    def btn_apply_click(self):
        logger.debug('Apply button clicked')
        try:
            WriteSettings.view_to_model(self)
            self.view.plot.clear_selector()
            self.model.settings_changed.emit(self.model.settings)
        except Exception as e:
            self.status_bar.error(f"Error applying settings: {e}")

    def btn_protocol_click(self):
        selected_frequency = self.view.plot.get_current_frequency()
        if selected_frequency is None:
            return
        
        with open("results.csv", "r") as file:
            next(file) # skip header
            result_file = list(csv.reader(file))
            data = []
            for row in result_file:
                if is_equal_frequencies(row[0], selected_frequency):
                    data.append(row)

        with open("Settings/meas_settings.json", "r") as file:
            settings = json.load(file)
            doc = MeasurementProtocol(data, settings)

    def data_signals_handler(self, message):
        if 'data' in message:
            if self.check_recalc():
                self.model.recalc_data()
        if 'point' in message:
            print(f"message['point'][0]: {message['point'][0]}")
            if (self.view.plot.frequency - message['point'][0]) < 100: # 100 Hz tolerance
                self.view.plot.figure1.add_point(message['point'][1], message['point'][3]*1e3)
                self.view.plot.figure2.add_point(message['point'][2], message['point'][3]*1e3, autoscale=True)
        if 'frequency' in message:
            self.view.plot.frequency = message['frequency']
            self.view.plot.clear_plot()
            self.view.plot.set_selector()
        if 'recalc_data' in message:
            print(message['recalc_data'])


    def update_gen_elem(self, message, mes_key, param):
        elem_key, unit = param
        if unit in self.units:
             dev = self.units[unit]

        value_min, value_max, points = message.get(f'{mes_key}', (None, None, None))
        elem = self.view.meas.elem
        elem[f'{elem_key}_min_line'].setText(remove_zeros(value_min/dev))
        elem[f'{elem_key}_max_line'].setText(remove_zeros(value_max/dev))
        elem[f'{elem_key}_points_line'].setText(remove_zeros(points))

    def update_sa_elem(self, value, param):
        elem_key, unit = param
        if unit in self.units:
             dev = self.units[unit]
        self.view.meas.elem[f'{elem_key}_line'].setText(remove_zeros(value/dev))

    def update_osc_elem(self, value, param):
        self.update_sa_elem(value, param)

    
    def change_state_precise(self):
        """Precise checkbox handler"""
        is_checked = self.view.meas.elem['precise_enabled'].isChecked()
        self.enable_precise(is_checked)

    def change_state_recalc(self):
        is_checked = self.view.meas.elem['recalc_att'].isChecked()
        self.enable_recalc(is_checked)

    def enable_precise(self, state):
        elem = self.view.meas.elem
        elem['precise_enabled'].setChecked(state)
        keys = ('span_precise_label', 'span_precise_line',
                'rbw_precise_label', 'rbw_precise_line',
                'vbw_precise_label', 'vbw_precise_line')
        for key in keys:
            elem[key].setEnabled(state)

    def enable_recalc(self, state):
        elem = self.view.meas.elem
        elem['recalc_att'].setChecked(state)
        keys = ('s21_gen_sa_label', 's21_gen_sa_file_label',
                's21_gen_det_label', 's21_gen_det_file_label',
                'btn_load_s21_gen_sa', 'btn_load_s21_gen_det')
        for key in keys:
            elem[key].setEnabled(state)
    
    def check_recalc(self):
        if not self.view.meas.elem['recalc_att'].isChecked():
            return False
        if  self.model.s21_gen_det is None or self.model.s21_gen_sa is None:
            return False
        return True


    def unlock_stop_btn(self):
        elem = self.view.meas.elem
        is_checked = elem['unlock_stop'].isChecked()
        elem['btn_stop'].setEnabled(is_checked)
        elem['unlock_stop'].setChecked(is_checked)

    def status_bar_signals_handler(self, message):
        print(message)
        elem = self.view.meas.elem
        elem['progress'].setValue(message)

    def s21_signals_handler(self, message):
        if 's21_gen_sa' in message:
            elem = self.view.meas.elem['s21_gen_sa_file_label']
            elem.setText(message['s21_gen_sa'])
            elem.setProperty('class', 's21_label_file')
            refresh_obj_view(elem)
        if 's21_gen_det' in message:
            elem = self.view.meas.elem['s21_gen_det_file_label']
            elem.setText(message['s21_gen_det'])
            elem.setProperty('class', 's21_label_file')
            refresh_obj_view(elem)


    def equipment_signals_handler(self, message):
        """Handle completion of SCPI-instrument objects initialization"""
        logger.debug('MeasController: equipment signals handler')

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
        SettingsSignalHandler.handler(self, message)
        self.set_elements_unchanged()

    def meas_signals_handler(self, message):
        elem = self.view.meas.elem
        if 'Finish' in message:
            self.unlock_control_elem()
            self.unlock_start_btn()
            elem['progress_label'].setText('Finished')
            elem['progress'].setValue(0)
        if 'Stop' in message:
            self.unlock_control_elem()
            self.unlock_start_btn()
            elem['progress_label'].setText('Stopped')

        self.waiting_timer.start()

    def lock_control_elem(self):
        elem = self.view.meas.elem
        elem['btn_save_result'].setEnabled(False)
        elem['btn_start'].hide()
        elem['btn_stop'].setEnabled(False)
        elem['btn_stop'].show()

        elem = self.view.plot.elem
        elem['freq_cobmo'].setEnabled(False)
        elem['btn_protocol'].setEnabled(False)

    def unlock_control_elem(self):
        elem = self.view.meas.elem
        elem['btn_stop'].hide()
        elem['btn_start'].show()
        elem['btn_save_result'].setEnabled(True)

        elem = self.view.plot.elem
        elem['freq_cobmo'].setEnabled(True)
        elem['btn_protocol'].setEnabled(True)

    def run(self):
        logger.debug('GUI running')
        self.view.show()