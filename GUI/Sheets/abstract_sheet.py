from PyQt6.QtWidgets import  QApplication,  QGroupBox

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
    
    def cleanup(self):
        """Safe cleanup method to be called explicitly"""
        if hasattr(self, 'box') and self.box:
            self.box.deleteLater()
            self.box = None


