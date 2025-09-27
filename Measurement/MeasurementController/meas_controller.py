from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QRadioButton

from ..helper_functions import remove_zeros, str_to_bool, refresh_obj_view, is_equal_frequencies, load_units
from .status_bar_controller import StatusBarController
from .write_settings import WriteSettings
from .model_signal_handler import ModelSignalHandler

from Measurement.InfographicController.infographic_controller import InfographicController

import csv
import json
from GUI.palette import *

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementController(QObject):
    units = dict()

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

    def __init__(self, model, view):
        super().__init__()

        self.units = load_units() # MHz, dBm, ms, ...

        self.general_view = view # General View
        self.model = model  # General Measurement Model
        self.view = view.meas # Measurement Sheet
        self.ig_controller = InfographicController(model, view) # Slave Sheet

        self.init_signals_handlers() # Must be before instrument initialization
        self.init_view_controllers()

        self.model.instr_initialization()
        self.model.load_settings()


    def init_signals_handlers(self):
        ModelSignalHandler.init(self)
        self.init_view_signals()
        self.init_timers_signals()


    def init_view_controllers(self):
        self.status_bar = StatusBarController(self.view.elem['status_bar_label'])

    def init_timers_signals(self):
        self.settings_timer = QTimer()
        self.settings_timer.setInterval(3000) # 3 second
        self.settings_timer.timeout.connect(self.hide_settings_status)

        self.waiting_timer = QTimer()
        self.waiting_timer.setInterval(5000) # 5 second
        self.waiting_timer.timeout.connect(self.hide_waiting_status)


    def init_view_signals(self):
        elem =self.view.elem
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
                element.textChanged.connect(lambda _, object=element: self.element_changed(object))
            elif isinstance(element, (QRadioButton, QCheckBox)):
                if isinstance(element, QCheckBox) and element is elem['unlock_stop']:
                    continue
                element.toggled.connect(lambda _, object=element: self.element_changed(object))

    def element_changed(self, object):
        if isinstance(object, QLineEdit):
            object.setProperty('class', 'line_changed')
        elif isinstance(object, (QCheckBox, QRadioButton)):
            object.setProperty('class', 'radiocheck_changed')

        refresh_obj_view(object)
        self.lock_start_btn()


    def lock_start_btn(self):
        elem = self.view.elem
        elem['btn_apply'].setEnabled(True)
        elem['btn_start'].setEnabled(False)
        self.status_bar.warning('Submit input parameters')

    def unlock_start_btn(self):
        elem = self.view.elem
        elem['btn_apply'].setEnabled(False)
        elem['btn_start'].setEnabled(True)
        self.status_bar.info('Ready to measurement')
        
    def set_elements_unchanged(self):
        elem =self.view.elem
        for element in elem.values():
            if isinstance(element, (QLineEdit, QCheckBox, QRadioButton)):
                element.setProperty('class', '')
                refresh_obj_view(element)
        self.unlock_start_btn()

    def btn_clicked_connect(self, btn_name, btn_handler):
        if btn_handler is not None:
            self.view.elem[f'btn_{btn_name}'].clicked.connect(btn_handler)

    def btn_save_settings_click(self):
        WriteSettings.view_to_model(self)
        self.model.file_manager.save_settings()
        self.change_settings_status('Settings saved')

    def change_settings_status(self,status):
        elem = self.view.elem['settings_status_label']
        elem.setText(status)
        elem.show()
        self.settings_timer.start()

    def hide_settings_status(self):
        self.settings_timer.stop()
        elem = self.view.elem['settings_status_label']
        elem.hide()
        
    def hide_waiting_status(self):
        self.waiting_timer.stop()
        elem = self.view.elem
        elem['progress_label'].setText('')

    def btn_load_settings_click(self):
        self.ig_controller.clear_selector()
        self.model.file_manager.load_settings_from_file()
        self.change_settings_status('Settings loaded')

    def btn_set_default_click(self):
        self.ig_controller.clear_selector()
        self.model.file_manager.load_default_settings()
        self.change_settings_status('Default settings')
    
    def btn_start_click(self):
        elem = self.view.elem
        elem['unlock_stop'].setChecked(False)
        if self.model.start_measurement_process():
            self.lock_control_elem()
            elem['progress_label'].setText('Waiting...')
            elem['progress_label'].show()
            self.status_bar.info('Measurement in progress...')

    def progress_label_text(self, text):
        elem = self.view.elem
        elem['progress_label'].setText(text)
        elem['progress_label'].show()
        self.waiting_timer.start()
        
    def btn_stop_click(self):
        elem = self.view.elem
        elem['btn_stop'].setEnabled(False)
        elem['unlock_stop'].setChecked(False)
        self.model.stop_measurement_process()
        self.progress_label_text('Stopped')
    
    def btn_save_result_click(self):
        logger.debug('Save result')
        self.model.file_manager.save_results()
        self.progress_label_text('Saved')

    def btn_load_s21_gen_sa_click(self):
        self.model.file_manager.load_s21_gen_sa()
        logger.debug('Load S21 Gen-SA file')

    def btn_load_s21_gen_det_click(self):
        self.model.file_manager.load_s21_gen_det()
        logger.debug('Load S21 Gen-Det file')
  
    def btn_apply_click(self):
        logger.debug('Apply button clicked')
        try:
            WriteSettings.view_to_model(self)
            self.ig_controller.clear_selector()
            self.model.settings_changed.emit(self.model.settings)
        except Exception as e:
            self.status_bar.error(f"Error applying settings: {e}")
    
    def change_state_precise(self):
        """Precise checkbox handler"""
        is_checked = self.view.elem['precise_enabled'].isChecked()
        self.enable_precise(is_checked)

    def change_state_recalc(self):
        is_checked = self.view.elem['recalc_att'].isChecked()
        self.enable_recalc(is_checked)

    def enable_precise(self, state):
        elem = self.view.elem
        elem['precise_enabled'].setChecked(state)
        keys = ('span_precise_label', 'span_precise_line',
                'rbw_precise_label', 'rbw_precise_line',
                'vbw_precise_label', 'vbw_precise_line')
        for key in keys:
            elem[key].setEnabled(state)

    def enable_recalc(self, state):
        elem = self.view.elem
        elem['recalc_att'].setChecked(state)
        keys = ('s21_gen_sa_label', 's21_gen_sa_file_label',
                's21_gen_det_label', 's21_gen_det_file_label',
                'btn_load_s21_gen_sa', 'btn_load_s21_gen_det')
        for key in keys:
            elem[key].setEnabled(state)
    
    def check_recalc(self):
        if not self.view.elem['recalc_att'].isChecked():
            return False
        if  self.model.s21_gen_det is None or self.model.s21_gen_sa is None:
            return False
        return True

    def unlock_stop_btn(self):
        elem = self.view.elem
        is_checked = elem['unlock_stop'].isChecked()
        elem['btn_stop'].setEnabled(is_checked)
        elem['unlock_stop'].setChecked(is_checked)

    def lock_control_elem(self):
        elem = self.view.elem
        elem['btn_save_result'].setEnabled(False)
        elem['btn_start'].hide()
        elem['btn_stop'].setEnabled(False)
        elem['btn_stop'].show()
        self.ig_controller.lock_control_elem()

    def unlock_control_elem(self):
        elem = self.view.elem
        elem['btn_stop'].hide()
        elem['btn_start'].show()
        elem['btn_save_result'].setEnabled(True)
        self.ig_controller.unlock_control_elem()