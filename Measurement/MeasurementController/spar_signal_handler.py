from ..helper_functions import refresh_obj_view
from .abstract_signal_handler import SignalHandler

from System.logger import get_logger
logger = get_logger(__name__)

class SparSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def handler(meas_controller, message):
        if 's21_gen_sa' in message:
            elem = meas_controller.view.elem['s21_gen_sa_file_label']
            elem.setText(message['s21_gen_sa'])
            elem.setProperty('class', 's21_label_file')
            refresh_obj_view(elem)
        if 's21_gen_det' in message:
            elem = meas_controller.view.elem['s21_gen_det_file_label']
            elem.setText(message['s21_gen_det'])
            elem.setProperty('class', 's21_label_file')
            refresh_obj_view(elem)