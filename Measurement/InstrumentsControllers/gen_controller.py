from .instr_controller import InstrumentController

from System.logger import get_logger
logger = get_logger(__name__)

class GenController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr, instr_sheet)

        self.instr.connect() # TODO move to parent class
        
    def connect_signals(self): 
        super().connect_signals()
        self.view.elem['BTN_RF_ON'].clicked.connect(self.btn_rf_on_click)
        self.view.elem['BTN_FREQ'].clicked.connect(self.btn_freq_set_click)
        self.view.elem['BTN_LEVEL'].clicked.connect(self.btn_level_set_click)

    def btn_freq_set_click(self):
        freq = float(self.view.elem['FREQ_LINE'].text())*1e6
        self.instr.set_frequency(freq)

    def btn_level_set_click(self):
        level = float(self.view.elem['LEVEL_LINE'].text())
        self.instr.set_level(level)

    def btn_rf_on_click(self):
        btn = self.view.elem['BTN_RF_ON']
        state = self.instr.get_output_state()
        if state == True:
            self.instr.rf_off()
            btn.setChecked(False)
        else:
            self.instr.rf_on()
            btn.setChecked(True)
        
    def signal_handler(self, message):
        super().signal_handler(message)
        elem = self.view.elem
        if 'LEVEL' in message:
           elem['LEVEL_LINE'].setText(self.value_to_str(round(message['LEVEL'], 2), 'dBm'))
        if 'FREQUENCY' in message:
            elem['FREQ_LINE'].setText(self.value_to_str(round(message['FREQUENCY'], 2), 'MHz'))
        if 'RF_STATE' in message:
            elem['BTN_RF_ON'].setDown(message['RF_STATE'])
        if 'MODULATION' in message:
            elem['BTN_MOD_ON'].setDown(message['MOD_STATE'])

            
        
