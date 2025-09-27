from System.logger import get_logger
logger = get_logger(__name__)

from .abstract_signal_handler import SignalHandler

class ProgressSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    def handler(meas_controller, message):
        logger.debug(f"ProgressSignalHandler")
        elem = meas_controller.view.elem
        if 'FINISH' in message:
            meas_controller.unlock_control_elem()
            meas_controller.unlock_start_btn()
            meas_controller.progress_label_text('Finished')
            elem['PROGRESS'].setValue(0)
        if 'STOP' in message:
            meas_controller.unlock_control_elem()
            meas_controller.unlock_start_btn()
            meas_controller.progress_label_text('Stopped')

        if 'PROGRESS' in message:
           meas_controller.view.elem['PROGRESS'].setValue(int(message))
