
from PyQt6.QtWidgets import QGroupBox, QPushButton, QGridLayout

from .abstract_sheet import Sheet
from GUI.palette import *

from System.logger import get_logger

logger = get_logger(__name__)


class InstrumentSheet(Sheet):
    """
    Class for instrument sheet in the main window.

    This class is used to create the instrument sheet in the main window.
    It contains the instrument type, IP address, and animated progress bar.
    """

    def __init__(self, main_layout: QGridLayout) -> None:
        super().__init__(main_layout)
        self.ip = "NoIP"

        self.add_instrument_sheet()
        self.add_ip_field()
        self.add_animated_progress_bar()

    def add_instrument_sheet(self) -> None:
        """
        Add the instrument type sheet to the main layout.

        """

        self.box = QGroupBox("Instrument type")

        self.add_label("MODEL", 16, self.zero_row, "Model", 100).setStyleSheet(
            f"color: {YELLOW}; font-weight: bold"
        )

    def add_ip_field(self) -> None:
        """
        Add the IP address field and connect button to the main layout.

        """

        self.ip_row = 2
        key = "IP"
        self.add_label(key, self.zero_col, self.ip_row, "IP:", 50)
        self.add_clickable_line_edit(key, 3, self.ip_row, f"{self.ip}", 93)
        self.add_btn(key, 13, self.ip_row, "Connect")
        self.add_label(f"{key}_STATUS", 20, self.ip_row, "", 100)

        self.ip_keys = (
            f"{key}_LABEL",
            f"{key}_CLICKLINE",
            f"BTN_{key}",
            f"{key}_STATUS_LABEL",
        )

    def add_animated_progress_bar(self) -> None:
        """Add the animated progress bar to the main layout."""
        bar = self.add_progress_bar(
            "PROGRESS",
            self.zero_col,
            self.zero_row + 1,
            391 - 2 * self.margin_left,
            self.elem_height,
        )
        self.shift_position(bar, shift_x=0, shift_y=-3)
        bar.setProperty("class", "instr_progress_bar")
        bar.setRange(0, 100)

    def add_control_elem(
        self,
        key: str,
        col: int,
        row: int,
        text: str,
        value: str,
        label_width: int = 85,
        line_width: int = 63,
        btn_width: int = 60,
    ) -> None:
        """Add a control element consisting of a label, line edit, and button."""
        col_label = col
        self.add_label(key, col_label, row, text, label_width)

        col_line = col + label_width // 10 + 1
        self.add_line_edit(key, col_line, row, value, line_width)

        col_btn = col_line + line_width // 10 + 1
        self.add_btn(key, col_btn, row, "Set", btn_width)

    def add_big_btn(
        self, key: str, col: int, row: int, text: str, width: int = 60
    ) -> QPushButton:
        """Add a "big" button to the sheet."""
        btn = self.add_btn(key, col, row, text, width)
        btn.setFixedHeight(45)
        return btn
