from PyQt6 import QtCore
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QApplication, 
    QGridLayout, QLabel, QLineEdit, QGroupBox)

from .abstract_sheet import Sheet
from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class InstrumentSheet(Sheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)
        self.ip = "NoIP"

        self.add_instrument_sheet()
        self.add_ip_field()


    def add_instrument_sheet(self):
        """Initialize instrument sheet in the main window"""
        self.box = QGroupBox("Instrument type")

        self.add_label("model", 20, self.zero_row, "Model", 100).setStyleSheet(f"color: {YELLOW}; font-weight: bold")

    def add_ip_field(self):
        self.ip_row = 2
        key = 'ip'
        self.add_label(key , self.zero_col, self.ip_row, "IP:", 50)
        self.add_clickable_line_edit(key, 3, self.ip_row, f"{self.ip}", 93)
        self.add_btn(key, 13, self.ip_row, "Connect")
        self.add_label(f'{key}_status', 20, self.ip_row, "", 100)

    def add_control_elem(self, key, col, row, text, value, label_width=85, line_width=63, btn_width=60):
        col_label = col
        self.add_label(key, col_label, row, text, label_width)

        col_line = col+ label_width//10 + 1
        self.add_line_edit(key, col_line, row, value, line_width)

        col_btn = col_line + line_width//10 +1 
        self.add_btn(key, col_btn, row, 'Set', btn_width)

    def add_big_btn(self, key, col, row, text, width=60):
        btn = self.add_btn(key, col, row, text, width)
        btn .setStyleSheet(f"font-weight: bold")
        btn .setFixedHeight(45)



