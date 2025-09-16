from .instr_controller import InstrumentController

class OscController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr, instr_sheet)

        self.instr.connect()

    def connect_signals(self): 
        super().connect_signals()

        self.btn_clicked('vert_scale', self.btn_vert_scale_click)
        self.btn_clicked('vert_pos', self.btn_vert_pos_click)

        self.btn_clicked('hor_scale', self.btn_hor_scale_click)
        self.btn_clicked('hor_pos', self.btn_hor_pos_click)

        self.btn_clicked('ch1', self.btn_ch1_click)
        self.btn_clicked('ch2', self.btn_ch2_click)
        self.btn_clicked('ch3', self.btn_ch3_click)
        self.btn_clicked('ch4', self.btn_ch4_click)

        self.btn_clicked('run', self.btn_run_click)
        self.btn_clicked('single', self.btn_single_click)
        self.btn_clicked('trig_force', self.btn_trig_force_click)

    def btn_vert_scale_click(self):
        pass

    def btn_vert_pos_click(self):
        pass

    def btn_hor_scale_click(self):
        pass

    def btn_hor_pos_click(self):
        pass

    def btn_ch1_click(self):
        pass

    def btn_ch2_click(self):
        pass

    def btn_ch3_click(self):
        pass

    def btn_ch4_click(self):
        pass

    def btn_run_click(self):
        pass

    def btn_single_click(self):
        pass

    def btn_trig_force_click(self):
        pass


    def signal_handler(self, message):
        super().signal_handler(message)
        if 'vert_scale' in message:












        
        
        
        

