from System.logger import get_logger

logger = get_logger(__name__)

class ValuesValidator:
    """ Validator for different types of values. """
    def __init__(self) -> None:
        pass

    @staticmethod
    def is_float(s: str) -> bool:
        """ Validate if the text is a float."""
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_int(s: str) -> bool:
        """ Validate if the text is an integer."""
        try:
            int(s)
            return True
        except ValueError:
            return False