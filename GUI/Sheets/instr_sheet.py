

from .abstract_sheet import Sheet
from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class InstrumentSheet(Sheet):

    
    def __init__(self, main_layout):
        super().__init__(main_layout)
        self.ip = "NoIP"

