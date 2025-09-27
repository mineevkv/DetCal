from PyQt6.QtCore import QObject, QTimer
from GUI.palette import *
from Measurement.InfographicController.infographic_controller import (
    InfographicController,
)
from Measurement.MeasurementModel.file_manager import FileManager
from .model_signal_handler import ModelSignalHandler
from .status_bar_controller import StatusBarController
from .view_signal_handler import ViewSignalHandler
from .write_settings import WriteSettings
from .settings_validator import SettingsValidator

from System.logger import get_logger

logger = get_logger(__name__)


class MeasurementController(QObject):
    """
    Measurement Controller class.

    This class is responsible for managing the Measurement Model and the Measurement Sheet (View) and the Infographic Sheet.
    It initializes the Signal Handlers and the View Controllers.

    :param model: The Measurement Model.
    :param view: The View.
    """

    def __init__(self, model: object, view: object) -> None:
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


    def init_signals_handlers(self) -> None:
        """
        Initialize the Signal Handlers.

        """
        ModelSignalHandler.init(self)
        ViewSignalHandler.init(self)
        self.init_timers_signals()

    def init_view_controllers(self) -> None:
        """
        Initialize the View Controllers.

        """
        self.status_bar = StatusBarController(self.view.elem["STATUS_BAR_LABEL"])

    def init_timers_signals(self) -> None:
        """
        Initialize the Timers related to the Signal Handlers.

        The Timers are used to hide the status messages after a certain amount of time.
        """
        # TODO class for timers
        self.settings_status_timer = QTimer()
        self.settings_status_timer.setInterval(3000)  # 3 second
        self.settings_status_timer.timeout.connect(self.hide_settings_status)

        self.meas_waiting_timer = QTimer()
        self.meas_waiting_timer.setInterval(5000)  # 5 second
        self.meas_waiting_timer.timeout.connect(self.hide_meas_waiting_status)

    def lock_start_btn(self) -> None:
        """
        Lock the start button to prevent multiple measurements from being started at the same time.

        This function is called when the measurement process is started.
        """
        elem = self.view.elem
        elem["BTN_APPLY"].setEnabled(True)
        elem["BTN_START"].setEnabled(False)
        self.status_bar.warning("Submit input parameters")

    def unlock_start_btn(self) -> None:
        """
        Unlock the start button.

        This function is called when the measurement process is finished.
        """
        elem = self.view.elem
        elem["BTN_APPLY"].setEnabled(False)
        elem["BTN_START"].setEnabled(True)
        self.status_bar.info("Ready for measurement")

    def btn_save_settings_click(self) -> None:
        """
        Save the current settings to the settings file.

        This function is called when the "Save settings" button is clicked.
        """
        if not self.validate_settings():
            return
        try:
            WriteSettings.view_to_model(self)
            if self.model.file_manager.save_settings():
                self.change_settings_status("Settings saved")
            else:
                self.status_bar.error("Failed to save settings")
        except Exception as e:
            self.status_bar.error(f"Save error: {e}")

    def change_settings_status(self, text: str) -> None:
        """
        Change the status of the settings label.

        Args:
            status (str): New status of the settings label.

        This function is called when the settings are saved or loaded from buttons.
        It will show the new status for a few seconds.
        """
        self.view.elem["SETTINGS_STATUS_LABEL"].setText(text)
        self.settings_status_timer.start()

    def hide_settings_status(self) -> None:
        """
        Hide the settings status label.

        This function is called after the settings status label has been shown for a few seconds.
        It will stop the timer and erase the text of the label.
        """
        self.settings_status_timer.stop()
        self.view.elem["SETTINGS_STATUS_LABEL"].setText("")

    def hide_meas_waiting_status(self) -> None:
        """
        Hide the waiting status label.

        This function is called after the waiting status label has been shown for a few seconds.
        It will stop the timer and erase the text of the label.
        """
        self.meas_waiting_timer.stop()
        self.view.elem["PROGRESS_LABEL"].setText("")

    def btn_load_settings_click(self) -> None:
        """
        Load settings from a file.

        This function is called when the "Load settings" button is clicked.
        It will load the settings from a file and update the model.
        """
        self.ig_controller.clear_selector()
        self.model.file_manager.load_settings_from_file()
        self.change_settings_status("Settings loaded")

    def btn_set_default_click(self) -> None:
        """
        Set default settings.

        This function is called when the "Default" button is clicked.
        It will load the default settings from a file and update the model.
        """
        self.ig_controller.clear_selector()
        self.model.file_manager.load_default_settings()
        self.change_settings_status("Default settings")

    def btn_start_click(self) -> None:
        """
        Start the measurement process.

        This function is called when the "Start" button is clicked.
        It will check if the instruments are initialized and if the settings are valid, then start the measurement process.
        """
        if not self.validate_settings():
            return
        if self.model.start_measurement_process():
            self.view.elem["UNLOCK_STOP"].setChecked(False)
            self.lock_control_elem()
            self.progress_label_text("Waiting...")
            self.status_bar.info("Measurement in progress...")
        else:
            self.status_bar.error("Check instruments")

    def progress_label_text(self, text: str) -> None:
        """
        Update the progress label text.

        This function is called when the progress label needs to be updated.
        It will stop the waiting timer, update the label text, and then start the waiting timer again.
        """
        self.meas_waiting_timer.stop()
        self.view.elem["PROGRESS_LABEL"].setText(text)
        self.meas_waiting_timer.start()

    def btn_stop_click(self) -> None:
        """
        Stop the measurement process.

        This function is called when the "Stop" button is clicked.
        It will stop the measurement process and unlock the controls elements.
        """
        elem = self.view.elem
        elem["BTN_STOP"].setEnabled(False)
        elem["UNLOCK_STOP"].setChecked(False)
        self.model.stop_measurement_process()
        self.progress_label_text("Stopped")

    def btn_save_result_click(self) -> None:
        """
        Save the measurement results to a file.

        This function is called when the "Save result" button is clicked.
        It will save the measurement results to a file and update the progress label.
        """
        logger.debug("Save result")
        try:
            self.model.file_manager.save_results()
            self.progress_label_text("Saved")
        except Exception as e:
            self.status_bar.error(f"Save result error: {e}")

    def btn_load_s21_gen_sa_click(self) -> None:
        """
        Load an S21 Gen-SA parameters from external file.

        This function is called when the "Load S21 Gen-SA file" button is clicked.
        It will load the S21 Gen-SA file and update the status bar.
        """
        logger.debug("Load S21 Gen-SA file")
        if self.model.file_manager.load_s21_gen_sa():
            self.status_bar.info("S21 Gen-SA file loaded successfully")
        else:
            self.status_bar.error("Failed to load S21 Gen-SA file")

    def btn_load_s21_gen_det_click(self) -> None:
        """
        Load an S21 Gen-Det parameters from external file.

        This function is called when the "Load S21 Gen-Det file" button is clicked.
        It will load the S21 Gen-Det file and update the status bar.
        """
        logger.debug("Load S21 Gen-Det file")
        if self.model.file_manager.load_s21_gen_det():
            self.status_bar.info("S21 Gen-Det file loaded successfully")
        else:
            self.status_bar.error("Failed to load S21 Gen-Det file")

    def btn_apply_click(self) -> None:
        """
        Apply the settings to the model.

        This function is called when the "Apply" button is clicked.
        It will validate the settings, then apply them to the model if they are valid.
        """
        logger.debug("Apply button clicked")
        try:
            if not self.validate_settings():
                return
            WriteSettings.view_to_model(self)
            self.ig_controller.clear_selector()
            self.model.settings_changed.emit(self.model.settings)
        except Exception as e:
            self.status_bar.error(f"Error applying settings: {e}")

    def validate_settings(self) -> bool:
        """
        Validate the settings.

        This function is called before applying the settings to the model.
        It will check if the settings are valid and return True if they are, False otherwise.
        """
        validator = SettingsValidator(self.view)
        result = validator.check()
        if not result:
            self.status_bar.error("Invalid settings")
        return result

    def change_state_precise(self) -> None:
        """
        Precise checkbox handler.

        This function is called when the "Precise" checkbox is changed.
        It will update the state of the precise fields in the view.
        """
        is_checked = self.view.elem["PRECISE_ENABLED"].isChecked()
        self.enable_precise(is_checked)

    def change_state_recalc(self) -> None:
        """
        Recalc attenuation checkbox handler.

        This function is called when the "Recalc attenuation" checkbox is changed.
        It will update the state of the recalc fields in the view.
        """
        is_checked = self.view.elem["RECALC_ATT"].isChecked()
        self.enable_recalc(is_checked)

    def enable_precise(self, state: bool) -> None:
        """
        Enable or disable the precise fields in the view.

        Args:
            state (bool): The state of the precise fields.
        """
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

    def enable_recalc(self, state: bool) -> None:
        """
        Enable or disable the recalc attenuation fields in the view.

        Args:
            state (bool): The state of the recalc attenuation fields.
        """
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

    def check_recalc(self) -> bool:
        """
        Check if the recalc attenuation is enabled and if the S21 files are loaded.

        Returns:
            bool: True if the recalc checkbox is enabled and the files are loaded, False otherwise.
        """
        if not self.view.elem["RECALC_ATT"].isChecked():
            return False
        if self.model.s21_gen_det is None or self.model.s21_gen_sa is None:
            return False
        return True

    def unlock_stop_btn(self) -> None:
        """
        Unlock the stop button.

        This function is called when the "Unlock STOP" checkbox is changed.
        It will update the state of the stop button.
        """
        elem = self.view.elem
        is_checked = elem["UNLOCK_STOP"].isChecked()
        elem["BTN_STOP"].setEnabled(is_checked)
        elem["UNLOCK_STOP"].setChecked(is_checked)

    def lock_control_elem(self) -> None:
        """
        Lock the control elements.

        This function is called when the measurement process is started.
        It will lock the control elements in the view.
        """
        elem = self.view.elem
        elem["BTN_SAVE_RESULT"].setEnabled(False)
        elem["BTN_START"].hide()
        elem["BTN_STOP"].setEnabled(False)
        elem["BTN_STOP"].show()
        self.ig_controller.lock_control_elem()

    def unlock_control_elem(self) -> None:
        """
        Unlock the control elements.

        This function is called when the measurement process is finished.
        It will unlock the control elements in the view.
        """
        elem = self.view.elem
        elem["BTN_STOP"].hide()
        elem["BTN_START"].show()
        elem["BTN_SAVE_RESULT"].setEnabled(True)
        self.ig_controller.unlock_control_elem()

    def cleanup(self) -> None:
        """
        Clean up the measurement controller.

        This function is called when the measurement controller is about to be deleted.
        It will stop all the timers and clean up the resources.
        """
        self.settings_status_timer.stop()
        self.meas_waiting_timer.stop()
