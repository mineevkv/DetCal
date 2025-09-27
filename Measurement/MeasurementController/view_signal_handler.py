
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
        keys = ('SAVE_SETTINGS',
                'LOAD_SETTINGS',
                'SET_DEFAULT',
                'START',
                'STOP',
                'SAVE_RESULT',
                'LOAD_S21_GEN_SA',
                'LOAD_S21_GEN_DET',
                'APPLY'
        )
        
        for key in keys:
                meas_controller.btn_clicked_connect(key, getattr(meas_controller, f'btn_{key}_click', None))

        elem['PRECISE_ENABLED'].stateChanged.connect(meas_controller.change_state_precise)
        elem['UNLOCK_STOP'].stateChanged.connect(meas_controller.unlock_stop_btn)
        elem['RECALC_ATT'].stateChanged.connect(meas_controller.change_state_recalc)

        for element in elem.values():
            if isinstance(element, QLineEdit):
                element.textChanged.connect(lambda _, object=element: ViewSignalHandler.element_changed(meas_controller, object))
            elif isinstance(element, (QRadioButton, QCheckBox)):
                if isinstance(element, QCheckBox) and element is elem['UNLOCK_STOP']:
                    continue
                element.toggled.connect(lambda _, object=element: ViewSignalHandler.element_changed(meas_controller, object))

    def element_changed(meas_controller, object):
        if isinstance(object, QLineEdit):
            object.setProperty('class', 'line_changed')
        elif isinstance(object, (QCheckBox, QRadioButton)):
            object.setProperty('class', 'radiocheck_changed')

        refresh_obj_view(object)
        meas_controller.lock_start_btn()