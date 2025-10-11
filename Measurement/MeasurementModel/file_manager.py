from Instruments.rsa5000vna_parcer import RSA506N_S21_Parser
from PyQt6.QtWidgets import QFileDialog
from ..helper_functions import read_csv_file, open_file
import os
import json
import numpy as np
from typing import Tuple, Dict, Any

from System.logger import get_logger

logger = get_logger(__name__)


class FileManager:
    """
    A class to handle file operations for the measurement model.

    This class provides functions to load settings from a file and to load S21 files.

    """

    def __init__(self, meas_model: object) -> None:
        self.model = meas_model

    def load_settings_from_file(self) -> bool:
        """
        Load settings from a opened file.

        This function will load the settings from a manual opened file and update the measurement model.
        """
        logger.debug("MeasModel: load settings from file")
        try:
            path = self.open_settings_file()
            if not path:  # Check if user cancelled or error occurred
                logger.info("Settings file selection cancelled")
                return False
            return self.load_settings(path)
        except Exception as e:
            logger.error(f"Failed to load settings from file: {e}")
            return False

    def is_settings(self, settings: dict) -> bool:
        """
        Check if the settings dictionary is valid.

        Parameters:
            settings (dict): A dictionary containing the settings.

        Returns:
            bool: True if the settings dictionary is valid, False otherwise.
        """
        keys = [
            "RF_FREQUENCIES",
            "RF_LEVELS",
            "SPAN_WIDE",
            "RBW_WIDE",
            "VBW_WIDE",
            "REF_LEVEL",
            "SWEEP_POINTS",
            "HOR_SCALE",
            "IMPEDANCE_50OHM",
            "COUPLING_DC",
        ]

        for key in keys:
            if key not in settings.keys():
                return False
        return True

    def load_settings(self, path: str) -> bool:
        """Load settings from a json file."""
        try:
            with open(path, "r", encoding="utf-8") as f:  # Added encoding
                settings = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load settings from {path}: {e}")
            return False

        if self.is_settings(settings):
            self.model.settings = settings
            logger.info(f"Settings loaded successfully from {path}")
            return True
        else:
            logger.error(f"Invalid settings file: {path}")
            return False

    def load_start_settings(self) -> bool:
        """Load settings from the existing settings json file."""
        logger.debug("FileManager: load settings")
        try:
            path = os.path.join(
                self.model.settings_folder, f"{self.model.settings_filename}.json"
            )
            if not os.path.exists(path):
                error_msg = f"User settings file not found: {path}"
                logger.error(error_msg)
                raise FileNotFoundError(error_msg)
            return self.load_settings(path)
        except Exception as e:
            logger.error(f"Failed to load start settings: {e}")
            return False

    def load_default_settings(self) -> bool:
        """Load default settings from the default settings json file."""
        logger.debug("FileManager: load default settings")
        path = os.path.join(
            self.model.settings_folder, f"{self.model.settings_filename}_default.json"
        )
        if not os.path.exists(path):
            error_msg = f"Default settings file not found: {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        return self.load_settings(path)

    def open_settings_file(self) -> str | None:
        """
        Open a file dialog to load settings from a file.

        Returns:
            str: Optional[str]: Path to the selected file, or None if cancelled/error
        """
        try:
            path, _ = QFileDialog.getOpenFileName(
                caption="Load settings file",
                directory=self.model.settings_folder,
                filter="JSON files (*.json)",
            )
            return path if path else None
        except Exception as e:
            logger.warning(f"Failed to open file dialog: {e}")
            return None

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
            if not os.path.exists(folder):
                os.makedirs(folder)
            path = os.path.join(folder, f"{filename}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.model.settings, f, indent=4)
                logger.info(f"Settings saved successfully to {path}")
            return True
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            return False

    def load_s21_gen_sa(self, filename: str = None) -> bool:
        """Load S21 parameters file for generator to spectrum analyzer line."""
        try:
            if filename is None:
                path = open_file(self.model.s21_folder, "S21 files (*.trs)")
                if not path:
                    logger.warning("No S21 file selected")
                    return False
                filename = os.path.basename(path)

            if not filename or not filename.strip():
                logger.error("Invalid filename provided")
                return False

            s21_data = self.parse_s21_file(filename)
            if s21_data is None:
                return False

            self.model.s21_gen_sa = s21_data
            self.model.s21_file_changed.emit({"S21_GEN_SA_FILENAME": filename})
            return True

        except Exception as e:
            logger.error(f"Failed to load S21 Gen-SA file: {e}")
            return False

    def load_s21_gen_det(self, filename: str = None) -> bool:
        """Load S21 parameters file for the line from generator to detector."""
        try:
            if filename is None:
                path = open_file(self.model.s21_folder, "S21 files (*.trs)")
                if not path:
                    logger.warning("No S21 file selected")
                    return False
                filename = os.path.basename(path)

            if not filename or not filename.strip():
                logger.error("Invalid filename provided")
                return False

            s21_data = self.parse_s21_file(filename)
            if s21_data is None:
                return False

            self.model.s21_gen_det = s21_data
            self.model.s21_file_changed.emit({"S21_GEN_DET_FILENAME": filename})
            return True

        except Exception as e:
            logger.error(f"Failed to load S21 Gen-Det file: {e}")
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

    def parse_s21_file(self, filename: str) -> tuple[list[float], list[float]] | None:
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

        try:
            parser = RSA506N_S21_Parser(path)
            data = parser.parse_file()

            # Validate the parsed data structure
            if not data or "FREQUENCY" not in data or "MAGNITUDE_DB" not in data:
                logger.error(f"Invalid S21 file format: {path}")
                return None

            frequencies = data["FREQUENCY"]
            magnitudes = data["MAGNITUDE_DB"]

            # Validate data content
            if not self.validate_s21_data(frequencies, magnitudes, path):
                return None

            return (frequencies, magnitudes)

        except Exception as e:
            logger.error(f"Failed to parse S21 file {filename}: {e}")
            return None

    def validate_s21_data(
        self, frequencies: Dict[str, Any], magnitudes: Dict[str, Any], path: str
    ) -> bool:
        """
        Validate the structure of S21 data arrays.
        """
        # Basic existence checks
        if frequencies is None or magnitudes is None:
            logger.error(f"S21 data is None in file: {path}")
            return False

        # Type checks
        if not isinstance(frequencies, (list, np.ndarray)) or not isinstance(
            magnitudes, (list, np.ndarray)
        ):
            logger.error(f"S21 data must be list or ndarray in file: {path}")
            return False

        # Convert and validate
        try:
            freq_array = np.asarray(frequencies, dtype=float)
            mag_array = np.asarray(magnitudes, dtype=float)
        except (ValueError, TypeError) as e:
            logger.error(f"S21 data contains non-numeric values in file {path}: {e}")
            return False

        # Dimension and size checks
        if freq_array.ndim != 1 or mag_array.ndim != 1:
            logger.error(f"S21 data must be 1-dimensional in file: {path}")
            return False

        if freq_array.size == 0 or mag_array.size == 0:
            logger.error(f"Empty S21 data in file: {path}")
            return False

        if freq_array.size != mag_array.size:
            logger.error(f"S21 data length mismatch in file: {path}")
            return False

        return True

    def save_results(self, mode: str = None) -> bool:
        """
        Saves the measurement results to a CSV file.

        The CSV file will contain the following columns:

        - Generator Frequency (Hz)
        - Generator output power Level (dBm)
        - Spectrum Analyzer input Level (dBm)
        - Oscilloscope Voltage (V) - Detector voltage output
        - S21 parameter from generator to spectrum analyzer (dB)
        - S21 parameter from generator to detector (dB)
        - Detector input power level (dBm) - Recalculated via S21 parameters

        In mode=open', the filename will be selected by the user through a file dialog.
        """
        path = None

        try:
            if not hasattr(self.model, "meas_data") or self.model.meas_data is None:
                logger.error("No measurement data to save")
                return False

            if "FILENAME" not in self.model.settings:
                logger.error("No filename specified in settings")
                return False

            filename = f"{self.model.settings['FILENAME']}_results.csv"
            if mode == "open":
                path, _ = QFileDialog.getSaveFileName(
                    caption="Save results",
                    directory=filename,
                    filter="CSV files (*.csv)",
                )
                if not path:  # User cancelled the dialog
                    logger.info("Save operation cancelled by user")
                    return False
            else:
                try:
                    os.makedirs(self.model.output_dir, exist_ok=True)
                    path = os.path.join(self.model.output_dir, filename)
                except OSError as e:
                    logger.error(f"Failed to create output directory: {e}")
                    return False
        except Exception as e:
            logger.error(f"Failed to open file dialog: {e}")
            return False

        # Ensure we have a valid path at this point
        if not path:
            logger.error("No valid file path determined for saving")
            return False

        return FileManager.save_results_to_file(self.model.meas_data, path)

    @staticmethod
    def save_results_to_file(data: list, path: str) -> bool:
        """Save measurement results to a CSV file."""
        if path:
            try:
                file_header = "Gen Frequency (Hz), Gen Level (dBm), SA Level (dBm), Osc Voltage (V), S21 Gen-Sa (dB), S21 Gen-Det (dB), Det Level (dBm)"
                np.savetxt(path, data, delimiter=",", header=file_header)
                logger.info(f"Results saved to {path}")
                return True
            except Exception as e:
                logger.error(f"Failed to save results to {path}: {e}")
        else:
            logger.warning(f"No file selected")
            return False

    @staticmethod
    def load_units(folder: str = "Settings") -> dict:
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
