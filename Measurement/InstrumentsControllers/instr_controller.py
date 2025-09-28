from PyQt6.QtCore import QObject, QTimer
from abc import ABC, abstractmethod
from Measurement.MeasurementModel.file_manager import FileManager

from Measurement.abstract_controller import Controller

from GUI.palette import *

from System.logger import get_logger
logger = get_logger(__name__)

class InstrumentController(Controller):
    def __init__(self, instr, instr_sheet):
        super().__init__()
        self.instr = instr
        self.view = instr_sheet
        
        self.connect_signals()
        self.set_connection_field()
        self.init_progress_timer()
        

        
    #Controller
    @abstractmethod
    def connect_signals(self):
        self.view.elem['BTN_IP'].clicked.connect(self.btn_connect_click)
        self.instr.state_changed.connect(self.signal_handler)
        self.instr.progress_changed.connect(self.progress)

    @abstractmethod
    def signal_handler(self, message):
        if 'IP' in message:
            self.view.elem['IP_CLICKLINE'].setText(message['IP'])
            self.set_connection_field()
        if 'MODEL' in message:
            self.view.elem['MODEL_LABEL'].setText(message['MODEL'])
        if 'TYPE' in message:
            self.view.box.setTitle(message['TYPE'])
        if 'THREAD' in message:
            self.instr.connect_thread = None

            
    def is_connect(self):
        if self.instr is not None and self.instr.is_initialized():
            return True
        else:
            return False

    def set_connection_field(self):
        label = self.view.elem['IP_STATUS_LABEL']
        line_edit = self.view.elem['IP_CLICKLINE']
        
        if self.is_connect():           
            label.setText("Connected")
            label.setStyleSheet(f"color: {GREEN}")
            line_edit.setEnabled(False)
        else:
            label.setStyleSheet(f"color: {RED}")
            label.setText("No connection")
            line_edit.setEnabled(True)

    def btn_connect_click(self):
        new_ip = self.view.elem['IP_CLICKLINE'].text()
        new_ip = new_ip.strip()

        if not self.is_valid_ip(new_ip):
            logger.warning(f"Invalid IP address: {new_ip}")
            return

        if self.is_connect():
            current_ip = self.instr.get_ip()
            if current_ip == new_ip:
                logger.info(f"Already connected to {new_ip}")
                return
                        
        if self.instr is not None:
            self.instr.set_ip(new_ip)
            self.instr.connect()
            self.timer.start(300)

    def init_progress_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.progress_update)
        self.timer.start(300)

    def progress(self,value):
        self.view.elem['PROGRESS'].setValue(value)
        if value == 100:
            self.timer.timeout.connect(self.progress_hide)

    def progress_update(self):
        value = self.view.elem['PROGRESS'].value()
        self.progress(value + 1)

    def progress_hide(self):
        self.timer.stop()
        self.progress(0)

    def is_valid_ip(self, ip):
        """
        Check if given IP address is valid
        """
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            if int(part) < 0 or int(part) > 255:
                return False
        return True

    def check_initialization(self):
        if self.instr.is_initialized():
            self.enable_control_elem()
        else:
            self.disable_control_elem()

    def enable_control_elem():
        pass

    def disable_control_elem():
        pass



    def disable_control_elem(self):
        for key in self.elem:
            self.elem[key].setEnabled(False)
 
    def enable_control_elem(self):
        for key in self.elem:
            self.elem[key].setEnabled(True)

    def btn_clicked(self,btn_name, btn_handler):
        self.view.elem[f'BTN_{btn_name}'].clicked.connect(btn_handler)

    def read_line(self, line_edit):
        return self.view.elem[f'{line_edit}_LINE'].text()
    
    
