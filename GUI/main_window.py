import os
from PyQt6.QtWidgets import QWidget, QGridLayout, QApplication
from PyQt6.QtGui import QFont, QFontDatabase

from GUI.Sheets.meas_sheet import MeasurementSheet
from GUI.Sheets.plot_sheet import PlotSheet
from GUI.Sheets.init_sheet import InitializationSheet
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
        self.create_fields()

    def init_main_window(self):
        self.init_fonts()
        self.setWindowTitle("Detectors calibration")
        self.setFixedSize(1280, 720)

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)


    def init_sheets(self):
        self.sheet_param = {
            'left_width': 391,
            'right_width': 861,
        }
    
        self.meas = MeasurementSheet(self)
        self.plot = PlotSheet(self)
        self.init = InitializationSheet(self)
        self.gen = GeneratorSheet(self)
        self.sa = SpectrumAnalyzerSheet(self)
        self.osc = OscilloscopeSheet(self)


    def create_fields(self):
        # Left fields
        self.main_layout.addWidget(self.init.get_widget(), 0, 0, 3, 1)
        # Right fields
        self.main_layout.addWidget(self.meas.get_widget(), 0, 1, 2, 1)
        self.meas.get_widget().setFixedWidth(self.sheet_param['right_width'])
        self.main_layout.addWidget(self.plot.get_widget(), 2, 1)

    def instr_sheet_hide(self):
        sheets = ['gen', 'sa', 'osc']
        for sh in sheets:
            getattr(self, sh).hide()

    def instr_sheet_show(self):
        # Left fields
        self.main_layout.addWidget(self.gen.get_widget(), 0, 0)
        self.main_layout.addWidget(self.sa.get_widget(), 1, 0)
        self.main_layout.addWidget(self.osc.get_widget(), 2, 0)

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
                logger.info(f"Successfully loaded font: {font_family}")
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
        return self.main_layout


    # def apply_font_to_widgets(self, widget=None):
    #     """Recursively apply custom font to all widgets"""
    #     if widget is None:
    #         widget = self
        
    #     # Apply font to the current widget
    #     if hasattr(widget, 'setFont'):
    #         widget.setFont(self.custom_font)
        
    #     # Apply to all child widgets
    #     for child in widget.findChildren(QWidget):
    #         self.apply_font_to_widgets(child)
    #         print(f"Applied font to {child.__class__.__name__}")