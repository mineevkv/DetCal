from .instr_sheet import InstrumentSheet
from PyQt6.QtWidgets import  QGroupBox

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class GeneratorSheet(InstrumentSheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)
        self.box.setTitle("Microwave Generator")

        freq_row = self.ip_row + 2
        level_row = freq_row + 1
        rf_row = freq_row

        # OUTPUT PARAMETERS
        self.add_control_elem('freq', self.zero_col, freq_row, 'FREQ, MHz:', '1000')
        self.add_control_elem('level', self.zero_col, level_row, 'LEVEL, dBm:', '-50')
        self.add_big_btn('rf_on', 31, rf_row, 'RF OFF')
