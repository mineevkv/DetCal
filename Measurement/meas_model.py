from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog
from Instruments.Initializer import InstrumentInitializer

import os
import json

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementModel(QObject):
    data_changed = pyqtSignal(dict)  # Signal to notify data changes
    settings_changed = pyqtSignal(dict)
    settings_filename = 'meas_settings'
    settings_folder = 'Settings'
    
    def __init__(self):
        super().__init__()

        self.gen = None
        self.sa = None
        self.osc = None

        self.initializer = InstrumentInitializer()
        self.initializer.instr_list.connect(self.init_instruments)

    def start_initialization(self):
        """Start the instrument initialization process"""
        if not self.initializer.isRunning():
            self.initializer.start()

    def init_instruments(self, gen, sa, osc, error):
        """Handle completion of instrument initialization"""
        if error:
            logger.debug('MeasModel_init_complete with error:', error)
            return
        
        if gen is not None:
            self.gen = gen
            self.data_changed.emit({'Gen': gen})
        if sa is not None:
            self.sa = sa
            self.data_changed.emit({'SA': sa})
        if osc is not None:
            self.osc = osc
            self.data_changed.emit({'Osc': osc})


        # TODO: emit the data_changed signal with the initialized instruments
        
    def offline_mode(self, mode):
        if mode:
            self.initializer.offline_debug = True
        else:    
            self.initializer.offline_debug = False

    def load_settings_from_file(self):
        logger.debug('MeasModel: load settings from file')
        settings = self.load_settings_file()
        if not settings == {}:
            self.settings = settings
            logger.info(f"Load settings")
            self.settings_changed.emit(self.settings)
        # self.update_settings_elem()

    def load_settings_file(self):
        filename, _ = QFileDialog.getOpenFileName(
            caption="Load settings file",
            directory=self.settings_folder,
            filter="JSON files (*.json)"
        )
        settings =  dict()
        if filename:
            try:
                with open(filename, 'r') as f:
                    settings = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load settings from {filename}: {e}")
        else:
            logger.warning(f"No file selected")
        
        return settings