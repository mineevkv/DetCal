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
    sheet = dict()

    def __init__(self):
        super().__init__()
        self.init_main_window()
        self.init_sheets()
        self.add_fields()
        

    def init_main_window(self):
        self.init_fonts()
        self.setWindowTitle("Detectors calibration")
        self.setFixedSize(1280, 720)

        self._main_layout = QGridLayout()
        self.setLayout(self._main_layout)


    def init_sheets(self):
        self.sheet_param = {
            'left_width': 391,
            'right_width': 861,
        }
    
        self.meas = MeasurementSheet(self)
        self.ig = InfographicSheet(self)
        self.gen = GeneratorSheet(self)
        self.sa = SpectrumAnalyzerSheet(self)
        self.osc = OscilloscopeSheet(self)


    def add_fields(self):
        # Left fields
        self._main_layout.addWidget(self.gen.get_widget(), 0, 0)
        self._main_layout.addWidget(self.sa.get_widget(), 1, 0)
        self._main_layout.addWidget(self.osc.get_widget(), 2, 0)
        # Right fields
        self._main_layout.addWidget(self.meas.get_widget(), 0, 1, 2, 1)
        self.meas.get_widget().setFixedWidth(self.sheet_param['right_width'])
        self._main_layout.addWidget(self.ig.get_widget(), 2, 1)

    def init_fonts(self):
        default_font = 'Sergo UI'

        font_folder = "./GUI/Fonts/Roboto"
        if os.path.exists(font_folder):
            for file in os.listdir(font_folder):
                if file.endswith(".ttf"):
                    QFontDatabase.addApplicationFont(os.path.join(font_folder, file))
            
            font_id = QFontDatabase.addApplicationFont("./GUI/Fonts/Roboto/Roboto_SemiCondensed-Regular.ttf")

            # Check if font was loaded successfully
            if font_id != -1:
                font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
                # Use the font
                self.custom_font = QFont(font_family) 
                logger.debug(f"Successfully loaded font: {font_family}")
            else:
                logger.warning("Failed to load font")
                self.custom_font = QFont(default_font)
        else:
            logger.warning("Font folder not found")
            self.custom_font = QFont(default_font)
      
        # Apply font to the application
        QApplication.setFont(self.custom_font)

    def showEvent(self, event):
        """Override showEvent after window is shown"""
        super().showEvent(event)
        logger.debug(f"Main window '{self.windowTitle()}' is shown")

    def get_layout(self):
        return self._main_layout
    