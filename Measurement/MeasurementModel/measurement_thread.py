from PyQt6.QtCore import pyqtSignal, QThread

from System.logger import get_logger

logger = get_logger(__name__)


class MeasurementThread(QThread):
    """
    This class is used to move the measurement process to a separate thread.
    This is necessary because the measurement process can take a long time and
    would otherwise block the GUI.

    Args:
         meas_model: The measurement model containing the general business logic about the measurement process
    """

    finished_signal = pyqtSignal()

    def __init__(self, meas_model: object) -> None:
        super().__init__()
        self.model = meas_model

    def run(self) -> None:
        """
        Run the measurement process in a separate thread.

        This method is called when the thread is started.
        It calls the `start_measurement` method of the parent object and
        emits the `finished_signal` when the measurement process is finished.
        """
        try:
            logger.debug("Starting measurement thread")
            self.model.start_measurement()
        except Exception as e:
            logger.error(f"Measurement process failed: {e}")
        finally:
            logger.debug("Measurement thread finished")
            self.finished_signal.emit()

    def stop(self) -> None:
        """Safely stop the measurement thread."""
        self.requestInterruption()  # QThread built-in method
        self.wait(5000)  # 5 seconds for graceful termination
