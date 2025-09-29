from .instr_sheet import InstrumentSheet

from PyQt6.QtWidgets import  QGroupBox
from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QApplication, 
    QGridLayout, QLabel, QLineEdit, QGroupBox)


from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class SpectrumAnalyzerSheet(InstrumentSheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)
        
        center_freq_row = self.ip_row + 2
        span_row = center_freq_row + 1
        rbw_row = span_row + 2
        vbw_row = rbw_row
        single_row = center_freq_row

        vbw_col = 19

        edit_line_width_small = 43
        label_width = 130
        rbw_label_width = 60

        # INPUT PARAMETERS
        self.add_control_elem('CENTER_FREQ', self.zero_col, center_freq_row, 'CENTER FREQ, MHz:', '1000', label_width)
        self.add_control_elem('SPAN', self.zero_col, span_row, 'SPAN, MHz:', '1', label_width)
        self.add_control_elem('RBW', self.zero_col, rbw_row, 'RBW, kHz:', '10', rbw_label_width, edit_line_width_small)
        self.add_control_elem('VBW', vbw_col, vbw_row, 'VBW, kHz:', '10', rbw_label_width, edit_line_width_small)

        self.add_big_btn('SINGLE', 31, single_row, 'SINGLE')