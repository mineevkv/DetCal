from .write_settings import WriteSettings
from Measurement.MeasurementModel.recalc_results import RecalcResults

from System.logger import get_logger

logger = get_logger(__name__)

class ButtonsMC():
    def __init__(self, meas_controller) -> None:
        self.mc = meas_controller

    def btn_stop_click(self) -> None:
        """
        Stop the measurement process.

        This function is called when the "Stop" button is clicked.
        It will stop the measurement process and unlock the controls elements.
        """
        elem = self.mc.view.elem
        elem["BTN_STOP"].setEnabled(False)
        elem["UNLOCK_STOP"].setChecked(False)
        self.mc.model.stop_measurement_process()
        self.mc.progress_label_text("Stopped")

    def btn_save_settings_click(self) -> None:
        """
        Save the current settings to the settings file.

        This function is called when the "Save settings" button is clicked.
        """
        if not self.mc.validate_settings():
            return
        try:
            WriteSettings.view_to_model(self.mc)
            if self.mc.model.file_manager.save_settings():
                self.mc.change_settings_status("Settings saved")
            else:
                self.mc.status_bar.error("Failed to save settings")
        except Exception as e:
            self.mc.status_bar.error(f"Save error: {e}")

    def btn_load_settings_click(self) -> None:
        """
        Load settings from a file.

        This function is called when the "Load settings" button is clicked.
        It will load the settings from a file and update the model.
        """
        self.mc.ig_controller.clear_selector()
        if self.mc.model.file_manager.load_settings_from_file():
            self.mc.change_settings_status("Settings loaded")
        else:
            self.mc.lock_start_btn()
            self.mc.status_bar.error("Failed to load settings")

    def btn_set_default_click(self) -> None:
        """
        Set default settings.

        This function is called when the "Default" button is clicked.
        It will load the default settings from a file and update the model.
        """
        self.mc.ig_controller.clear_selector()
        self.mc.model.file_manager.load_default_settings()
        self.mc.change_settings_status("Default settings")

    def btn_start_click(self) -> None:
        """
        Start the measurement process.

        This function is called when the "Start" button is clicked.
        It will check if the instruments are initialized and if the settings are valid, then start the measurement process.
        """
        if not self.mc.validate_settings():
            return
        if self.mc.model.start_measurement_process():
            self.mc.view.elem["UNLOCK_STOP"].setChecked(False)
            self.mc.lock_control_elem()
            self.mc.progress_label_text("Waiting...")
            self.mc.status_bar.info("Measurement in progress...")
        else:
            self.mc.status_bar.error("Check instruments")

    def btn_save_result_click(self) -> None:
        """
        Save the measurement results to a file.

        This function is called when the "Save result" button is clicked.
        It will save the measurement results to a file and update the progress label.
        """
        logger.debug("Save result")
        try:
            self.mc.model.file_manager.save_results('open')
            self.mc.progress_label_text("Saved")
        except Exception as e:
            self.mc.status_bar.error(f"Save result error: {e}")

    
    def btn_load_s21_gen_sa_click(self) -> None:
        """
        Load an S21 Gen-SA parameters from external file.

        This function is called when the "Load S21 Gen-SA file" button is clicked.
        It will load the S21 Gen-SA file and update the status bar.
        """
        logger.debug("Load S21 Gen-SA file")
        if self.mc.model.file_manager.load_s21_gen_sa():
            self.mc.status_bar.info("S21 Gen-SA file loaded successfully")
        else:
            self.mc.status_bar.error("Failed to load S21 Gen-SA file")

    def btn_load_s21_gen_det_click(self) -> None:
        """
        Load an S21 Gen-Det parameters from external file.

        This function is called when the "Load S21 Gen-Det file" button is clicked.
        It will load the S21 Gen-Det file and update the status bar.
        """
        logger.debug("Load S21 Gen-Det file")
        if self.mc.model.file_manager.load_s21_gen_det():
            self.mc.status_bar.info("S21 Gen-Det file loaded successfully")
        else:
            self.mc.status_bar.error("Failed to load S21 Gen-Det file")

    def btn_apply_click(self) -> None:
        """
        Apply the settings to the model.

        This function is called when the "Apply" button is clicked.
        It will validate the settings, then apply them to the model if they are valid.
        """
        logger.debug("Apply button clicked")
        try:
            if not self.mc.validate_settings():
                return
            WriteSettings.view_to_model(self.mc)
            self.mc.ig_controller.clear_selector()
            self.mc.model.settings_changed.emit(self.mc.model.settings)
        except Exception as e:
            self.mc.status_bar.error(f"Error applying settings: {e}")

    def btn_recalc_external_click(self) -> None:
        if RecalcResults.from_external_file(self.mc.model):
           self.mc.status_bar.info("Recalculation completed")
        else:
            self.mc.status_bar.error("Recalculation failed")