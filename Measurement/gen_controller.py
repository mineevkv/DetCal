from .instr_controller import InstrumentController

from System.logger import get_logger
logger = get_logger(__name__)

class GenController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr, instr_sheet)

        self.instr.connect()
        
    def connect_signals(self): 
        super().connect_signals()
        self.view.elem['btn_rf_on'].clicked.connect(self.btn_rf_on_click)
        self.view.elem['btn_freq'].clicked.connect(self.btn_freq_set_click)
        self.view.elem['btn_level'].clicked.connect(self.btn_level_set_click)

    def btn_freq_set_click(self):
        freq = float(self.view.elem['freq_line'].text())*1e6
        self.instr.set_frequency(freq)

    def btn_level_set_click(self):
        level = float(self.view.elem['level_line'].text())
        self.instr.set_level(level)

    def btn_rf_on_click(self):
        if not self.instr.is_initialized():
            btn = self.view.elem['btn_rf_on']
            btn.setDown(False)
            btn.setText("ERROR")
            return
        
        button_state = self.btn_rf_on.isDown()

        print(button_state) # TODO: fix


    def signal_handler(self, message):
        super().signal_handler(message)
        elem = self.view.elem
        if 'level' in message:
           elem['level_line'].setText(str(message['level']))
        if 'frequency' in message:
            elem['freq_line'].setText(str(message['frequency']/1e6))
        if 'rf_state' in message:
            elem['btn_rf_on'].setDown(message['rf_state'])
        if 'modulation' in message:
            elem['btn_mod_on'].setDown(message['mod_state'])
        
