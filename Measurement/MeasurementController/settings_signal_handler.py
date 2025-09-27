from ..helper_functions import remove_zeros, str_to_bool, refresh_obj_view, is_equal_frequencies
import numpy as np
from .abstract_signal_handler import SignalHandler
from .keys import Keys
from PyQt6.QtWidgets import QCheckBox, QLineEdit, QRadioButton


from System.logger import get_logger
logger = get_logger(__name__)

class SettingsSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def handler(meas_controller, message):
        logger.debug(f"SettingsSignalHandler")
        args = meas_controller, message
        SettingsSignalHandler.gen_handler(*args)
        SettingsSignalHandler.sa_handler(*args)
        SettingsSignalHandler.osc_handler(*args)
        SettingsSignalHandler.recalc_handler(*args)
        
        args = meas_controller.ig_controller, message
        SettingsSignalHandler.plot_handler(*args)

        SettingsSignalHandler.set_elements_unchanged(meas_controller)

    @staticmethod
    def gen_handler(meas_controller, message):
        # Gen settings
        for key, param in Keys.gen.items():
            if key in message:
                SettingsSignalHandler.update_gen_elem(meas_controller, message, key, param)

    @staticmethod
    def sa_handler(meas_controller, message):
        # SA settings
        for key, param in Keys.sa.items():
            if key in message:
                SettingsSignalHandler.update_sa_elem(meas_controller, message[key], param)

        if 'PRECISE' in message:
            meas_controller.enable_precise(str_to_bool(message['PRECISE']))

    @staticmethod
    def osc_handler(meas_controller, message):
        # Osc settings
        for key, param in Keys.osc.items():
            if key in message:
                SettingsSignalHandler.update_osc_elem(meas_controller, message[key], param)

        elem = meas_controller.view.elem
        if "HIGH_RES" in message:
            elem['HIGHT_RES_BOX'].setChecked(message["HIGH_RES"])
        if "IMPEDANCE_50OHM" in message:
            status = message["IMPEDANCE_50OHM"]
            elem['RB_50OHM'].setChecked(status)
            elem['RB_MEG'].setChecked(not status) 
        if "COUPLING_DC" in message:
            status = message["COUPLING_DC"]
            elem['RB_DC'].setChecked(status)
            elem['RB_AC'].setChecked(not status)
        if 'CHANNEL' in message:
            elem[f'RB_CH{message["CHANNEL"]}'].setChecked(True)

    @staticmethod
    def recalc_handler(meas_controller, message):
        if "RECALC_ATTEN" in message:
             meas_controller.enable_recalc(message["RECALC_ATTEN"])

    @staticmethod
    def plot_handler(ig_controller, message):
        if "RF_LEVELS" in message:
            level_min, level_max, _ = message["RF_LEVELS"]
            ig_controller.clear_plot()

            ig_controller.view.figure1.ax.set_xlim(level_min, level_max)
            ig_controller.view.figure1.canvas.draw_idle()

            # meas_controller.view.plot.figure2.ax.set_xlim(level_min, level_max)
            ig_controller.view.figure2.canvas.draw_idle()
        if "RF_FREQUENCIES" in message:
            freq_min, freq_max, points = message["RF_FREQUENCIES"]
            if is_equal_frequencies(freq_min, freq_max):
                ig_controller.add_selector_point(freq_min)
            else:
                frequencies = np.linspace(freq_min, freq_max, points)
                for frequency in frequencies:
                    ig_controller.add_selector_point(frequency)

    @staticmethod
    def update_gen_elem(meas_controller, message, mes_key, param):
        elem_key, unit = param
        if unit in meas_controller.units:
             dev = meas_controller.units[unit]

        value_min, value_max, points = message.get(f'{mes_key}', (None, None, None))
        elem = meas_controller.view.elem
        elem[f'{elem_key}_MIN_LINE'].setText(remove_zeros(value_min/dev))
        elem[f'{elem_key}_MAX_LINE'].setText(remove_zeros(value_max/dev))
        elem[f'{elem_key}_POINTS_LINE'].setText(remove_zeros(points))

    @staticmethod
    def update_sa_elem(meas_controller, value, param):
        elem_key, unit = param
        if unit in meas_controller.units:
             dev = meas_controller.units[unit]
        meas_controller.view.elem[f'{elem_key}_LINE'].setText(remove_zeros(value/dev))
                
    @staticmethod
    def update_osc_elem(meas_controller, value, param):
        SettingsSignalHandler.update_sa_elem(meas_controller, value, param)

    @staticmethod
    def set_elements_unchanged(meas_controller) -> None:
        """
        Reset the style of the elements to their default state after submitting the input parameters.
        """
        elem = meas_controller.view.elem
        for element in elem.values():
            if isinstance(element, (QLineEdit, QCheckBox, QRadioButton)):
                element.setProperty("class", "")
                refresh_obj_view(element)
        meas_controller.unlock_start_btn()

            
