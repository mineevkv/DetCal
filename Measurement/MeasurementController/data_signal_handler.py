from System.logger import get_logger
logger = get_logger(__name__)

from .abstract_signal_handler import SignalHandler

class DataSignalHandler(SignalHandler):
    
    def __init__(self):
        super().__init__()

    @staticmethod
    def handler(meas_controller, message):
        logger.debug(f"DataSignalHandler")
        if 'DATA' in message:
            if meas_controller.check_recalc():
                meas_controller.model.recalc_data()
        if 'POINT' in message:
            if (meas_controller.view.plot.frequency - message['POINT'][0]) < 100: # 100 Hz tolerance
                meas_controller.view.plot.figure1.add_point(message['POINT'][1], message['POINT'][3]*1e3)
                meas_controller.view.plot.figure2.add_point(message['POINT'][2], message['POINT'][3]*1e3, autoscale=True)
        if 'FREQUENCY' in message:
            meas_controller.view.plot.frequency = message['FREQUENCY']
            meas_controller.view.plot.clear_plot()
            meas_controller.view.plot.set_selector()
        if 'RECALC_DATA' in message:
            pass