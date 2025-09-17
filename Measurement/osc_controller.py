from .instr_controller import InstrumentController

class OscController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr, instr_sheet)

        self.instr.connect()
        self.hide_channel_frames()

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

    def bth_ch_handler(self, channel): # TODO: fix switching
        self.instr.selected_channel = channel
        btn = self.view.elem[f'btn_{channel.lower()}']
        if not btn.isChecked():
            self.instr.channel_off()
            btn.setChecked(False)
        else:
            self.instr.channel_on()
            btn.setChecked(True)
        
        self.show_selected_channel() 

    def show_selected_channel(self):
        channel = self.instr.get_selected_channel()
        self.selected_channel = channel
        self.hide_channel_frames()
        if channel:
            self.view.elem[f'ch{channel}_frame'].show()

    def hide_channel_frames(self):
        for channel in [1, 2, 3, 4]:
            self.view.elem[f'ch{channel}_frame'].hide()
  

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
        btn = self.view.elem[f'btn_hi_res']
        if not btn.isChecked():
            self.instr.set_sample_mode()
            btn.setChecked(False)
        else:
            self.instr.set_high_res_mode()
            btn.setChecked(True)

    def signal_handler(self, message):
        super().signal_handler(message)
        elem = self.view.elem

        # Updating current measurement parameters
        lines = {
        'vert_scale': ('vert_scale_line', lambda v: str(v * 1e3)),
        'vert_pos':   ('vert_pos_line',   lambda v: str(v * 1e3)),
        'hor_scale':  ('hor_scale_line',  lambda v: str(v * 1e3)),
        'hor_pos':    ('hor_pos_line',    str)
        }

        for key, (line, conv) in lines.items():
            if key in message:
                elem[line].setText(conv(message[key]))
      
        # Updating active channels
        for channel in [1, 2, 3, 4]:
            key = f'CH{channel}'
            if key in message:
                elem[f'btn_ch{channel}'].setChecked(message[key])
        

        # Updating Hight Resolution mode
        if 'acquire_mode' in message:
            print(message['acquire_mode'])
            elem['btn_hi_res'].setChecked(message['acquire_mode'] == 'HIRES')

        if 'select_ch' in message:
            channel = message['select_ch']
            if channel is not None:
                self.hide_channel_frames()
                self.view.elem[f'ch{channel}_frame'].show()
            

        # if 'vert_scale' in message: TODO: for debug
        #     elem['vert_scale_line'].setText(str(message['vert_scale']*1e3))
        # if 'vert_pos' in message:
        #     elem['vert_pos_line'].setText(str(message['vert_pos']*1e3))
        # if 'hor_scale' in message:
        #     elem['hor_scale_line'].setText(str(message['hor_scale']*1e3))
        # if 'hor_pos' in message:
        #     elem['hor_pos_line'].setText(str(message['hor_pos']))
        # if 'CH1' in message:
        #     elem['btn_ch1'].setChecked(message['CH1'])
        # if 'CH2' in message:
        #     elem['btn_ch2'].setChecked(message['CH2'])
        # if 'CH3' in message:
        #     elem['btn_ch3'].setChecked(message['CH3'])
        # if 'CH4' in message:
        #     elem['btn_ch4'].setChecked(message['CH4'])
                
        # if 'acquire_mode' in message:
        #     if message['acquire_mode' ] == 'HIRes':
        #         elem['btn_hi_res'].setChecked(True)
        #     else:
        #         elem['btn_hi_res'].setChecked(False)

