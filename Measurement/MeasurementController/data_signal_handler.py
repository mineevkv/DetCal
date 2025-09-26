from System.logger import get_logger
logger = get_logger(__name__)

from .abstract_signal_handler import SignalHandler

class DataSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def handler(meas_controller, message):
        logger.debug(f"DataSignalHandler")
        if 'data' in message:
            if meas_controller.check_recalc():
                meas_controller.model.recalc_data()
        if 'point' in message:
            print(f"message['point'][0]: {message['point'][0]}")
            if (meas_controller.view.plot.frequency - message['point'][0]) < 100: # 100 Hz tolerance
                meas_controller.view.plot.figure1.add_point(message['point'][1], message['point'][3]*1e3)
                meas_controller.view.plot.figure2.add_point(message['point'][2], message['point'][3]*1e3, autoscale=True)
        if 'frequency' in message:
            meas_controller.view.plot.frequency = message['frequency']
            meas_controller.view.plot.clear_plot()
            meas_controller.view.plot.set_selector()
        if 'recalc_data' in message:
            pass