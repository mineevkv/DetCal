from PyQt6.QtCore import QObject
from Measurement.MeasurementModel.file_manager import FileManager
from Measurement.helper_functions import remove_zeros

from System.logger import get_logger

logger = get_logger(__name__)


class Controller(QObject):
    """
    Abstract base class for controllers.

    This class provides a basic structure for controllers.

    Attributes:
        units (dict): A dictionary containing the units.

    """

    def __init__(self):
        super().__init__()

        self.units = FileManager.load_units()

    def value_to_str(self, value: float | int, unit: str) -> str:
        if value is None:
            logger.warning(f"None type mustn't be converted to string")
            return ""

        if unit in self.units:
            dev = self.units[unit]
            return str(remove_zeros(value / dev))
        else:
            logger.warning(f"Unknown unit: {unit}")
            return str(value)
