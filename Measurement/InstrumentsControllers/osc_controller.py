from .instr_controller import InstrumentController
from Measurement.helper_functions import refresh_obj_view

class OscController(InstrumentController):
    def __init__(self, instr, instr_sheet):
        super().__init__(instr, instr_sheet)

        self.instr.connect()
        self.hide_channel_frames()

    def connect_signals(self): 
        super().connect_signals()

        # TODO : refactor this part
        self.btn_clicked('VERT_SCALE', self.btn_vert_scale_click)
        self.btn_clicked('VERT_POS', self.btn_vert_pos_click)

        self.btn_clicked('HOR_SCALE', self.btn_hor_scale_click)
        self.btn_clicked('HOR_POS', self.btn_hor_pos_click)

        self.btn_clicked('CH1', self.btn_ch1_click)
        self.btn_clicked('CH2', self.btn_ch2_click)
        self.btn_clicked('CH3', self.btn_ch3_click)
        self.btn_clicked('CH4', self.btn_ch4_click)
        self.btn_clicked('HI_RES', self.btn_hi_res_click)

        self.btn_clicked('RUN', self.btn_run_click)
        self.btn_clicked('SINGLE', self.btn_single_click)
        self.btn_clicked('TRIG_FORCE', self.btn_trig_force_click)

    def btn_vert_scale_click(self):
        value = float(self.read_line('VERT_SCALE'))/1e3
        self.instr.set_vertical_scale(value)

    def btn_vert_pos_click(self):
        value = float(self.read_line('VERT_POS'))/1e3
        self.instr.set_vertical_position(value)

    def btn_hor_scale_click(self):
        value = float(self.read_line('HOR_SCALE'))/1e3
        self.instr.set_horizontal_scale(value)

    def btn_hor_pos_click(self):
        value = float(self.read_line('HOR_POS'))
        self.instr.set_horizontal_position(value)

    def bth_ch_handler(self, channel):
        self.instr.selected_channel = channel
        btn = self.view.elem[f'BTN_{channel.upper()}']

        if btn.isChecked():
            self.instr.channel_on()
            btn.setChecked(True)
        else:
            if int(channel[-1:]) == self.instr.get_selected_channel():
                self.instr.channel_off()
                btn.setChecked(False)
            else:
                self.instr.channel_on()
                btn.setChecked(True)

        self.show_selected_channel()
        self.set_vertical_settings()

    def show_selected_channel(self):
        channel = self.instr.get_selected_channel()
        self.selected_channel = channel
        self.hide_channel_frames()
        elem = self.view.elem
        if channel:
            elem[f'CH{channel}_FRAME'].show()
            elem['VERT_LABEL'].setProperty('class', f'osc_vert_label{channel}')
            refresh_obj_view(elem['VERT_LABEL'])

    def hide_channel_frames(self):
        elem = self.view.elem
        for channel in [1, 2, 3, 4]:
            elem[f'CH{channel}_FRAME'].hide()
        elem['VERT_LABEL'].setProperty('class', 'osc_label')
        refresh_obj_view(elem['VERT_LABEL'])


    def btn_ch1_click(self):
        self.bth_ch_handler('CH1')

    def btn_ch2_click(self):
        self.bth_ch_handler('CH2')
        
    def btn_ch3_click(self):
        self.bth_ch_handler('CH3')

    def btn_ch4_click(self):
        self.bth_ch_handler('CH4')

    def get_vertical_settings(self):
        message = {
            'VERT_SCALE': self.instr.get_vertical_scale(),
            'VERT_POS': self.instr.get_vertical_position(),
        }

        return message
    
    def set_vertical_settings(self):
        message = self.get_vertical_settings()
        self.instr.state_changed.emit(message)


    def btn_run_click(self):
        pass

    def btn_single_click(self):
        pass

    def btn_trig_force_click(self):
        pass

    def btn_hi_res_click(self):
        btn = self.view.elem[f'BTN_HI_RES']
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
        'VERT_SCALE': ('VERT_SCALE_LINE', lambda v: str(v * 1e3)),
        'VERT_POS':   ('VERT_POS_LINE',   lambda v: str(v * 1e3)),
        'HOR_SCALE':  ('HOR_SCALE_LINE',  lambda v: str(v * 1e3)),
        'HOR_POS':    ('HOR_POS_LINE',    str)
        }

        for key, (line, conv) in lines.items():
            if key in message:
                elem[line].setText(conv(message[key]))
      
        # Updating active channels
        for channel in [1, 2, 3, 4]:
            key = f'CH{channel}'
            if key in message:
                elem[f'BTN_CH{channel}'].setChecked(message[key])
        

        # Updating Hight Resolution mode
        if 'ACQUIRE_MODE' in message:
            elem['BTN_HI_RES'].setChecked(message['ACQUIRE_MODE'] == 'HIRES')

        if 'SELECT_CH' in message:
            channel = message['SELECT_CH']
            if channel is not None:
                self.hide_channel_frames()
                if channel:
                    self.view.elem[f'CH{channel}_FRAME'].show()
                    elem['VERT_LABEL'].setProperty('class', f'osc_vert_label{channel}')
                    refresh_obj_view(elem['VERT_LABEL'])

        if 'CH_ON' in message:
            channel = message['CH_ON']
            elem['BTN_HI_RES'].setChecked(message['ACQUIRE_MODE'] == 'HIRES')

        if 'TERMINATIONS' in message:
            terminations = message['TERMINATIONS']
            for channel in [1, 2, 3, 4]:
                termination = OscController.ch_impedance(terminations[f'CH{channel}']) 
                elem[f'CH{channel}_IMP_LABEL'].setText(termination)

        if 'TERMINATION' in message:
            termination = OscController.ch_impedance(message['TERMINATION']) 
            channel = self.instr.selected_channel
            elem[f'CH{channel}_IMP_LABEL'].setText(termination)
            

        if 'COUPLING' in message:
            pass

        if 'RESET' in message:
            pass
            
    @staticmethod
    def ch_impedance(termination):
        if 'FIFty' in termination:
            return '50'
        elif 'MEG' in termination:
            return 'MEG'
        
        if float(termination) > 50:
            return 'MEG'
        return '50'
