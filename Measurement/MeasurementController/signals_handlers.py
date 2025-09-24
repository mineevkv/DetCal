from abc import ABC, abstractmethod
from ..helper_functions import remove_zeros, str_to_bool, refresh_obj_view
import numpy as np

from System.logger import get_logger
logger = get_logger(__name__)

class SignalHandler(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def handler(self, message):
        pass

class DataSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

class EquipmentSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

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
        SettingsSignalHandler.plot_handler(*args)

    @staticmethod
    def gen_handler(meas_controller, message):
        # Gen settings
        for key, param in meas_controller.gen_keys.items():
            if key in message:
                meas_controller.update_gen_elem(message, key, param)

    @staticmethod
    def sa_handler(meas_controller, message):
        # SA settings
        for key, param in meas_controller.sa_keys.items():
            if key in message:
                meas_controller.update_sa_elem(message[key], param)

        if 'Precise' in message:
            meas_controller.enable_precise(str_to_bool(message['Precise']))

    @staticmethod
    def osc_handler(meas_controller, message):
        # Osc settings
        for key, param in meas_controller.osc_keys.items():
            if key in message:
                meas_controller.update_osc_elem(message[key], param)

        elem = meas_controller.view.meas.elem
        if "High_res" in message:
            elem['hight_res_box'].setChecked(message["High_res"])
        if "Impedance_50Ohm" in message:
            status = message["Impedance_50Ohm"]
            elem['rb_50ohm'].setChecked(status)
            elem['rb_meg'].setChecked(not status) 
        if "Coupling_DC" in message:
            status = message["Coupling_DC"]
            elem['rb_dc'].setChecked(status)
            elem['rb_ac'].setChecked(not status)
        if 'Channel' in message:
            elem[f'rb_ch{message["Channel"]}'].setChecked(True)

    @staticmethod
    def recalc_handler(meas_controller, message):
        if "Recalc_atten" in message:
             meas_controller.enable_recalc(message["Recalc_atten"])

    @staticmethod
    def plot_handler(meas_controller, message):
        if "RF_levels" in message:
            level_min, level_max, _ = message["RF_levels"]
            meas_controller.view.plot.figure1.clear_plot()
            meas_controller.view.plot.figure1.ax.set_xlim(level_min, level_max)
            meas_controller.view.plot.figure1.canvas.draw_idle()

            meas_controller.view.plot.figure2.clear_plot()
            # meas_controller.view.plot.figure2.ax.set_xlim(level_min, level_max)
            meas_controller.view.plot.figure2.canvas.draw_idle()
        if "RF_frequencies" in message:
            freq_min, freq_max, points = message["RF_frequencies"]
            if freq_min == freq_max:
                points = 1
                frequencies = freq_min
            else:
                frequencies = np.linspace(freq_min, freq_max, points)

            for frequency in frequencies:
                meas_controller.view.plot.add_selector_point(frequency)


            
