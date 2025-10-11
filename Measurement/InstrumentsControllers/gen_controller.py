from .instr_controller import InstrumentController
from PyQt6.QtCore import QObject
from Instruments.scpi_instr import Instrument

from System.logger import get_logger

logger = get_logger(__name__)


class GenController(InstrumentController):
    """Controller for Microwave Generator."""

    def __init__(self, instr: Instrument, instr_sheet: QObject) -> None:
        super().__init__(instr, instr_sheet)

    def init_signals(self) -> None:
        """Initialize signals for instrument controller."""
        super().init_signals()
        elem = self.view.elem

        elem["BTN_RF_ON"].clicked.connect(self.btn_rf_on_click)
        elem["BTN_FREQ"].clicked.connect(self.btn_freq_set_click)
        elem["BTN_LEVEL"].clicked.connect(self.btn_level_set_click)
        elem["BTN_MOD_ON"].clicked.connect(self.btn_mod_on_click)

    def btn_freq_set_click(self) -> None:
        """Button frequency set click handler."""
        freq = float(self.view.elem["FREQ_LINE"].text()) * 1e6
        self.instr.set_frequency(freq)

    def btn_level_set_click(self) -> None:
        """Button level set click handler."""
        level = float(self.view.elem["LEVEL_LINE"].text())
        self.instr.set_level(level)

    def btn_rf_on_click(self) -> None:
        """Button RF ON click handler."""
        btn = self.view.elem["BTN_RF_ON"]
        state = self.instr.get_output_state()
        if state == True:
            self.instr.rf_off()
            btn.setChecked(False)
        else:
            self.instr.rf_on()
            btn.setChecked(True)

    def btn_mod_on_click(self) -> None:
        """Button Modulation ON click handler."""
        btn = self.view.elem["BTN_MOD_ON"]
        state = self.instr.get_modulation_state()
        if state == True:
            self.instr.modulation_off()
            btn.setChecked(False)
        else:
            self.instr.modulation_on()
            btn.setChecked(True)

    def signal_handler(self, message: dict) -> None:
        """Handle signals from the instrument and update the GUI accordingly."""
        super().signal_handler(message)
        elem = self.view.elem
        if "LEVEL" in message:
            elem["LEVEL_LINE"].setText(self.value_to_str(message["LEVEL"], "dBm", 2))
        if "FREQUENCY" in message:
            elem["FREQ_LINE"].setText(self.value_to_str(message["FREQUENCY"], "MHz", 2))
        if "RF_STATE" in message:
            elem["BTN_RF_ON"].setChecked(message["RF_STATE"])
        if "MOD_STATE" in message:
            elem["BTN_MOD_ON"].setChecked(message["MOD_STATE"])
