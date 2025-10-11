from Measurement.helper_functions import get_s21, open_file
import numpy as np
from Measurement.MeasurementModel.file_manager import FileManager
from PyQt6.QtWidgets import QFileDialog
import os

from System.logger import get_logger

logger = get_logger(__name__)


class RecalcResults:
    """Class for recalculating measurement results using S21 parameters."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def from_external_file(model: object) -> bool:
        """
        Recalculate measurement results using S21 parameters from an external file.

        :param model: The measurement model object
        :return: True if the recalculated data was saved successfully, False otherwise
        """
        try:
            path = open_file(type_filter="CSV files (*.csv)")
            if not path:
                logger.warning("No file selected")
                return False
            data = np.genfromtxt(path, delimiter=",", skip_header=True)
            recalc_data = RecalcResults.recalc_data(
                data, model.s21_gen_sa, model.s21_gen_det
            )

            filename = os.path.basename(path) if path else None
            file_dir = os.path.dirname(path) if path else None
            new_filename = filename.split(".")[0] + "_recalc.csv"
            new_path = os.path.join(file_dir, new_filename)

            if FileManager.save_results_to_file(
                recalc_data, os.path.normpath(new_path)
            ):
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Failed to open file dialog: {e}")
            return False

    @staticmethod
    def recalc_data(
        meas_data: list, s21_gen_sa_data: list, s21_gen_det_data: list
    ) -> list:
        """
        Recalculate data via measured S21 parameters.

        This function recalculates the measurement data using the measured S21 parameters.
        The recalculated data is stored in the form of a list of tuples, where each tuple
        contains the frequency (Hz), the output power level (dBm), the level (dBm) measured by the Spectrum Analyzer,
        and the voltage measured by the oscilloscope.

        :return: A list of tuples containing the recalculated data
        :rtype: list
        """
        recalc_data = []
        for point in meas_data:
            frequency, level, sa_level, osc_voltage = point[:4]
            s21_gen_sa_dB = get_s21(frequency, s21_gen_sa_data)
            s21_gen_det_dB = get_s21(frequency, s21_gen_det_data)
            det_level = (sa_level - s21_gen_sa_dB) + s21_gen_det_dB

            recalc_point = [
                frequency,
                level,
                sa_level,
                osc_voltage,
                s21_gen_sa_dB,
                s21_gen_det_dB,
                det_level,
            ]
            recalc_data.append(recalc_point)
        return recalc_data
