from abc import ABC
from PyQt6.QtWidgets import (
    QWidget,
    QPushButton,
    QCheckBox,
    QProgressBar,
    QRadioButton,
    QLabel,
    QLineEdit,
    QGroupBox,
)

from PyQt6 import QtCore

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger

logger = get_logger(__name__)


class Sheet(ABC):
    """
    Abstract base class for all sheets.

    Provides common functionality for all sheets.

    Attributes:
        layout (QLayout): The layout of the main window.
        _margin_top (int): The top margin of the sheet.
        _margin_left (int): The left margin of the sheet.
        _zero_col (int): The column where the sheet starts.
        _zero_row (int): The row where the sheet starts.
        _row_hight (int): The height of a row in the sheet.
        _col_width (int): The width of a column in the sheet.
        elem (dict): A dictionary of elements in the sheet.
        _elem_hight (int): The height of an element in the sheet.
        box (QGroupBox): The group box of the sheet.
        x_col (list): A list of x coordinates of the columns in the sheet.
        y_row (list): A list of y coordinates of the rows in the sheet.

    """

    def __init__(self, main_window: object) -> None:
        self.layout = main_window.get_layout()
        self._margin_top = 10
        self._margin_left = 11

        self._zero_col = 0
        self._zero_row = 0

        self._row_height = 25
        self._col_width = 10

        self.elem = getattr(self, "elem", {})  # existing condition
        self._elem_height = 20

        self.box = QGroupBox("Empty sheet")  # existing condition

        # Default grid for placing elements
        right_end = main_window.width() - self.margin_left
        bottom_end = main_window.height() - self.margin_top
        self.x_col = [x for x in range(self.margin_left, right_end, self.col_width)]
        self.y_row = [y for y in range(self.margin_top, bottom_end, self.row_height)]

    @property
    def col_width(self) -> int:
        """Return the width of a column in the sheet"""
        return self._col_width

    @property
    def row_height(self) -> int:
        """Return the height of a row in the sheet"""
        return self._row_height

    @property
    def margin_top(self) -> int:
        """Return the top margin of the sheet"""
        return self._margin_top

    @property
    def margin_left(self) -> int:
        """Return the left margin of the sheet"""
        return self._margin_left

    @property
    def zero_col(self) -> int:
        """Return the index of the first column in the sheet"""
        return self._zero_col

    @property
    def zero_row(self) -> int:
        """Return the index of the first row in the sheet"""
        return self._zero_row

    @property
    def elem_height(self) -> int:
        """Return the height of an element in the sheet"""
        return self._elem_height

    def get_widget(self) -> QWidget:
        """Return the main widget of the sheet"""
        return self.box

    def hide(self) -> None:
        """Hide the sheet"""
        self.box.hide()

    def add_label(
        self, key: str, col: int, row: int, text: str, width: int = 85
    ) -> QLabel:
        """Add a QLabel to the sheet"""
        label = self.elem[f"{key}_LABEL"] = QLabel(f"{text}", parent=self.box)
        label.setGeometry(
            QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_height)
        )
        return label

    def add_line_edit(
        self, key: str, col: int, row: int, value: float, width: int = 63
    ) -> QLineEdit:
        """Add a QLineEdit to the sheet"""
        line_edit = self.elem[f"{key}_LINE"] = QLineEdit(f"{value}", parent=self.box)
        line_edit.setGeometry(
            QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_height)
        )
        line_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        return line_edit

    def add_clickable_line_edit(
        self, key: str, col: int, row: int, value: float, width: int = 63
    ) -> ClickableLineEdit:
        """Add a ClickableLineEdit (QLineEdit with a click event)  to the sheet"""
        line_edit = self.elem[f"{key}_CLICKLINE"] = ClickableLineEdit(
            f"{value}", parent=self.box
        )
        line_edit.setGeometry(
            QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_height)
        )
        line_edit.setProperty("class", "ip_line")
        line_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        return line_edit

    def add_btn(
        self, key: str, col: int, row: int, text: str, width: int = 60
    ) -> QPushButton:
        """Add a QPushButton to the sheet"""
        btn = self.elem[f"BTN_{key}"] = QPushButton(f"{text}", parent=self.box)
        btn.setGeometry(
            QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_height)
        )
        freeze_label = self.elem[f"FREEZEBTN_{key}"] = QLabel(f"", parent=self.box)
        freeze_label.setGeometry(
            QtCore.QRect(self.x_col[col], self.y_row[row], width, self.elem_height)
        )
        freeze_label.setProperty("class", "freeze_btn")
        freeze_label.hide()

        return btn

    def add_custom_btn(
        self,
        key: str,
        col: int,
        row: int,
        text: str,
        width: int,
        height: int,
        elem_class: str = None,
    ) -> QPushButton:
        """Add a custom QPushButton with a specific class to the sheet"""
        btn = self.add_btn(key, col, row, text, width)
        btn.setFixedHeight(height)
        self.elem[f"FREEZEBTN_{key}"].setFixedHeight(height)
        if elem_class is not None:
            btn.setProperty("class", elem_class)
        return btn

    def add_check_box(self, key: str, col: int, row: int, text: str) -> QCheckBox:
        """Add a QCheckBox to the sheet"""
        check_box = self.elem[key] = QCheckBox(parent=self.box, text=text)
        check_box.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], 200, 20))
        return check_box

    def add_radio_btn(
        self, key: str, col: int, row: int, text: str, width: int = 90
    ) -> QRadioButton:
        """Add a QRadioButton to the sheet"""
        radio_btn = self.elem[key] = QRadioButton(parent=self.box, text=text)
        radio_btn.setGeometry(QtCore.QRect(self.x_col[col], self.y_row[row], width, 20))
        radio_btn.setChecked(False)
        return radio_btn

    def add_progress_bar(
        self, key: str, col: int, row: int, width: int, height: int
    ) -> QProgressBar:
        """Add a QProgressBar to the sheet"""
        progress_bar = self.elem[key] = QProgressBar(parent=self.box)
        progress_bar.setGeometry(
            QtCore.QRect(self.x_col[col], self.y_row[row], width, height)
        )
        progress_bar.setRange(0, 100)
        return progress_bar

    def shift_position(self, elem: object, shift_x: int = 0, shift_y: int = 0) -> None:
        """Shift the (dx, dy)position of an element"""
        elem.move(elem.x() + shift_x, elem.y() + shift_y)

    def add_frame(
        self,
        key: str,
        col: int,
        row: int,
        dx: int,
        dy: int,
        width: int,
        height: int,
        class_name: str,
    ) -> None:
        """Add a frame to the sheet"""
        frame = self.elem[f"{key}_FRAME"] = self.frame_ch = QWidget(self.box)
        frame.setProperty("class", f"{class_name}")
        frame.setGeometry(self.x_col[col] - dx, self.y_row[row] - dy, width, height)
        frame.setAutoFillBackground(True)

    def cleanup(self) -> None:
        """Safe cleanup method to be called explicitly"""
        if hasattr(self, "box") and self.box:
            self.box.deleteLater()
            self.box = None
