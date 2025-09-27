from System.logger import get_logger
logger = get_logger(__name__)


class WriteSettings():
    def __init__(self):
        pass

    @staticmethod
    def view_to_model(meas_controller):
        settings = meas_controller.model.settings
        elem = meas_controller.view.elem

        for key, param in meas_controller.gen_keys.items():
            settings[key] = WriteSettings.write_gen_settings(meas_controller, param)

        for key, param in meas_controller.sa_keys.items():
            settings[key] = WriteSettings.write_sa_settings(meas_controller, param)

        settings['Precise'] = elem['precise_enabled'].isChecked()
        settings['Recalc_atten'] = elem['recalc_att'].isChecked()
        
        for key, param in meas_controller.osc_keys.items():
            settings[key] = WriteSettings.write_osc_settings(meas_controller, param)

        settings['High_res'] = elem['hight_res_box'].isChecked()
        settings['Impedance_50Ohm'] = elem['rb_50ohm'].isChecked()
        settings['Coupling_DC'] = elem['rb_dc'].isChecked()
        settings['Channel'] = next((i for i in [1, 2, 3, 4] if elem[f'rb_ch{i}'].isChecked()), None)


        
    @staticmethod
    def write_gen_settings(meas_controller, param):
        elem_key, unit = param
        if unit in meas_controller.units:
             multiplier = meas_controller.units[unit]

        elem = meas_controller.view.elem
        value_min = float(elem[f'{elem_key}_min_line'].text()) * multiplier
        value_max = float(elem[f'{elem_key}_max_line'].text()) * multiplier
        points = int(elem[f'{elem_key}_points_line'].text())

        return value_min, value_max, points

    @staticmethod
    def write_sa_settings(meas_controller, param):
        elem_key, unit = param
        if unit in meas_controller.units:
             multiplier = meas_controller.units[unit]
             try:
                return float(meas_controller.view.elem[f'{elem_key}_line'].text())* multiplier
             except ValueError:
                logger.warning(f"Invalid value for {elem_key}_line")
                raise
             
    @staticmethod
    def write_osc_settings(meas_controller, param):
        return WriteSettings.write_sa_settings(meas_controller, param)
    
        