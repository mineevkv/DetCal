from .instr_controller import InstrumentController
from Measurement.helper_functions import refresh_obj_view, btn_clicked_connect
from Measurement.MeasurementController.values_validator import ValuesValidator as Val

from System.logger import get_logger

logger = get_logger(__name__)


class SAController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr, instr_sheet)

    def init_signals(self): 
        super().init_signals()
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
        tolerance = 3
        if "CENTER_FREQ" in message:
            elem["CENTER_FREQ_LINE"].setText(self.value_to_str(message['CENTER_FREQ'], "MHz", tolerance))
        if "SPAN" in message:
            elem["SPAN_LINE"].setText(self.value_to_str(message["SPAN"], "MHz", tolerance))
        if "RBW" in message:
            elem["RBW_LINE"].setText(self.value_to_str(message["RBW"], "kHz", tolerance))
        if "VBW" in message:
            elem["VBW_LINE"].setText(self.value_to_str(message["VBW"], "kHz", tolerance))

    def btn_center_freq_click(self):  # TODO: freq_line_edit_handler
        line_edit = self.view.elem["CENTER_FREQ_LINE"]
        setter = self.instr.set_center_freq
        getter = self.instr.get_center_freq
        unit = "MHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)

    def btn_span_click(self):
        line_edit = self.view.elem["SPAN_LINE"]
        setter = self.instr.set_span
        getter = self.instr.get_span
        unit = "MHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)
        

    def btn_rbw_click(self):
        line_edit = self.view.elem["RBW_LINE"]
        setter = self.instr.set_rbw
        getter = self.instr.get_rbw
        unit = "kHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)
        

    def btn_vbw_click(self):
        line_edit = self.view.elem["VBW_LINE"]
        setter = self.instr.set_vbw
        getter = self.instr.get_vbw
        unit = "kHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)

    def btn_single_click(self):
        self.instr.start_single_measurement()


    def freq_line_edit_handler(self, line_edit, setter, getter, unit):
        if Val.is_float(line_edit.text()):
            freq = float(line_edit.text()) * self.units[unit]
            if not 0 < freq <= 6.5e9:
                logger.warning(f"Value {line_edit.text()} is out of range")
                return
            setter(freq)
            value = getter()
            line_edit.setText(self.value_to_str(value, unit, 3))
        else:
            logger.error(f"Error value: {line_edit.text()}")
            return
