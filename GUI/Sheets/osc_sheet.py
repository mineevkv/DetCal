from .instr_sheet import InstrumentSheet

from PyQt6.QtWidgets import  QGroupBox

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class OscilloscopeSheet(InstrumentSheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)
        self.box.setTitle("Oscilloscope")