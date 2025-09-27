from Measurement.MeasurementModel.meas_model import MeasurementModel
from Measurement.MeasurementController.meas_controller import MeasurementController
from GUI.main_window import MainWindow

from System.logger import get_logger
logger = get_logger(__name__)

class MainController:
    def __init__(self):
        self.model = MeasurementModel()
        self.view = MainWindow()

        self.model.offline_mode(0)
        self.meas_controller = MeasurementController(self.model, self.view)
        self.view.show()
       