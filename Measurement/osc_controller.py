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
        self.btn_clicked('hi_res', self.btn_hi_res_click)

        self.btn_clicked('run', self.btn_run_click)
        self.btn_clicked('single', self.btn_single_click)
        self.btn_clicked('trig_force', self.btn_trig_force_click)

    def btn_vert_scale_click(self):
        value = float(self.read_line('vert_scale'))/1e3
        self.instr.set_vertical_scale(value)

    def btn_vert_pos_click(self):
        value = float(self.read_line('vert_pos'))/1e3
        self.instr.set_vertical_position(value)

    def btn_hor_scale_click(self):
        value = float(self.read_line('hor_scale'))/1e3
        self.instr.set_horizontal_scale(value)

    def btn_hor_pos_click(self):
        value = float(self.read_line('hor_pos'))
        self.instr.set_horizontal_position(value)

    def bth_ch_handler(self, channel):
        self.instr.select_channel(channel)
        btn = self.view.elem[f'btn_{channel.lower()}']
        if not btn.isChecked():
            self.instr.channel_off()
            btn.setChecked(False)
            return
        self.instr.channel_on()
        btn.setChecked(True)

    def btn_ch1_click(self):
        self.bth_ch_handler('CH1')

    def btn_ch2_click(self):
        self.bth_ch_handler('CH2')
        
    def btn_ch3_click(self):
        self.bth_ch_handler('CH3')

    def btn_ch4_click(self):
        self.bth_ch_handler('CH4')

    def btn_run_click(self):
        pass

    def btn_single_click(self):
        pass

    def btn_trig_force_click(self):
        pass

    def btn_hi_res_click(self):
        pass

    def signal_handler(self, message):
        super().signal_handler(message)
        elem = self.view.elem
        if 'vert_scale' in message:
            elem['vert_scale_line'].setText(str(message['vert_scale']*1e3))
        if 'vert_pos' in message:
            elem['vert_pos_line'].setText(str(message['vert_pos']*1e3))
        if 'hor_scale' in message:
            elem['hor_scale_line'].setText(str(message['hor_scale']*1e3))
        if 'hor_pos' in message:
            elem['hor_pos_line'].setText(str(message['hor_pos']))
        if 'CH1' in message:
            elem['btn_ch1'].setChecked(message['CH1'])
        if 'CH2' in message:
            elem['btn_ch2'].setChecked(message['CH2'])
        if 'CH3' in message:
            elem['btn_ch3'].setChecked(message['CH3'])
        if 'CH4' in message:
            elem['btn_ch4'].setChecked(message['CH4'])
