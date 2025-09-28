from PyQt6.QtCore import pyqtSignal, QThread

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementThread(QThread):
    """Set measurement process in a separate thread"""
    finished_signal = pyqtSignal()
    
    def __init__(self, meas_model):
        super().__init__()
        self.parent = meas_model
        
    def run(self):
        try:
            self.parent.start_measurement()  
        except Exception as e:
            logger.error(f"Measurement process error: {e}")
        finally:
            self.finished_signal.emit()