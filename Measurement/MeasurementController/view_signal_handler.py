
from PyQt6.QtWidgets import QLineEdit, QCheckBox, QRadioButton
from .abstract_signal_handler import SignalHandler

from ..helper_functions import refresh_obj_view, btn_clicked_connect

from System.logger import get_logger
logger = get_logger(__name__)

class ViewSignalHandler(SignalHandler):
    """ Handler for view-related signals. """
    def __init__(self) -> None:
        super().__init__()

    def init(meas_controller: object) -> None:
        """ Connect view elements to their respective handlers."""
        elem =meas_controller.view.elem
        keys = ('SAVE_SETTINGS',
                'LOAD_SETTINGS',
                'SET_DEFAULT',
                'START',
                'STOP',
                'SAVE_RESULT',
                'LOAD_S21_GEN_SA',
                'LOAD_S21_GEN_DET',
                'APPLY',
                "RECALC_EXTERNAL"
        )
        
        for key in keys:
                btn_clicked_connect(meas_controller, key, getattr(meas_controller.buttons, f'btn_{key.lower()}_click', None))

        elem['PRECISE_ENABLED'].stateChanged.connect(meas_controller.change_state_precise)
        elem['UNLOCK_STOP'].stateChanged.connect(meas_controller.unlock_stop_btn)
        elem['RECALC_ATT'].stateChanged.connect(meas_controller.change_state_recalc)
        elem['REF_LEVEL_ENABLED'].stateChanged.connect(meas_controller.change_state_ref_line)

        for element in elem.values():
            if isinstance(element, QLineEdit):
                element.textChanged.connect(lambda _, object=element: ViewSignalHandler.element_changed(meas_controller, object))
            elif isinstance(element, (QRadioButton, QCheckBox)):
                if isinstance(element, QCheckBox) and element is elem['UNLOCK_STOP']:
                    continue
                element.toggled.connect(lambda _, object=element: ViewSignalHandler.element_changed(meas_controller, object))

        points_lines = ('FREQ_POINTS_LINE', 'LEVEL_POINTS_LINE')
        for key in points_lines:
            elem[key].textChanged.connect(lambda _, object=key: ViewSignalHandler.points_line_changed(meas_controller, object))

        min_lines = ('FREQ_MIN_LINE', 'LEVEL_MIN_LINE')
        for key in min_lines:
            elem[key].textChanged.connect(lambda _, object=key: ViewSignalHandler.min_line_changed(meas_controller, object))

    @staticmethod
    def element_changed(meas_controller: object, element: object) -> None:
        """ Handle changes in view elements and update their properties."""
        if isinstance(element, QLineEdit):
            element.setProperty('class', 'line_changed')
        elif isinstance(element, (QCheckBox, QRadioButton)):
            element.setProperty('class', 'radiocheck_changed')

        refresh_obj_view(element)
        meas_controller.lock_start_btn()

    @staticmethod
    def points_line_changed(meas_controller: object, key: str) -> None:
        """ Handle changes in points line elements and update max line state."""
        elem = meas_controller.view.elem
        if elem[key].text() == '1':
            ViewSignalHandler.max_line_off(elem, key)
        else:
            ViewSignalHandler.max_line_on(elem, key)

    def max_line_off(elem: object, key: str) -> None:
        """ Disable max line elements."""
        descriptor = key.split('_')[0]
        max_line = elem[f'{descriptor}_MAX_LINE']
        max_label = elem[f'{descriptor}_MAX_LABEL']
        max_line.setEnabled(False)
        max_label.setEnabled(False)

    def max_line_on(elem: object, key: str) -> None:
        """ Enable max line elements."""
        descriptor = key.split('_')[0]
        max_line = elem[f'{descriptor}_MAX_LINE']
        max_label = elem[f'{descriptor}_MAX_LABEL']
        max_line.setEnabled(True)
        max_label.setEnabled(True)

    @staticmethod
    def min_line_changed(meas_controller: object, key: str) -> None:
        """ Handle changes in min line elements and update points line state."""
        descriptor = key.split('_')[0]
        if meas_controller.view.elem[f'{descriptor}_MAX_LINE'].isEnabled():
            return
        else:
            ViewSignalHandler.points_line_changed(meas_controller, f'{descriptor}_POINTS_LINE')


