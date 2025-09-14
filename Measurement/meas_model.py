from PyQt6.QtCore import QObject, pyqtSignal
from Instruments.Initializer import InstrumentInitializer

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementModel(QObject):
    data_changed = pyqtSignal(list)  # Signal to notify data changes
    
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
        
        self.gen = gen
        self.sa = sa
        self.osc = osc

        # TODO: emit the data_changed signal with the initialized instruments
        
    def offline_mode(self, mode):
        if mode:
            self.initializer.offline_debug = True
        else:    
            self.initializer.offline_debug = False