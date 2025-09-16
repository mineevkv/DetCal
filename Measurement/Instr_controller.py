from PyQt6.QtCore import QObject, QTimer
from abc import ABC, abstractmethod

from GUI.palette import *

from System.logger import get_logger
logger = get_logger(__name__)

class InstrumentController(QObject):
    def __init__(self, instr, instr_sheet):
        super().__init__()
        self.instr = instr
        self.view = instr_sheet
        
        self.connect_signals()
        self.set_connection_field()
        
        # self.ip_btn_connect.clicked.connect(self.ip_btn_connect_click)

        
    #Controller
    @abstractmethod
    def connect_signals(self):
        self.view.elem['btn_ip'].clicked.connect(self.btn_connect_click)
        self.instr.state_changed.connect(self.signal_handler)

    @abstractmethod
    def signal_handler(self, message):
        if 'ip' in message:
            self.view.elem['ip_clickline'].setText(message['ip'])
            self.set_connection_field()
        if 'model' in message:
            self.view.elem['model_label'].setText(message['model'])
        if 'type' in message:
            self.view.box.setTitle(message['type'])
        if 'thread' in message:
            self.instr.connect_thread = None
            


    def is_connect(self):
        if self.instr is not None and self.instr.is_initialized():
            return True
        else:
            return False

    def set_connection_field(self):
        label = self.view.elem['ip_status_label']
        line_edit = self.view.elem['ip_clickline']
        
        if self.is_connect():           
            label.setText("Connected")
            label.setStyleSheet(f"color: {GREEN}")
            line_edit.setEnabled(False)
        else:
            label.setStyleSheet(f"color: {RED}")
            label.setText("No connection")
            line_edit.setEnabled(True)

    def btn_connect_click(self):
        new_ip = self.view.elem['ip_clickline'].text()
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
            


        # if not self.is_connect():
        #     label = self.view.elem['ip_status_label']
        #     label.setText("Connection error")

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
        self.view.elem[f'btn_{btn_name}'].clicked.connect(btn_handler)