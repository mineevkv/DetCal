from PyQt6.QtCore import QObject, QTimer
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QRadioButton

from ..helper_functions import refresh_obj_view
from Measurement.MeasurementModel.file_manager import FileManager
from .status_bar_controller import StatusBarController
from .write_settings import WriteSettings
from .model_signal_handler import ModelSignalHandler
from .view_signal_handler import ViewSignalHandler

from Measurement.InfographicController.infographic_controller import (
    InfographicController,
)


from GUI.palette import *

from System.logger import get_logger

logger = get_logger(__name__)


class MeasurementController(QObject):

    def __init__(self, model, view):
        super().__init__()

        self.general_view = view  # General View
        self.model = model  # General Measurement Model
        self.view = view.meas  # Measurement Sheet
        self.ig_controller = InfographicController(model, view)  # Slave Sheet

        self.units = FileManager.load_units()

        self.init_signals_handlers()  # Must be before instrument initialization
        self.init_view_controllers()

        self.model.instr_initialization()
        self.model.load_settings()

    def init_signals_handlers(self):
        ModelSignalHandler.init(self)
        ViewSignalHandler.init(self)
        self.init_timers_signals()

    def init_view_controllers(self):
        self.status_bar = StatusBarController(self.view.elem["STATUS_BAR_LABEL"])

    def init_timers_signals(self):
        self.settings_timer = QTimer()
        self.settings_timer.setInterval(3000)  # 3 second
        self.settings_timer.timeout.connect(self.hide_settings_status)

        self.waiting_timer = QTimer()
        self.waiting_timer.setInterval(5000)  # 5 second
        self.waiting_timer.timeout.connect(self.hide_waiting_status)

    def lock_start_btn(self):
        elem = self.view.elem
        elem["BTN_APPLY"].setEnabled(True)
        elem["BTN_START"].setEnabled(False)
        self.status_bar.warning("Submit input parameters")

    def unlock_start_btn(self):
        elem = self.view.elem
        elem["BTN_APPLY"].setEnabled(False)
        elem["BTN_START"].setEnabled(True)
        self.status_bar.info("Ready for measurement")

    def set_elements_unchanged(self):
        elem = self.view.elem
        for element in elem.values():
            if isinstance(element, (QLineEdit, QCheckBox, QRadioButton)):
                element.setProperty("class", "")
                refresh_obj_view(element)
        self.unlock_start_btn()

    def btn_clicked_connect(self, btn_name, btn_handler):
        if btn_handler is not None:
            self.view.elem[f"BTN_{btn_name}"].clicked.connect(btn_handler)

    def btn_save_settings_click(self):
        try:
            WriteSettings.view_to_model(self)
            if self.model.file_manager.save_settings():
                self.change_settings_status("Settings saved")
            else:
                self.status_bar.error("Failed to save settings")
        except Exception as e:
            self.status_bar.error(f"Save error: {e}")

    def change_settings_status(self, status):
        self.view.elem["SETTINGS_STATUS_LABEL"].setText(status)
        self.settings_timer.start()

    def hide_settings_status(self):
        self.settings_timer.stop()
        self.view.elem["SETTINGS_STATUS_LABEL"].setText("")

    def hide_waiting_status(self):
        self.waiting_timer.stop()
        self.view.elem["PROGRESS_LABEL"].setText("")

    def btn_load_settings_click(self):
        self.ig_controller.clear_selector()
        self.model.file_manager.load_settings_from_file()
        self.change_settings_status("Settings loaded")

    def btn_set_default_click(self):
        self.ig_controller.clear_selector()
        self.model.file_manager.load_default_settings()
        self.change_settings_status("Default settings")

    def btn_start_click(self):
        if self.model.start_measurement_process():
            self.view.elem["UNLOCK_STOP"].setChecked(False)
            self.lock_control_elem()
            self.progress_label_text("Waiting...")
            self.status_bar.info("Measurement in progress...")
        else:
            self.status_bar.error("Check instruments")
        
    def progress_label_text(self, text):
        self.waiting_timer.stop()
        self.view.elem["PROGRESS_LABEL"].setText(text)
        self.waiting_timer.start()

    def btn_stop_click(self):
        elem = self.view.elem
        elem["BTN_STOP"].setEnabled(False)
        elem["UNLOCK_STOP"].setChecked(False)
        self.model.stop_measurement_process()
        self.progress_label_text("Stopped")

    def btn_save_result_click(self):
        logger.debug("Save result")
        try:
            self.model.file_manager.save_results()
            self.progress_label_text("Saved")
        except Exception as e:
            self.status_bar.error(f"Save result error: {e}")

    def btn_load_s21_gen_sa_click(self):
        logger.debug("Load S21 Gen-SA file")
        if self.model.file_manager.load_s21_gen_sa():
            self.status_bar.info("S21 Gen-SA file loaded successfully")
        else:
            self.status_bar.error("Failed to load S21 Gen-SA file")
        

    def btn_load_s21_gen_det_click(self):
        logger.debug("Load S21 Gen-Det file")
        if self.model.file_manager.load_s21_gen_det():
            self.status_bar.info("S21 Gen-Det file loaded successfully")
        else:
            self.status_bar.error("Failed to load S21 Gen-Det file")
        

    def btn_apply_click(self):
        logger.debug("Apply button clicked")
        try:
            if not self.validate_settings():
                self.status_bar.error("Invalid settings")
                return
            WriteSettings.view_to_model(self)
            self.ig_controller.clear_selector()
            self.model.settings_changed.emit(self.model.settings)
        except Exception as e:
            self.status_bar.error(f"Error applying settings: {e}")

    def validate_settings(self):
        # Validate settings TODO: make function
        return True

    def change_state_precise(self):
        """Precise checkbox handler"""
        is_checked = self.view.elem["PRECISE_ENABLED"].isChecked()
        self.enable_precise(is_checked)

    def change_state_recalc(self):
        is_checked = self.view.elem["RECALC_ATT"].isChecked()
        self.enable_recalc(is_checked)

    def enable_precise(self, state):
        elem = self.view.elem
        elem["PRECISE_ENABLED"].setChecked(state)
        keys = (
            "SPAN_PRECISE_LABEL",
            "SPAN_PRECISE_LINE",
            "RBW_PRECISE_LABEL",
            "RBW_PRECISE_LINE",
            "VBW_PRECISE_LABEL",
            "VBW_PRECISE_LINE",
        )
        for key in keys:
            elem[key].setEnabled(state)

    def enable_recalc(self, state):
        elem = self.view.elem
        elem["RECALC_ATT"].setChecked(state)
        keys = (
            "S21_GEN_SA_LABEL",
            "S21_GEN_SA_FILE_LABEL",
            "S21_GEN_DET_LABEL",
            "S21_GEN_DET_FILE_LABEL",
            "BTN_LOAD_S21_GEN_SA",
            "BTN_LOAD_S21_GEN_DET",
        )
        for key in keys:
            elem[key].setEnabled(state)

    def check_recalc(self):
        if not self.view.elem["RECALC_ATT"].isChecked():
            return False
        if self.model.s21_gen_det is None or self.model.s21_gen_sa is None:
            return False
        return True

    def unlock_stop_btn(self):
        elem = self.view.elem
        is_checked = elem["UNLOCK_STOP"].isChecked()
        elem["BTN_STOP"].setEnabled(is_checked)
        elem["UNLOCK_STOP"].setChecked(is_checked)

    def lock_control_elem(self):
        elem = self.view.elem
        elem["BTN_SAVE_RESULT"].setEnabled(False)
        elem["BTN_START"].hide()
        elem["BTN_STOP"].setEnabled(False)
        elem["BTN_STOP"].show()
        self.ig_controller.lock_control_elem()

    def unlock_control_elem(self):
        elem = self.view.elem
        elem["BTN_STOP"].hide()
        elem["BTN_START"].show()
        elem["BTN_SAVE_RESULT"].setEnabled(True)
        self.ig_controller.unlock_control_elem()

    def cleanup(self):
        """Call this when controller is being destroyed"""
        self.settings_timer.stop()
        self.waiting_timer.stop()
