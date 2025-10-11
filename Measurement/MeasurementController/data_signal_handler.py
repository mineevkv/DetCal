from Measurement.helper_functions import is_equal

from System.logger import get_logger

logger = get_logger(__name__)

from .abstract_signal_handler import SignalHandler


class DataSignalHandler(SignalHandler):
    """ Handler for data-related signals. """
    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def handler(meas_controller: object, message: dict) -> None:
        """ Handle signals from the instrument and update the GUI accordingly."""
        logger.debug(f"DataSignalHandler")

        if "DATA" in message:
            if meas_controller.check_recalc():
                meas_controller.model.recalc_data()
        if "POINT" in message:
            if is_equal(
                meas_controller.ig_controller.frequency, message["POINT"][0], 100
            ):  # 100 Hz tolerance
                meas_controller.ig_controller.view.figure1.add_point(
                    message["POINT"][1],
                    message["POINT"][3] / meas_controller.units["mV"],
                )
                meas_controller.ig_controller.view.figure2.add_point(
                    message["POINT"][2],
                    message["POINT"][3] / meas_controller.units["mV"],
                    autoscale=True,
                )
        if "FREQUENCY" in message:
            meas_controller.ig_controller.frequency = message["FREQUENCY"]
            meas_controller.ig_controller.clear_plot()
            meas_controller.ig_controller.set_selector()

        if "RECALC_DATA" in message:
            pass
