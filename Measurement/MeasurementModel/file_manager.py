from Instruments.rsa5000vna_parcer import RSA506N_S21_Parser
from PyQt6.QtWidgets import QFileDialog
from ..helper_functions import read_csv_file, open_file
import os
import json
import numpy as np

from System.logger import get_logger
logger = get_logger(__name__)

class FileManager():
    def __init__(self, meas_model):
        self.model = meas_model


    def load_settings_from_file(self):
        logger.debug('MeasModel: load settings from file')
        settings = self.open_settings_file()
        if not settings == {}:
            self.model.settings = settings
            self.model.settings_changed.emit(self.model.settings)

    def load_settings(self, default=False):
        type = 'default ' if default else ''
        logger.debug(f"MeasModel: load {type}settings")
        settings =  dict()
        path = f"{self.model.settings_folder}/{self.model.settings_filename}{'_default' if default else ''}.json"
        try:
            with open(path, 'r') as f:
                settings = json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load {type}settings from {path}: {e}")

        if not settings == {}:
            self.model.settings = settings
            self.model.settings_changed.emit(self.model.settings) 

    def load_default_settings(self):
        self.load_settings(default=True)
 

    def open_settings_file(self):
        path, _ = QFileDialog.getOpenFileName(
            caption="Load settings file",
            directory=self.model.settings_folder,
            filter="JSON files (*.json)"
        )
        settings =  dict()
        if path:
            try:
                with open(path, 'r') as f:
                    settings = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load settings from {path}: {e}")
        else:
            logger.warning(f"No file selected")
        
        return settings
    
    def save_settings(self):
        with open(f"{self.model.settings_folder}/{self.model.settings_filename}.json", 'w') as f:
            json.dump(self.model.settings, f, indent=4)
            self.model.settings_changed.emit(self.model.settings)

    def load_s21_gen_sa(self, filename=None):
        try:
            # filename = 's21_gen_sa.trs'
            if filename is None:
                path = open_file(self.model.s21_folder, "S21 files (*.trs)")
                filename = os.path.basename(path)  
            self.model.s21_gen_sa = self.parse_s21_file(filename)
            self.model.s21_file_changed.emit({'s21_gen_sa' : filename})
        except Exception as e:
            logger.warning(f"Failed to load S21 file: {e}")

    def load_s21_gen_det(self, filename=None):
        try:
            if filename is None:
                path = open_file(self.model.s21_folder, "S21 files (*.trs)")
                filename = os.path.basename(path)  
            self.s21_gen_det = self.parse_s21_file(filename)
            print(filename)
            self.model.s21_file_changed.emit({'s21_gen_det' : filename})
        except Exception as e:
            logger.warning(f"Failed to load S21 file: {e}")

    def load_s21_files(self):
        self.load_s21_gen_sa('s21_gen_sa.trs')
        self.load_s21_gen_det('s21_gen_det.trs')


    def parse_s21_file(self, filename):
        parser = RSA506N_S21_Parser(os.path.join(self.model.s21_folder, filename))
        data = parser.parse_file()
        return (data['frequency'], data['magnitude_db'])
    
    def save_results(self):
        filename, _ = QFileDialog.getSaveFileName(
            caption="Save results",
            directory=os.path.join('results.csv'),
            filter="CSV files (*.csv)"
        )
        if filename:
            file_header = 'Gen Frequency (Hz), Gen Level (dBm), SA Level (dBm), Osc Voltage (V), S21 Gen-Sa (dB), S21 Gen-Det (dB), Det Level (dBm)'
            np.savetxt(filename, self.model.meas_data, delimiter=',', header=file_header)
            logger.info(f"Results saved to {filename}")
        else:
            logger.warning(f"No file selected")

    @staticmethod
    def load_units():
        with open('Settings/units.json', 'r') as f:
            return json.load(f)
