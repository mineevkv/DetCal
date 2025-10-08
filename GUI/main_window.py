import os
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication
from PyQt6.QtGui import QFont, QFontDatabase

from GUI.Sheets.meas_sheet import MeasurementSheet
from GUI.Sheets.infographic_sheet import InfographicSheet
from GUI.Sheets.gen_sheet import GeneratorSheet
from GUI.Sheets.sa_sheet import SpectrumAnalyzerSheet
from GUI.Sheets.osc_sheet import OscilloscopeSheet

from System.logger import get_logger

logger = get_logger(__name__)


class MainWindow(QWidget):
    """
    Main window class for the application.

    This class is used to create the main window of the application.
    It contains methods for initializing the main window, adding fields and
    initializing the sheets.

    """

    # Window constants
    WINDOW_WIDTH = 1280
    WINDOW_HEIGHT = 680
    LEFT_SHEET_WIDTH = 391
    RIGHT_SHEET_WIDTH = 861

    # Font constants
    DEFAULT_FONT = "Segoe UI"
    FONT_FOLDER = "./GUI/Fonts/Roboto"
    PRIMARY_FONT_FILE = "Roboto_SemiCondensed-Regular.ttf"

    def __init__(self) -> None:
        super().__init__()
        self.init_main_window()
        self.init_sheets()
        self.add_fields()

    def init_main_window(self) -> None:
        """Initialize the main window."""
        self.init_fonts()
        self.setWindowTitle("Detectors calibration")
        self.setFixedSize(self.WINDOW_WIDTH, self.WINDOW_HEIGHT)

        self._main_layout = QGridLayout()
        self.setLayout(self._main_layout)

    def init_sheets(self) -> None:
        """Initialize the sheets."""
        self.meas = MeasurementSheet(self)
        self.ig = InfographicSheet(self)
        self.gen = GeneratorSheet(self)
        self.sa = SpectrumAnalyzerSheet(self)
        self.osc = OscilloscopeSheet(self)

    def add_fields(self) -> None:
        """Add working fields to the main layout."""
        # Left fields
        self._main_layout.addWidget(self.gen.get_widget(), 0, 0)
        self._main_layout.addWidget(self.sa.get_widget(), 1, 0)
        self._main_layout.addWidget(self.osc.get_widget(), 2, 0)
        # Right fields
        self._main_layout.addWidget(self.meas.get_widget(), 0, 1, 2, 1)
        self._main_layout.addWidget(self.ig.get_widget(), 2, 1)
        # Right fields dimensions
        self.meas.get_widget().setFixedWidth(self.RIGHT_SHEET_WIDTH)

    def init_fonts(self) -> None:
        """Initialize the main fonts."""
        if os.path.exists(self.FONT_FOLDER):
            for file in os.listdir(self.FONT_FOLDER):
                if file.endswith(".ttf"):
                    QFontDatabase.addApplicationFont(
                        os.path.join(self.FONT_FOLDER, file)
                    )

            # Load the font
            font_id = QFontDatabase.addApplicationFont(
                os.path.join(self.FONT_FOLDER, self.PRIMARY_FONT_FILE)
            )

            # Check if font was loaded successfully
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                # Use the font
                self.custom_font = QFont(font_family)
                logger.debug(f"Successfully loaded font: {font_family}")
            else:
                logger.warning("Failed to load font")
                self.custom_font = QFont(self.DEFAULT_FONT)
        else:
            logger.warning("Font folder not found")
            self.custom_font = QFont(self.DEFAULT_FONT)

        # Apply font to the application
        QApplication.setFont(self.custom_font)

    def showEvent(self, event: object) -> None:
        """Override showEvent after window is shown"""
        super().showEvent(event)
        logger.debug(f"Main window '{self.windowTitle()}' is shown")

    def get_layout(self) -> QGridLayout:
        """Get the main layout."""
        return self._main_layout
