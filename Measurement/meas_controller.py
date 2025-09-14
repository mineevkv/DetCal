from PyQt6.QtCore import QObject, QTimer
from .meas_model import MeasurementModel
from GUI.main_window import MainWindow

from GUI.palette import *

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementController(QObject):
    def __init__(self):
        super().__init__()

        self.model = MeasurementModel()
        self.view = MainWindow()

        self.connect_signals() # Must be before initialization
        self.model.offline_mode(True) # Set to True for offline testing without instruments
        self.model.start_initialization()



        # self.connect_signals()
        # self.update_view()


    def connect_signals(self):
        self.initializer_signals()
        self.init_timer_signals()

    def initializer_signals(self):
        self.model.initializer.progress.connect(self.update_init_progress)
        self.model.initializer.finished.connect(self.initialization_complete)

    def init_timer_signals(self):
        self.init_timer = QTimer()
        self.init_timer.timeout.connect(self.close_init_window)

    def update_init_progress(self, message):
        """Update progress message"""
        self.append_init_text(f"progress: {message}")
        logger.info(message)

    def initialization_complete(self, error):
        """Handle completion of instrument initialization"""

        if error:
            message = f"Instrument initialization failed: {str(error)}"
            logger.error(message)
            self.append_init_text(message, status="ERROR")
            self.view.init.status_label.setText("No instruments")
            self.view.init.progress_bar.setRange(0, 100)
            self.view.init.progress_bar.setValue(100)            
            self.init_timer.setInterval(100) # 0.1 seconds
            self.init_timer.start()
            return
        
        message = 'Initialization complete'
        self.append_init_text(message)
        logger.info(message)
        self.init_timer.setInterval(500) # 0.5 second
        self.init_timer.start()

    def close_init_window(self):
        self.init_timer.stop()
        self.view.instr_sheet_show()
        self.view.init.cleanup()

        self.set_instrum_sheets_controllers()
    
    def set_instrum_sheets_controllers(self):
        pass


    def append_init_text(self, text, status="INFO"):

        if status == "INFO":
            color = SURFGREEN
        elif status == "ERROR":
            color = RED
        elif status == "WARNING":
            color = YELLOW
        else:
            color = VIOLET

        self.view.init.text_browser.append(f"<span style='color: {color}'>{text}</span>")

    def run(self):
        logger.debug('GUI running')
        self.view.show()