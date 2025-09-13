from PyQt6.QtWidgets import (
    QWidget, QPushButton, QApplication,
    QGridLayout, QLabel, QLineEdit, QGroupBox, QProgressBar, QTextBrowser
)

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt


from .abstract_sheet import Sheet
from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class InitializationSheet(Sheet):
    box_width = 391
    def __init__(self, main_window):
        super().__init__(main_window)

        self.box = QGroupBox("")
        # self.box.setFixedWidth(self.box_width)
        self.layout.addWidget(self.box)

        margin = 20
        size = self.box_width - 2*margin
        self.status_label = QLabel("Initializing instruments...", parent=self.box)
        self.status_label.setGeometry(QtCore.QRect(margin, 50, size, 30))
        self.status_label.setStyleSheet(f"font-size: 16pt; color: {YELLOW}")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar(parent=self.box)
        self.progress_bar.setGeometry(QtCore.QRect(margin, 100, size, 20))
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFixedWidth(size)

        self.text_browser = QTextBrowser(parent=self.box)
        self.text_browser.setGeometry(QtCore.QRect(margin, 140, size, 540))

    def __del__(self):
        self.box.deleteLater()
        logger.debug("Initialization complete, init_sheet was deleted")


