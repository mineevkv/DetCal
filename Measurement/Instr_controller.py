from PyQt6.QtCore import QObject, QTimer


from GUI.palette import *

from System.logger import get_logger
logger = get_logger(__name__)

class InstrumentController(QObject):
    def __init__(self):
        super().__init__()
        pass

        # self.ip_btn_connect.clicked.connect(self.ip_btn_connect_click)

        # self.check_connection()

            #Controller


    def check_connection(self):
        if self.instr.is_initialized():
            self.ip_status_label.setText("Connected")
            self.ip_status_label.setStyleSheet(f"color: {GREEN}")
            self.ip_line.setEnabled(False)
            return True
        else:
            self.ip_status_label.setText("No connection")
            self.ip_status_label.setStyleSheet(f"color: {RED}")
            self.ip_line.setEnabled(True)
            return False
        

    def update_ip(self):
           pass
        #    self.ip = self.instr.ip

    def ip_btn_connect_click(self):
        if not self.check_connection():
            self.ip = self.ip_line.text()
            self.instr.set_ip(self.ip)
            self.instr.connect()
        if not self.check_connection():
            self.ip_status_label.setText("Connection error")

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