from PyQt6.QtCore import QObject
from Measurement.MeasurementModel.file_manager import FileManager
from Measurement.helper_functions import remove_zeros
from abc import abstractmethod

from System.logger import get_logger

logger = get_logger(__name__)


class Controller(QObject):
    """
    Abstract base class for controllers.

    This class provides a basic structure for controllers.

    Attributes:
        units (dict): A dictionary containing the units.

    """

    _abstract_methods = ["lock_control_elements", "unlock_control_elements"]

    def __init__(self) -> None:
        super().__init__()

        self._check_abstract_methods()
        self.units = FileManager.load_units()

    def value_to_str(self, value: float | int, unit: str, decimals: int = 0) -> str:
        """Converts a value to a string with the specified unit and decimals."""
        if value is None:
            logger.warning(f"None type mustn't be converted to string")
            return ""

        if unit in self.units:
            dev = self.units[unit]
            round_value = round(value / dev, decimals)
            return str(remove_zeros(round_value))
        else:
            logger.warning(f"Unknown unit: {unit}")
            return str(value)

    def _check_abstract_methods(self) -> None:
        """Checks if abstract methods are implemented in the derived class"""
        for method_name in self._abstract_methods:
            if getattr(type(self), method_name) is getattr(Controller, method_name):
                raise TypeError(
                    f"Can't instantiate abstract class {self.__class__.__name__} "
                    f"with abstract method {method_name}"
                )

    @abstractmethod
    def lock_control_elements(self) -> None:
        """Should be overridden in derived classes"""
        raise NotImplementedError("Method lock_control_elements must be implemented")

    @abstractmethod
    def unlock_control_elements(self) -> None:
        """Should be overridden in derived classes"""
        raise NotImplementedError("Method unlock_control_elements must be implemented")
