from System.logger import get_logger

logger = get_logger(__name__)

class ValuesValidator:
    def __init__(self):
        pass

    @staticmethod
    def is_float(s):
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_int(s):
        try:
            int(s)
            return True
        except ValueError:
            return False
        
    @staticmethod 
    def is_str(s):
        try:
            str(s)
            return True
        except ValueError:
            return False