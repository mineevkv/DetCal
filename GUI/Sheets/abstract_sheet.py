from PyQt6.QtWidgets import (
    QWidget, QPushButton, QApplication, QCheckBox, QProgressBar, QRadioButton,
    QGridLayout, QLabel, QLineEdit, QGroupBox)

from PyQt6 import QtCore

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class Sheet:    
    def __init__(self, main_window): 
        self.layout = main_window.get_layout()
        self._margin_top = 10
        self._margin_left = 11

        self._zero_col = 0
        self._zero_row = 0

        self._row_hight = 25
        self._col_width = 10


        self.elem = getattr(self, 'elem', {}) # existing condition
        self._elem_hight = 20

        self.box = QGroupBox("Empty sheet") # existing condition

        # Default grid for placing elements
        self.x_col = [x for x in range(self.margin_left, main_window.width() - self.margin_left, self.col_width)]
        self.y_row = [y for y in range(self.margin_top, main_window.height() - self.margin_top, self.row_hight)]

    @property
    def col_width(self) -> int:
        """Return the width of a column in the sheet"""
        return self._col_width
    
    @property
    def row_hight(self) -> int:
        """Return the height of a row in the sheet"""
        return self._row_hight
    
    @property
    def margin_top(self) -> int:
        """Return the top margin of the sheet"""
        return self._margin_top
    
    @property
    def margin_left(self) -> int:
        """Return the left margin of the sheet"""
        return self._margin_left
    
    @property
    def zero_col(self) -> int:
        """Return the index of the first column in the sheet"""
        return self._zero_col
    
    @property
    def zero_row(self) -> int:
        """Return the index of the first row in the sheet"""
        return self._zero_row

    @property
    def elem_hight(self) -> int:
        """Return the height of an element in the sheet"""
        return self._elem_hight

    def get_widget(self):
        """Return the main widget of the sheet"""
        return self.box
    
    def hide(self):
        self.box.hide()

    def add_label(self, key, col, row, text, width=85):
        label = self.elem[f'{key}_LABEL'] = QLabel(f"{text}",parent=self.box)
        label.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_hight))
        return label

    def add_line_edit(self, key, col, row, value, width=63):
        line_edit = self.elem[f'{key}_LINE'] = QLineEdit(f"{value}", parent=self.box)
        line_edit.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_hight))
        line_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        return line_edit

    def add_clickable_line_edit(self, key, col, row, value, width=63):
        line_edit = self.elem[f'{key}_CLICKLINE'] = ClickableLineEdit(f"{value}", parent=self.box)
        line_edit.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_hight))
        line_edit.setProperty('class', 'ip_line')
        line_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        return line_edit
        
    def add_btn(self, key, col, row, text, width=60):
        btn = self.elem[f'BTN_{key}'] = QPushButton(f"{text}", parent=self.box)
        btn.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_hight))
        return btn

    def add_custom_btn(self, key,  col, row, text, width, hight, elem_class = None):
        btn = self.add_btn(key, col, row, text, width)
        btn.setFixedHeight(hight)
        if elem_class is not None: 
            btn.setProperty('class', elem_class)
        return btn

    def add_check_box(self, key, col, row, text):
        check_box = self.elem[key] = QCheckBox(parent=self.box, text=text)
        check_box.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], 200, 20))
        return check_box
    
    def add_radio_btn(self, key, col, row, text, width=90):
        radio_btn = self.elem[key] = QRadioButton(parent=self.box, text=text)
        radio_btn.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], width, 20))
        radio_btn.setChecked(False)
        return radio_btn
    
    def add_progress_bar(self, key, col, row, width, hight):
        progress_bar = self.elem[key] = QProgressBar(parent=self.box)
        progress_bar.setGeometry(QtCore.QRect(self.x_col[col] , self.y_row[row], width, hight))
        progress_bar.setRange(0, 100)
        return progress_bar
    
    def shift_position(self, elem, shift_x=0, shift_y=0):
        elem.move(elem.x() + shift_x, elem.y() + shift_y)

    def add_frame(self, key, col, row, dx, dy, width, hight, classname):
        frame = self.elem[f'{key}_FRAME'] = self.frame_ch = QWidget(self.box)
        frame.setProperty('class', f'{classname}')
        frame.setGeometry(self.x_col[col] - dx, self.y_row[row] - dy, width, hight)
        frame.setAutoFillBackground(True)
    
    def cleanup(self):
        """Safe cleanup method to be called explicitly"""
        if hasattr(self, 'box') and self.box:
            self.box.deleteLater()
            self.box = None


