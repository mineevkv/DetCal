from .instr_controller import InstrumentController
from Measurement.helper_functions import refresh_obj_view, btn_clicked_connect

from System.logger import get_logger

logger = get_logger(__name__)


class SAController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr, instr_sheet)
        self.instr.connect()

    def connect_signals(self):
        super().connect_signals()
        keys = (
            "CENTER_FREQ",
            "SPAN",
            "RBW",
            "VBW",
            "SINGLE",
        )

        for key in keys:
            btn_clicked_connect(
                self, key, getattr(self, f"btn_{key.lower()}_click", None)
            )

    def signal_handler(self, message):
        super().signal_handler(message)
        elem = self.view.elem
        if "CENTER_FREQ" in message:
            elem["CENTER_FREQ_LINE"].setText(
                self.value_to_str(message["CENTER_FREQ"], "MHz")
            )
        if "SPAN" in message:
            elem["SPAN_LINE"].setText(self.value_to_str(message["SPAN"], "MHz"))
        if "RBW" in message:
            elem["RBW_LINE"].setText(self.value_to_str(message["RBW"], "kHz"))
        if "VBW" in message:
            elem["VBW_LINE"].setText(self.value_to_str(message["VBW"], "kHz"))

        if "REFERENCE_LEVEL" in message:
            pass
        if "SWEEP_TIME" in message:
            pass
        if "SWEEP_POINTS" in message:
            pass
        if "TRACE_FORMAT" in message:
            pass
        if "SINGLE_SWEEP" in message:
            pass
        if "CONTINUOUS_SWEEP" in message:
            pass
        if "CONFIGURE" in message:
            pass

    def btn_center_freq_click(self):  # TODO: freq_line_edit_handler
        line_edit = self.view.elem["CENTER_FREQ_LINE"]
        try:
            freq = float(line_edit.text()) * 1e6
            if not 1e3 <= freq <= 6.5e9:
                raise ValueError("Center frequency must be between 1 kHz and 6.5 GHz")
            self.instr.set_center_freq(freq)
        except ValueError as e:
            logger.error(f"Error setting center frequency: {e}")
            freq = self.instr.get_center_freq()
            if freq is not None:
                line_edit.setText(str(freq / 1e6))

    def freq_line_edit_handler(self, line_edit, setter, getter, units="Hz"):
        multipliers = {"Hz": 1, "kHz": 1e3, "MHz": 1e6, "GHz": 1e9}
        multiplier = multipliers.get(units, 1)

        try:
            freq = float(line_edit.text()) * multiplier
            if not 1e3 <= freq <= 6.5e9:
                raise ValueError("Frequency must be between 1 kHz and 6.5 GHz")
            setter(freq)
        except ValueError as e:
            logger.error(f"Error setting frequency: {e}")
            freq = getter()
            if freq is not None:
                line_edit.setText(str(freq / multiplier))

    def btn_span_click(self):
        self.freq_line_edit_handler(
            self.view.elem["SPAN_LINE"], self.instr.set_span, self.instr.get_span, "MHz"
        )

    def btn_rbw_click(self):
        pass

    def btn_vbw_click(self):
        pass

    def btn_single_click(self):
        pass
