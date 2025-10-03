from ..helper_functions import refresh_obj_view
from .abstract_signal_handler import SignalHandler
from .settings_signal_handler import SettingsSignalHandler

from System.logger import get_logger

logger = get_logger(__name__)


class SparSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def handler(meas_controller, message):
        if "S21_GEN_SA_FILENAME" in message:
            elem = meas_controller.view.elem["S21_GEN_SA_FILE_LABEL"]
            elem.setText(message["S21_GEN_SA_FILENAME"])
            elem.setProperty("class", "s21_label_file")
            refresh_obj_view(elem)
        if "S21_GEN_DET_FILENAME" in message:
            elem = meas_controller.view.elem["S21_GEN_DET_FILE_LABEL"]
            elem.setText(message["S21_GEN_DET_FILENAME"])
            elem.setProperty("class", "s21_label_file")
            refresh_obj_view(elem)
            SettingsSignalHandler.update_max_det_level(meas_controller)
