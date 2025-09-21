from .instr_controller import InstrumentController

from System.logger import get_logger
logger = get_logger(__name__)

class SAController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr,instr_sheet)

        self.instr.connect()

    def connect_signals(self): 
        super().connect_signals()
        elem = self.view.elem
        elem['btn_center_freq'].clicked.connect(self.btn_center_freq_click)
        elem['btn_span'].clicked.connect(self.btn_span_click)
        elem['btn_rbw'].clicked.connect(self.btn_rbw_click)
        elem['btn_vbw'].clicked.connect(self.btn_vbw_click)
        elem['btn_single'].clicked.connect(self.btn_single_click)

    def signal_handler(self, message):
        super().signal_handler(message)
        elem = self.view.elem
        if 'center_freq' in message:
            elem['center_freq_line'].setText(str(self.remove_zeros(message['center_freq']/1e6)))
        if 'span' in message:
            elem['span_line'].setText(str(self.remove_zeros(message['span']/1e6)))
        if 'rbw' in message:
            elem['rbw_line'].setText(str(self.remove_zeros(message['rbw']/1e3)))
        if 'vbw' in message:
            elem['vbw_line'].setText(str(self.remove_zeros(message['vbw']/1e3)))

        if 'reference level' in message:
            pass
        if 'sweep_time' in message:
            pass
        if 'sweep_points' in message:
            pass
        if 'trace_format' in message:
            pass
        if 'single_sweep' in message:
            pass
        if 'continuous_sweep' in message:
            pass
        if 'configure' in message:
            pass

    def btn_center_freq_click(self): # TODO: freq_line_edit_handler
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