"""
Helper functions module for the measurement model.

These functions are used by the measurement model to perform various tasks.

"""

import csv
import os
import numpy as np
from PyQt6.QtWidgets import QFileDialog


from System.logger import get_logger

logger = get_logger(__name__)


def remove_zeros(input_string: str | float) -> str | None:
    """
    Remove trailing zeros from a string containing a decimal point.

    Parameters:
        input_string (str): String containing a decimal point

    Returns:
        str: String with trailing zeros removed.
        If the input string is None, the function will return None.
    """
    if input_string is None:
        return None

    input_string = str(input_string)
    if "." in input_string:
        input_list = input_string.split(".")
        input_list[1] = input_list[1].rstrip("0")
        if input_list[1] == "":
            return input_list[0]
        input_list = ".".join(input_list)

    return input_list


def str_to_bool(value: str) -> bool:
    """
    Convert a string (json or python) str(boolean) value to a boolean value.

    Parameters:
        value: String value with boolean notation to convert

    Returns:
        bool: Boolean value of the input string value
    """
    if isinstance(value, str):
        value = value.lower()
        if value == "true":
            return True
        elif value == "false":
            return False
    return bool(value)


def refresh_obj_view(QObject_name: str) -> None:
    """
    Refresh the style of an object with the given name.

    Parameters:
        QObject_name (str): Name of the object to refresh
    """
    QObject_name.style().unpolish(QObject_name)
    QObject_name.style().polish(QObject_name)


def open_file(folder: str, type_filter: str = None) -> str | None:
    """
    Open a file dialog to open a file in the given folder.

    Parameters:
        folder (str): Folder to open the file dialog in
        filter (str): File filter to apply (optional)

    Returns:
        str: Path of the opened file. If not path: None
    """
    try:
        path, _ = QFileDialog.getOpenFileName(
            caption="Open file", directory=folder, filter=type_filter
        )
        return path
    except Exception as e:
        logger.warning(f"Failed to open file dialog: {e}")
        return None


def get_s21(target_frequency: float, s21: tuple[list[float], list[float]]) -> float:
    """
    Interpolate the S21 value at the given target frequency from the given S21 data.

    Parameters:
        target_frequency (float): The frequency at which to interpolate the S21 value
        s21 (tuple): A tuple containing the frequencies and magnitude of the S21 data

    Returns:
        float: The interpolated S21 value at the target frequency
    """
    frequencies = s21[0]
    magnitude_dB = s21[1]
    return np.interp(target_frequency, frequencies, magnitude_dB)


def is_equal_frequencies(
    frequency1: float, frequency2: float, tolerance: float = 1e4
) -> bool:
    """
    Check if two frequencies are equal within a given tolerance.

    Parameters:
        frequency1 (float): The first frequency (Hz) to compare
        frequency2 (float): The second frequency (Hz) to compare
        tolerance (float, optional): The tolerance within which the frequencies are considered equal. Defaults to 10kHz.

    Returns:
        bool: True if the frequencies are equal within the given tolerance, False otherwise
    """
    return abs(float(frequency1) - float(frequency2)) < tolerance


def read_csv_file(folder: str, filename: str = None) -> tuple[list, str] | None:
    """
    Read a CSV file from the specified folder.

    Parameters:
        folder (str): The folder containing the CSV file
        filename (str, optional): The name of the CSV file to read

    Returns:
        tuple: A tuple containing:
            - list: The contents of the CSV file as a list of rows
            - str: The full path to the CSV file that was read

    Raises:
        FileNotFoundError: If no CSV file is found in the specified folder
        csv.Error: If the file contains CSV formatting errors
        ValueError: If the folder contains multiple CSV files or no CSV files
        PermissionError: If the file cannot be accessed due to permission issues
    """
    if filename is None:
        path = open_file(folder, "CSV files (*.csv)")
    else:
        path = os.path.join(folder, filename)
    if path:
        try:
            with open(path, "r") as f:
                return list(csv.reader(f)), path
        except FileNotFoundError:
            logger.warning(f"Failed to read CSV file from {path}: file not found")
            return None
        except csv.Error as e:
            logger.warning(f"Failed to read CSV file from {path}: {e}")
            return None
    else:
        logger.warning(f"No file selected")
        return None
