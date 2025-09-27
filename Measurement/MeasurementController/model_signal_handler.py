from System.logger import get_logger
logger = get_logger(__name__)

from .abstract_signal_handler import SignalHandler
from .data_signal_handler import DataSignalHandler
from .settings_signal_handler import SettingsSignalHandler
from .equipment_signal_handler import EquipmentSignalHandler
from .spar_signal_handler import SparSignalHandler
from .progress_signal_handler import ProgressSignalHandler

class ModelSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    def init(meas_controller):
        meas_controller.model.data_changed.connect(lambda message: DataSignalHandler.handler(meas_controller, message))
        meas_controller.model.equipment_changed.connect(lambda message: EquipmentSignalHandler.handler(meas_controller, message))
        meas_controller.model.settings_changed.connect(lambda message: SettingsSignalHandler.handler(meas_controller, message))
        meas_controller.model.progress_status.connect(lambda message: ProgressSignalHandler.handler(meas_controller, message))
        meas_controller.model.s21_file_changed.connect(lambda message: SparSignalHandler.handler(meas_controller, message))

    def handler(self, message):
        pass