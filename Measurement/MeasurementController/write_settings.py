from .keys import Keys

from System.logger import get_logger
logger = get_logger(__name__)


class WriteSettings():
    def __init__(self):
        pass

    @staticmethod
    def view_to_model(meas_controller):
        settings = meas_controller.model.settings
        elem = meas_controller.view.elem

        for key, param in Keys.gen.items():
            settings[key] = WriteSettings.write_gen_settings(meas_controller, param)

        for key, param in Keys.sa.items():
            settings[key] = WriteSettings.write_sa_settings(meas_controller, param)

        settings['PRECISE'] = elem['PRECISE_ENABLED'].isChecked()
        settings['RECALC_ATTEN'] = elem['RECALC_ATT'].isChecked()
        
        for key, param in Keys.osc.items():
            settings[key] = WriteSettings.write_osc_settings(meas_controller, param)

        settings['HIGH_RES'] = elem['HIGHT_RES_BOX'].isChecked()
        settings['IMPEDANCE_50OHM'] = elem['RB_50OHM'].isChecked()
        settings['COUPLING_DC'] = elem['RB_DC'].isChecked()
        settings['CHANNEL'] = next((i for i in [1, 2, 3, 4] if elem[f'RB_CH{i}'].isChecked()), None)


        
    @staticmethod
    def write_gen_settings(meas_controller, param):
        elem_key, unit = param
        if unit in meas_controller.units:
             multiplier = meas_controller.units[unit]

        elem = meas_controller.view.elem
        value_min = float(elem[f'{elem_key}_MIN_LINE'].text()) * multiplier
        value_max = float(elem[f'{elem_key}_MAX_LINE'].text()) * multiplier
        points = int(elem[f'{elem_key}_POINTS_LINE'].text())

        return value_min, value_max, points

    @staticmethod
    def write_sa_settings(meas_controller, param):
        elem_key, unit = param
        if unit in meas_controller.units:
             multiplier = meas_controller.units[unit]
             try:
                return float(meas_controller.view.elem[f'{elem_key}_LINE'].text())* multiplier
             except ValueError:
                logger.warning(f"Invalid value for {elem_key}_LINE")
                raise
             
    @staticmethod
    def write_osc_settings(meas_controller, param):
        return WriteSettings.write_sa_settings(meas_controller, param)
    
        