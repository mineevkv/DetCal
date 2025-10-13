from .instr_controller import InstrumentController
from PyQt6.QtCore import QObject
from PyQt6.QtWidgets import QLineEdit
from Instruments.scpi_instr import Instrument
from Measurement.MeasurementController.values_validator import ValuesValidator as Val

from System.logger import get_logger

logger = get_logger(__name__)


class SAController(InstrumentController):
    """Controller for Spectrum Analyzer."""

    def __init__(self, instr: Instrument, instr_sheet: QObject) -> None:
        super().__init__(instr, instr_sheet)

    def init_signals(self) -> None:
        """Initialize signals for instrument controller."""
        super().init_signals()
        keys = (
            "CENTER_FREQ",
            "SPAN",
            "RBW",
            "VBW",
            "SINGLE",
        )

        for key in keys:
            self.btn_clicked(key, getattr(self, f"btn_{key.lower()}_click"))

    def signal_handler(self, message: dict) -> None:
        """Handle signals from the instrument and update the GUI accordingly."""
        super().signal_handler(message)
        elem = self.view.elem
        tolerance = 3

        message_handlers = {
            "CENTER_FREQ": ("CENTER_FREQ_LINE", "MHz"),
            "SPAN": ("SPAN_LINE", "MHz"),
            "RBW": ("RBW_LINE", "kHz"),
            "VBW": ("VBW_LINE", "kHz"),
        }

        for key, (line_element, unit) in message_handlers.items():
            if key in message:
                elem[line_element].setText(
                    self.value_to_str(message[key], unit, tolerance)
                )

    def btn_center_freq_click(self) -> None:
        """Button center frequency set click handler."""
        line_edit = self.view.elem["CENTER_FREQ_LINE"]
        setter = self.instr.set_center_freq
        getter = self.instr.get_center_freq
        unit = "MHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)

    def btn_span_click(self) -> None:
        """Button span set click handler."""
        line_edit = self.view.elem["SPAN_LINE"]
        setter = self.instr.set_span
        getter = self.instr.get_span
        unit = "MHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)

    def btn_rbw_click(self) -> None:
        """Button RBW set click handler."""
        line_edit = self.view.elem["RBW_LINE"]
        setter = self.instr.set_rbw
        getter = self.instr.get_rbw
        unit = "kHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)

    def btn_vbw_click(self) -> None:
        """Button VBW set click handler."""
        line_edit = self.view.elem["VBW_LINE"]
        setter = self.instr.set_vbw
        getter = self.instr.get_vbw
        unit = "kHz"
        self.freq_line_edit_handler(line_edit, setter, getter, unit)

    def btn_single_click(self) -> None:
        """Button Single click handler."""
        self.instr.start_single_measurement()

    def freq_line_edit_handler(
        self, line_edit: QLineEdit, setter: callable, getter: callable, unit: str
    ) -> None:
        """Handler for frequency line edit input: set and update the value."""
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
