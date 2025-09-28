from Instruments.rsa5000vna_parcer import RSA506N_S21_Parser
from PyQt6.QtWidgets import QFileDialog
from ..helper_functions import read_csv_file, open_file
import os
import json
import numpy as np

from System.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """
    A class to handle file operations for the measurement model.

    This class provides functions to load settings from a file and to load S21 files.

    """
    def __init__(self, meas_model: object) -> None:
        self.model = meas_model

    def load_settings_from_file(self) -> None:
        """
        Load settings from a opened file.

        This function will load the settings from a manual opened file and update the measurement model.
        """
        logger.debug("MeasModel: load settings from file")
        settings = self.open_settings_file()
        if settings:
            self.model.settings = settings

    def load_settings(self, default: bool = False) -> None:
        """
        Load settings from a file.

        This function will load the settings from a file and update the measurement model.

        Parameters:
                default (bool): If True, load the default settings file. If False, load the user settings file.
        """
        folder = self.model.settings_folder
        filename = self.model.settings_filename
        settings = {}

        if default:
            logger.debug("FileManager: load default settings")
            path = os.path.join(folder, f"{filename}_default.json")
            if not os.path.exists(path):
                error_msg = f"Default settings file not found: {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
        else:
            logger.debug("FileManager: load settings")
            path = os.path.join(folder, f"{filename}.json")
            if not os.path.exists(path):
                error_msg = f"User settings file not found: {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)

        try:
            with open(path, "r") as f:
                settings = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load settings from {path}: {e}")
            raise  # Re-raise the exception after logging

        if settings:
            self.model.settings = settings
            logger.info(f"Settings loaded successfully from {path}")

    def load_default_settings(self) -> None:
        """
        Load default settings from a file.

        This function will load the default settings from a file and update the measurement model.

        The default settings file is located in the settings folder and is named
        `meas_settings_default.json`".

        Raises:
            FileNotFoundError: If the default settings file is not found.
        """
        self.load_settings(default=True)

    def open_settings_file(self) -> dict:
        """
        Open a file dialog to load settings from a file.

        Returns:
            dict: A dictionary containing the settings.
        """
        try:
            path, _ = QFileDialog.getOpenFileName(
                caption="Load settings file",
                directory=self.model.settings_folder,
                filter="JSON files (*.json)",
            )
        except Exception as e:
            logger.warning(f"Failed to open file dialog: {e}")

        settings = {}
        if path:
            try:
                with open(path, "r") as f:
                    settings = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load settings from {path}: {e}")
        else:
            logger.warning(f"No file selected")

        return settings

    def save_settings(self) -> bool:
        """
        Save the current settings to a file.

        This function will save the current settings from the measurement model to a file in the settings folder.

        Returns:
            bool: True if the settings were saved successfully, False otherwise.

        """
        try:
            folder = self.model.settings_folder
            filename = self.model.settings_filename
            os.makedirs(folder, exist_ok=True)  # Ensure directory exists
            path = os.path.join(folder, f"{filename}.json")
            with open(path, "w") as f:
                json.dump(self.model.settings, f, indent=4)
                logger.info(f"Settings saved successfully to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def load_s21_gen_sa(self, filename: str = None) -> bool:
        """
        Load S21 parameters file for the line from generator to spectrum analyzer.

        This function will load the S21 parameters from a file and store them in the measurement model.

        Parameters:
            filename (str): The filename of the S21 file to load. If None, a file dialog will be opened to select the file.

        Returns:
            bool: True if the S21 parameters were loaded successfully, False otherwise.
        """
        try:
            if filename is None:
                path = open_file(self.model.s21_folder, "S21 files (*.trs)")
                filename = os.path.basename(path)
            self.model.s21_gen_sa = self.parse_s21_file(filename)
            return True
        except Exception as e:
            logger.warning(f"Failed to load S21 file: {e}")
            return False

    def load_s21_gen_det(self, filename=None) -> bool:
        """
        Load S21 parameters file for the line from generator to detector.

        This function will load the S21 parameters from a file and store them in the measurement model.

        Parameters:
            filename (str): The filename of the S21 file to load. If None, a file dialog will be opened to select the file.

        Returns:
            bool: True if the S21 parameters were loaded successfully, False otherwise.
        """
        try:
            if filename is None:
                path = open_file(self.model.s21_folder, "S21 files (*.trs)")
                filename = os.path.basename(path)
            self.model.s21_gen_det = self.parse_s21_file(filename)
            return True
        except Exception as e:
            logger.warning(f"Failed to load S21 file: {e}")
            return False

    def load_s21_files(self) -> bool:
        """
        Load both S21 parameters files for the lines from generator to spectrum analyzer and generator to detector.

        This function will load both S21 parameters files and store them in the measurement model.

        Returns:
            bool: True if both S21 parameters files were loaded successfully, False otherwise.
        """
        is_gen_sa_loaded = self.load_s21_gen_sa("s21_gen_sa.trs")
        is_gen_det_loaded = self.load_s21_gen_det("s21_gen_det.trs")
        return is_gen_sa_loaded and is_gen_det_loaded

    def parse_s21_file(self, filename: str) -> tuple[list[float], list[float]]:
        """
        Parse an S21 file and return the frequency and magnitude data.

        This function will parse an S21 file and return the frequency and magnitude data.

        Parameters:
            filename (str): The filename of the S21 file to parse.

        Returns:
            tuple[list[float], list[float]]: A tuple containing the frequency and magnitude data.

        Raises:
            FileNotFoundError: If the S21 file is not found.
        """
        path = os.path.join(self.model.s21_folder, filename)
        if not os.path.exists(path):
            error_msg = f"S21 file not found: {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        parser = RSA506N_S21_Parser(path)
        data = parser.parse_file()
        return (data["FREQUENCY"], data["MAGNITUDE_DB"])

    def save_results(self) -> None:
        """
        Save the measurement results to a CSV file.

        This function will save the measurement results to a CSV file. The filename will be selected by the user through a file dialog.

        The CSV file will contain the following columns:

        - Generator Frequency (Hz)
        - Generator output power Level (dBm)
        - Spectrum Analyzer input Level (dBm)
        - Oscilloscope Voltage (V) - Detector voltage output
        - S21 parameter from generator to spectrum analyzer (dB)
        - S21 parameter from generator to detector (dB)
        - Detector input power level (dBm) - Recalculated via S21 parameters
        """
        try:
            filename, _ = QFileDialog.getSaveFileName(
                caption="Save results",
                directory=os.path.join("results.csv"),
                filter="CSV files (*.csv)",
            )
        except Exception as e:
            logger.warning(f"Failed to open file dialog: {e}")

        if filename:
            try:
                file_header = "Gen Frequency (Hz), Gen Level (dBm), SA Level (dBm), Osc Voltage (V), S21 Gen-Sa (dB), S21 Gen-Det (dB), Det Level (dBm)"
                np.savetxt(
                    filename, self.model.meas_data, delimiter=",", header=file_header
                )
                logger.info(f"Results saved to {filename}")
            except Exception as e:
                logger.error(f"Failed to save results to {filename}: {e}")
        else:
            logger.warning(f"No file selected")

    @staticmethod
    def load_units(folder: str) -> dict:
        """
        Load units from a file.

        This function loads the units from a file and returns them as a dictionary.

        Returns:
            dict: A dictionary containing the units.

        Raises:
            FileNotFoundError: If the units file is not found.

        The units file should contain key-value pairs where the key is the unit name (e.g. Hz, dBm, V)
        and the value is the conversion factor to the base unit (e.g. 1, 1e3, 1e6).

        """
        units_file = os.path.join(folder, "units.json")
        if not os.path.exists(units_file):
            error_msg = f"Units file not found: {units_file}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        with open(units_file, "r") as f:
            return json.load(f)
