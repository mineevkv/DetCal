from PyQt6.QtCore import QObject
from .meas_model import MeasurementModel
from GUI.main_window import MainWindow

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementController(QObject):
    def __init__(self):
        super().__init__()
        self.model = MeasurementModel()
        self.view = MainWindow()

        # self.connect_signals()
        # self.update_view()

    def run(self):
        logger.debug('GUI running')
        self.view.show()