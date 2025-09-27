
from System.logger import get_logger
logger = get_logger(__name__)

class SettingsValidator():
    def __init__(self, view) -> None:
        self.view = view

    def check(self) -> bool:

        if not self.check_frequencies():
            return False
        if not self.check_levels():
            return False
        if not self.check_sweep_points():
            return False
        if not self.check_span():
            return False
        if not self.check_rbw():
            return False
        if not self.check_vbw():
            return False
        if not self.check_ref_level():
            return False
        if not self.check_recalc_attenuation():
            return False
        if not self.check_horizontal_scale():
            return False
        return True

    def check_frequencies(self) -> bool:
        if not self.validate_positive_float('FREQ_MIN_LINE'):
            return False
        if not self.validate_positive_float('FREQ_MAX_LINE'):
            return False
        if not self.validate_positive_int('FREQ_POINTS_LINE'):
            return False
        if not self.check_min_max('FREQ_MIN_LINE', 'FREQ_MAX_LINE'):
            return False
        return True

    def check_levels(self) -> bool:
        if not self.validate_float('LEVEL_MIN_LINE'):
            return False
        if not self.validate_float('LEVEL_MAX_LINE'):
            return False
        if not self.validate_positive_int('LEVEL_POINTS_LINE'):
            return False
        if not self.check_min_max('LEVEL_MIN_LINE', 'LEVEL_MAX_LINE'):
            return False
        return True

    def check_sweep_points(self) -> bool:
        if not self.validate_positive_int('SWEEP_POINTS_LINE'):
            return False
        return True
        
    def check_span(self) -> bool:
        if not self.validate_positive_float('SPAN_LINE'):
            return False
        if not self.validate_positive_float('SPAN_PRECISE_LINE'):
            return False
        return True

    def check_rbw(self) -> bool:
        if not self.validate_positive_float('RBW_LINE'):
            return False
        if not self.validate_positive_float('RBW_PRECISE_LINE'):
            return False
        return True

    def check_vbw(self) -> bool:
        if not self.validate_positive_float('VBW_LINE'):
            return False
        if not self.validate_positive_float('VBW_PRECISE_LINE'):
            return False
        return True

    def check_ref_level(self) -> bool:
        if not self.validate_float('REF_LEVEL_LINE'):
            return False
        return True

    def check_horizontal_scale(self) -> bool:
        if not self.validate_float('HOR_SCALE_LINE'):
            return False
        return True

    def check_recalc_attenuation(self) -> bool:
        text = self.view.elem['S21_GEN_SA_FILE_LABEL'].text()
        if text == 'No S21 file':
            return False
        text = self.view.elem['S21_GEN_DET_FILE_LABEL'].text()
        if text == 'No S21 file':
            return False
        return True

    def validate_float(self, key: str) -> bool:
        text = self.view.elem[key].text()
        try:
            float(text)
            return True
        except ValueError as e:
            logger.error(f"Error setting {key}: {e}")
            return False
        
    def validate_positive_float(self, key: str) -> bool:
        if self.validate_float(key):
            value = float(self.view.elem[key].text())
            if value > 0:
                return True
            else:
                logger.error(f"Error setting {key}: value must be positive")
                return False
        else:
            return False
    
    def validate_int(self, key: str) -> bool:
        text = self.view.elem[key].text()
        try:
            if '.' in text:
                logger.error(f"Error setting {key}: value must be an integer")
                return False
            int(text)
            return True
        except ValueError as e:
            logger.error(f"Error setting {key}: {e}")
            return False
        
    def validate_positive_int(self, key: str) -> bool:
        if self.validate_int(key):
            value = int(self.view.elem[key].text())
            if value > 0:
                return True
            else:
                logger.error(f"Error setting {key}: value must be positive")
                return False
        else:
            return False

    def get_value(self, key: str) -> float:
        try:
            value = float(self.view.elem[key].text())
            return value
        except ValueError as e:
            logger.error(f"Error setting {key}: {e}")
            return None
        
    def check_min_max(self, key_min: str, key_max: str) -> bool:
            if self.get_value(key_max) < self.get_value(key_min):
                logger.error(f"{key_max} value must be greater than {key_min}")
                return False
            else:
                return True


    
