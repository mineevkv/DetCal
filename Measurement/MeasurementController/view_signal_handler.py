
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QRadioButton
from .abstract_signal_handler import SignalHandler

from ..helper_functions import refresh_obj_view

from System.logger import get_logger
logger = get_logger(__name__)

class ViewSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    def init(meas_controller):
        elem =meas_controller.view.elem
        keys = ('save_settings',
                'load_settings',
                'set_default',
                'start',
                'stop',
                'save_result',
                'load_s21_gen_sa',
                'load_s21_gen_det',
                'apply'
        )
        
        for key in keys:
                meas_controller.btn_clicked_connect(key, getattr(meas_controller, f'btn_{key}_click', None))

        elem['precise_enabled'].stateChanged.connect(meas_controller.change_state_precise)
        elem['unlock_stop'].stateChanged.connect(meas_controller.unlock_stop_btn)
        elem['recalc_att'].stateChanged.connect(meas_controller.change_state_recalc)

        for element in elem.values():
            if isinstance(element, QLineEdit):
                element.textChanged.connect(lambda _, object=element: ViewSignalHandler.element_changed(meas_controller, object))
            elif isinstance(element, (QRadioButton, QCheckBox)):
                if isinstance(element, QCheckBox) and element is elem['unlock_stop']:
                    continue
                element.toggled.connect(lambda _, object=element: ViewSignalHandler.element_changed(meas_controller, object))

    def element_changed(meas_controller, object):
        if isinstance(object, QLineEdit):
            object.setProperty('class', 'line_changed')
        elif isinstance(object, (QCheckBox, QRadioButton)):
            object.setProperty('class', 'radiocheck_changed')

        refresh_obj_view(object)
        meas_controller.lock_start_btn()