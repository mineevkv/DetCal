from ..helper_functions import remove_zeros, str_to_bool, refresh_obj_view, is_equal
import numpy as np
from .abstract_signal_handler import SignalHandler
from .keys import Keys
from PyQt6.QtWidgets import QCheckBox, QLineEdit, QRadioButton


from System.logger import get_logger

logger = get_logger(__name__)


class SettingsSignalHandler(SignalHandler):
    """Handler for settings-related signals."""

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def handler(meas_controller: object, message: dict) -> None:
        """Handle signals from the instrument and update the GUI accordingly."""
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
    def gen_handler(meas_controller: object, message: dict) -> None:
        """Handle signals from the signal generator and update the GUI accordingly."""
        # Gen settings
        for key, param in Keys.gen.items():
            if key in message:
                SettingsSignalHandler.update_gen_elem(
                    meas_controller, message, key, param
                )

        SettingsSignalHandler.update_max_det_level(meas_controller)

    @staticmethod
    def sa_handler(meas_controller: object, message: dict) -> None:
        """Handle signals from the spectrum analyzer and update the GUI accordingly."""
        # SA settings
        for key, param in Keys.sa.items():
            if key in message:
                SettingsSignalHandler.update_sa_elem(
                    meas_controller, message[key], param
                )

        if "PRECISE" in message:
            meas_controller.enable_precise(str_to_bool(message["PRECISE"]))
        if "REF_MANUAL" in message:
            meas_controller.enable_ref_line(str_to_bool(message["REF_MANUAL"]))

    @staticmethod
    def osc_handler(meas_controller: object, message: dict) -> None:
        """Handle signals from the oscilloscope and update the GUI accordingly."""
        # Osc settings
        for key, param in Keys.osc.items():
            if key in message:
                SettingsSignalHandler.update_osc_elem(
                    meas_controller, message[key], param
                )

        elem = meas_controller.view.elem
        if "HIGH_RES" in message:
            elem["HIGHT_RES_BOX"].setChecked(message["HIGH_RES"])
        if "IMPEDANCE_50OHM" in message:
            status = message["IMPEDANCE_50OHM"]
            elem["RB_50OHM"].setChecked(status)
            elem["RB_MEG"].setChecked(not status)
        if "COUPLING_DC" in message:
            status = message["COUPLING_DC"]
            elem["RB_DC"].setChecked(status)
            elem["RB_AC"].setChecked(not status)
        if "CHANNEL" in message:
            elem[f'RB_CH{message["CHANNEL"]}'].setChecked(True)

    @staticmethod
    def recalc_handler(meas_controller: object, message: dict) -> None:
        """Handle signals related to attenuation recalculations."""
        if "RECALC_ATTEN" in message:
            meas_controller.enable_recalc(message["RECALC_ATTEN"])

    @staticmethod
    def plot_handler(ig_controller: object, message: dict) -> None:
        """Handle signals related to the plot and update the GUI accordingly."""
        if "RF_LEVELS" in message:
            level_min, level_max, _ = message["RF_LEVELS"]
            ig_controller.clear_plot()
            ig_controller.view.figure1.ax.set_xlim(level_min, level_max)
            ig_controller.view.figure1.canvas.draw_idle()
            ig_controller.view.figure2.canvas.draw_idle()

        if "RF_FREQUENCIES" in message:
            freq_min, freq_max, points = message["RF_FREQUENCIES"]
            if is_equal(freq_min, freq_max):
                ig_controller.add_selector_point(freq_min)
            else:
                frequencies = np.linspace(freq_min, freq_max, points)
                for frequency in frequencies:
                    ig_controller.add_selector_point(frequency)

        if "FILENAME" in message:
            ig_controller.set_det_name(message["FILENAME"])

    @staticmethod
    def update_gen_elem(
        meas_controller: object, message: dict, mes_key: str, param: tuple
    ) -> None:
        """Update the GUI elements related to the generator settings."""
        elem_key, unit = param

        value_min, value_max, points = message.get(f"{mes_key}", (None, None, None))
        elem = meas_controller.view.elem
        elem[f"{elem_key}_MIN_LINE"].setText(
            meas_controller.value_to_str(value_min, unit)
        )
        elem[f"{elem_key}_MAX_LINE"].setText(
            meas_controller.value_to_str(value_max, unit)
        )
        elem[f"{elem_key}_POINTS_LINE"].setText(remove_zeros(points))

    @staticmethod
    def update_sa_elem(meas_controller: object, value: float, param: tuple) -> None:
        """Update the GUI elements related to the spectrum analyzer settings."""
        elem_key, unit = param
        if unit in meas_controller.units:
            dev = meas_controller.units[unit]
        meas_controller.view.elem[f"{elem_key}_LINE"].setText(remove_zeros(value / dev))

    @staticmethod
    def update_osc_elem(meas_controller: object, value: float, param: tuple) -> None:
        """Update the GUI elements related to the oscilloscope settings."""
        SettingsSignalHandler.update_sa_elem(meas_controller, value, param)

    @staticmethod
    def set_elements_unchanged(meas_controller: object) -> None:
        """
        Reset the style of the elements to their default state after submitting the input parameters.
        """
        elem = meas_controller.view.elem
        for element in elem.values():
            if isinstance(element, (QLineEdit, QCheckBox, QRadioButton)):
                element.setProperty("class", "")
                refresh_obj_view(element)
        meas_controller.unlock_start_btn()

    def update_max_det_level(meas_controller: object) -> None:
        """Update the maximum detector input level display based on current settings."""
        model = meas_controller.model
        elem = meas_controller.view.elem
        if model.is_s21_gen_det() and model.settings:
            max_level = round(model.calc_max_det_level(), 2)  # .:2f
            elem["MAX_DET_LEVEL_VALUE_LABEL"].setText(
                meas_controller.value_to_str(max_level, "dBm")
            )
