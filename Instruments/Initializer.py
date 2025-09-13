
from PyQt6.QtCore import QThread, pyqtSignal
from queue import Queue
import threading
import json

from Instruments.rsa5065n import *
from Instruments.dsg830 import *
from Instruments.mdo34 import *


from System.logger import get_logger
logger = get_logger(__name__)

class InstrumentInitializer(QThread):
    """Thread for instrument initialization"""

    progress = pyqtSignal(str)
    finished = pyqtSignal(object)  # emits (error)
    instr_list = pyqtSignal(object, object, object, object)  # emits (gen, sa, osc, error)
    

    def __init__(self):
        super().__init__()
        self.offline_debug =  False # Set to True to simulate offline mode

        self.load_instr_ip_settings()

    def load_instr_ip_settings(self):
        ip_settings = self.load_instr_ip_from_file('Settings/instr_ip.json')
        for key, value in ip_settings.items():
            setattr(self, key, value)

    @staticmethod
    def load_instr_ip_from_file(filename):
        try:
            with open(filename, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load instrument IPs from {filename}: {e}")
            return {}

    def run(self):
        if self.offline_debug:
            self.progress.emit("Skipping instrument initialization")
            self.finished.emit('Offline debug mode')
            self.instr_list.emit(None, None, None, None)
            return
        
        try:
            # Initialize DSG
            self.progress.emit(f"Initializing Signal Generator at {self.ip_DSG830}")
            dsg_queue = Queue()
            dsg_thread = threading.Thread(
                target=self.init_instrument,
                args=(DSG830, self.ip_DSG830, self.visa_string_usb_DSG830, dsg_queue),
                name="DSG_Initialization"
            )
            dsg_thread.start()

            # Initialize RSA
            self.progress.emit(f"Initializing Spectrum Analyzer at {self.ip_RSA5065N}")
            rsa_queue = Queue()
            rsa_thread = threading.Thread(
                target=self.init_instrument,
                args=(RSA5065N, self.ip_RSA5065N, self.visa_string_usb_RSA5065N , rsa_queue),
                name="RSA_Initialization"
            )
            rsa_thread.start()
                  
            # Initialize MDO 

            self.progress.emit(f"Initializing Oscilloscope at {self.ip_MDO34}")
            mdo_queue = Queue()
            mdo_thread = threading.Thread(
                target=self.init_instrument,
                args=(MDO34, self.ip_MDO34, self.visa_string_usb_MDO34, mdo_queue),
                name="OSC_Initialization"
            )
            mdo_thread.start()
            
            rsa_thread.join()
            sa = rsa_queue.get()
            if isinstance(sa, Exception):
                raise sa
            
            dsg_thread.join()
            gen = dsg_queue.get()
            if isinstance(gen, Exception):
                raise gen
            
            mdo_thread.join()
            osc = mdo_queue.get()
            if isinstance(osc, Exception):
                raise osc

            self.progress.emit("Instruments initializing finished")
            self.finished.emit(None)
            self.instr_list.emit(gen, sa, osc, None)

            
            
        except Exception as e:
            self.progress.emit(f"Initialization failed: {str(e)}")
            self.instr_list.emit(None, None, None, e)
            self.finished.emit(e)

    def init_instrument(self, instrument_class, ip, visa_usb, q):
        try:
            result = instrument_class(ip, visa_usb)
            q.put(result)
        except Exception as e:
            q.put(e)