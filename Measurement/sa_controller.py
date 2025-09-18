from .instr_controller import InstrumentController

from System.logger import get_logger
logger = get_logger(__name__)

class SAController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr,instr_sheet)

        self.instr.connect()

    def connect_signals(self): 
        super().connect_signals()
        self.view.elem['btn_center_freq'].clicked.connect(self.btn_center_freq_click)
        self.view.elem['btn_span'].clicked.connect(self.btn_span_click)
        self.view.elem['btn_rbw'].clicked.connect(self.btn_rbw_click)
        self.view.elem['btn_vbw'].clicked.connect(self.btn_vbw_click)
        self.view.elem['btn_single'].clicked.connect(self.btn_single_click)

    def signal_handler(self, message):
        super().signal_handler(message)
        if 'cetner frequency' in message:
            self.view.elem['center_freq_line'].setText(str(message['center frequency']/1e6))
        if 'span' in message:
            self.view.elem['span_line'].setText(str(message['span']/1e6))
        if 'rbw' in message:
            self.view.elem['rbw_line'].setText(str(message['rbw']/1e3))
        if 'vbw' in message:
            self.view.elem['vbw_line'].setText(str(message['vbw']/1e3))

        if 'reference level' in message:
            pass
        if 'sweep time' in message:
            pass
        if 'sweep points' in message:
            pass
        if 'trace format' in message:
            pass
        if 'single sweep' in message:
            pass
        if 'continuous sweep' in message:
            pass
        if 'configure' in message:
            pass

    def btn_center_freq_click(self):
        line_edit = self.view.elem['center_freq_line']
        try:
            freq = float(line_edit.text())*1e6
            if not 1e3 <= freq <= 6.5e9:
                raise ValueError("Center frequency must be between 1 kHz and 6.5 GHz")
            self.instr.set_center_freq(freq)
        except ValueError as e:
            logger.error(f"Error setting center frequency: {e}")
            freq = self.instr.get_center_freq()
            if freq is not None:
                line_edit.setText(str(freq/1e6))

    def freq_line_edit_handler(self, line_edit, setter, getter, units='Hz'):
        multipliers = {
            'Hz': 1,
            'kHz': 1e3,
            'MHz': 1e6,
            'GHz': 1e9
        }
        multiplier = multipliers.get(units, 1)
            
        try:
            freq = float(line_edit.text())*multiplier
            if not 1e3 <= freq <= 6.5e9:
                raise ValueError("Frequency must be between 1 kHz and 6.5 GHz")
            setter(freq)
        except ValueError as e:
            logger.error(f"Error setting frequency: {e}")
            freq = getter()
            if freq is not None:
                line_edit.setText(str(freq/multiplier))
            

    def btn_span_click(self):
        self.freq_line_edit_handler(self.view.elem['span_line'], self.instr.set_span, self.instr.get_span, 'kHz')
        

    def btn_rbw_click(self):
        pass

    def btn_vbw_click(self):
        pass

    def btn_single_click(self):
        pass

        # if 'ip' in message:
        #     self.view.elem['ip_clickline'].setText(message['ip'])
        # if 'level' in message:
        #     self.view.elem['level_line'].setText(str(message['level']))
        # if 'frequency' in message:
        #     self.view.elem['freq_line'].setText(str(message['frequency']/1e6))
        # if 'rf' in message:
        #     self.btn_rf_on.setDown(message['rf'])