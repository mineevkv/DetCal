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

        self.zero_col = 0
        self.zero_row = 0

        self._row_hight = 25
        self._col_width = 10


        self.elem = getattr(self, 'elem', {}) # existing condition
        self.box = QGroupBox("Empty sheet") # existing condition

        # Default grid for placing elements
        self.x_col = [x for x in range(self._margin_left, main_window.width() - self._margin_left, self._col_width)]
        self.y_row = [y for y in range(self._margin_top, main_window.height() - self._margin_top, self._row_hight)]

    def get_widget(self):
        """Return the main widget of the sheet"""
        return self.box
