from .keys import Keys

from System.logger import get_logger

logger = get_logger(__name__)


class WriteSettings:
    """Class to write settings from the view to the model."""

    def __init__(self) -> None:
        pass

    @staticmethod
    def view_to_model(meas_controller: object) -> None:
        """Write settings from the view to the model."""
        settings = WriteSettings.view_to_dict(meas_controller)
        for key, value in settings.items():
            meas_controller.model.settings[key] = value

    def view_to_dict(meas_controller: object) -> dict:
        """Write settings from the view to a dictionary."""
        settings = {}
        elem = meas_controller.view.elem

        for key, param in Keys.gen.items():
            settings[key] = WriteSettings.get_gen_settings(meas_controller, param)

        for key, param in Keys.sa.items():
            if key == "REF_LEVEL" and not elem["REF_LEVEL_ENABLED"].isChecked():
                param = ("LEVEL_MAX", "dBm")
            settings[key] = WriteSettings.get_sa_settings(meas_controller, param)

        settings["PRECISE"] = elem["PRECISE_ENABLED"].isChecked()
        settings["RECALC_ATTEN"] = elem["RECALC_ATT"].isChecked()
        settings["REF_MANUAL"] = elem["REF_LEVEL_ENABLED"].isChecked()

        for key, param in Keys.osc.items():
            settings[key] = WriteSettings.get_osc_settings(meas_controller, param)

        settings["HIGH_RES"] = elem["HIGHT_RES_BOX"].isChecked()
        settings["IMPEDANCE_50OHM"] = elem["RB_50OHM"].isChecked()
        settings["COUPLING_DC"] = elem["RB_DC"].isChecked()
        settings["CHANNEL"] = next(
            (i for i in [1, 2, 3, 4] if elem[f"RB_CH{i}"].isChecked()), None
        )

        settings["FILENAME"] = WriteSettings.get_det_name(meas_controller)

        return settings

    @staticmethod
    def get_gen_settings(meas_controller: object, param: tuple) -> tuple:
        """Get generator settings from the view."""
        elem_key, unit = param
        if unit in meas_controller.units:
            multiplier = meas_controller.units[unit]

        elem = meas_controller.view.elem
        value_min = float(elem[f"{elem_key}_MIN_LINE"].text()) * multiplier
        value_max = float(elem[f"{elem_key}_MAX_LINE"].text()) * multiplier
        points = int(elem[f"{elem_key}_POINTS_LINE"].text())

        return value_min, value_max, points

    @staticmethod
    def get_sa_settings(meas_controller: object, param: tuple) -> tuple:
        """Get spectrum analyzer settings from the view."""
        elem_key, unit = param
        if unit in meas_controller.units:
            multiplier = meas_controller.units[unit]
            try:
                return (
                    float(meas_controller.view.elem[f"{elem_key}_LINE"].text())
                    * multiplier
                )
            except ValueError:
                logger.warning(f"Invalid value for {elem_key}_LINE")
                raise

    @staticmethod
    def get_osc_settings(meas_controller: object, param: tuple) -> tuple:
        """Get oscilloscope settings from the view."""
        return WriteSettings.get_sa_settings(meas_controller, param)

    @staticmethod
    def get_det_name(meas_controller: object) -> str:
        """Get detector name from the view."""
        elem = meas_controller.general_view.ig.elem
        det_name = elem["DET_NAME_LINE"].text()
        det_name = det_name.rstrip()
        det_name = det_name.replace(" ", "_")
        return det_name

    @staticmethod
    def write_det_name_to_model(meas_controller: object) -> None:
        """Write detector name to the model."""
        det_name = WriteSettings.get_det_name(meas_controller)
        meas_controller.model.settings["FILENAME"] = det_name
