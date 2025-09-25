import csv
import os
import numpy as np
from PyQt6.QtWidgets import QFileDialog

from System.logger import get_logger
logger = get_logger(__name__)

def remove_zeros( input_string):
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

def str_to_bool(value):
    """Convert string to bool """
    if isinstance(value, str):
        value = value.lower()
        if value == 'true':
            return True
        elif value == 'false':
            return False
    return bool(value)

def refresh_obj_view(object_name):
    object_name.style().unpolish(object_name)
    object_name.style().polish(object_name)

def open_file(folder, filter=None):
    patn, _ = QFileDialog.getOpenFileName(
        caption="Open file",
        directory=folder,
        filter=filter
    )
    return patn

def get_s21(frequency, s21):
    freq = s21[0]
    magnitude = s21[1]
    return np.interp(frequency, freq, magnitude)

def read_csv_file(folder, filename=None):
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
            with open(path, 'r') as f: 
                return list(csv.reader(f)), path
        except FileNotFoundError:
            logger.warning(f"Failed to read CSV file from {path}: file not found")
        except csv.Error as e:
            logger.warning(f"Failed to read CSV file from {path}: {e}")
    else:
        logger.warning(f"No file selected")