from .abstract_sheet import Sheet

from PyQt6.QtWidgets import  QGroupBox, QCheckBox, QRadioButton, QButtonGroup, QTextBrowser
from PyQt6 import QtCore
from PyQt6.QtCore import Qt

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class MeasurementSheet(Sheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)
        self.box.setTitle("Measurement parameters")

        # File operation fields
        default_col = 19 
        load_col = default_col + 7
        save_col = load_col + 7
        set_col = save_col + 7

        self.add_custom_btn('save_settings', save_col, self.zero_row, 'Save', 60, self.elem_hight)
        self.add_custom_btn('load_settings',  load_col, self.zero_row, 'Load', 60, self.elem_hight)
        self.add_custom_btn('set_default',  default_col, self.zero_row, 'Default', 60, self.elem_hight, 'btn_default')
        self.add_label('settings_status', set_col, self.zero_row, 'Settings saved', 100).setProperty('class', 'settings_status_label')
        self.elem['settings_status_label'].hide()
        
        # Generator and measurement fields
        edit_line_width = 63

        freq_row = self.zero_row + 2
        level_row = freq_row + 1

        self.add_gen_elem('freq', self.zero_col, freq_row, edit_line_width, 'Frequency, MHz:', 'START:', '0', 'STOP:', '0')
        self.add_gen_elem('level', self.zero_col, level_row, edit_line_width, 'Output level, dBm:', 'MIN:', '-150', 'MAX:', '-150')

        start_col = 52
        self.add_check_box('unlock_stop', start_col, self.zero_row, 'Unlock STOP')
        self.add_custom_btn('start', start_col, freq_row, 'START', 120, 45, 'btn_start')
        self.add_custom_btn('stop',  start_col, freq_row, 'STOP', 120, 45, 'btn_stop').hide()

        progress_col = 52
        self.add_progress_bar('progress', progress_col, self.zero_row+1, 320, self.elem_hight).hide()
        self.add_progress_label('progress', progress_col+13, self.zero_row+2, "Waiting...", 68).hide()
        self.add_custom_btn('save_result',  72, freq_row, 'SAVE', 120, 45, 'btn_save_result').setEnabled(False)

        # Spectrum analyzer and apply fields
        points_row = level_row + 2
        span_row = points_row + 1
        rbw_row = span_row + 1
        vbw_row = rbw_row + 1
        ref_level_row = vbw_row + 1
        self.add_sa_elem('sweep_points', self.zero_col, points_row, edit_line_width, 'Sweep points:', '0')
        self.add_sa_elem('span', self.zero_col, span_row, edit_line_width, 'SPAN, MHz:', '0')
        self.add_sa_elem('rbw', self.zero_col, rbw_row, edit_line_width, 'RBW, kHz:', '0')
        self.add_sa_elem('vbw', self.zero_col, vbw_row, edit_line_width, 'VBW, kHz:', '0')
        self.add_sa_elem('ref_level', self.zero_col, ref_level_row, edit_line_width, 'Ref level, dB:', '0')

        precise_col = self.zero_col + 20
        self.add_check_box('precise_enabled', precise_col, points_row, 'Precise measurement')
        self.add_sa_elem('span_precise', precise_col, span_row, edit_line_width, 'SPAN, MHz:', '0')
        self.add_sa_elem('rbw_precise', precise_col, rbw_row, edit_line_width, 'RBW, kHz:', '0')
        self.add_sa_elem('vbw_precise', precise_col, vbw_row, edit_line_width, 'VBW, kHz:', '0')

        self.add_custom_btn('apply', 40, span_row, 'APPLY', 60, 69, 'btn_apply')
        
        # Oscilloscope fields

        hor_scale_row = ref_level_row + 2

        ch1_col = self.zero_col + 10
        ch2_col = ch1_col + 6
        ch3_col = ch2_col + (ch2_col - ch1_col)
        ch4_col = ch3_col + (ch2_col - ch1_col)
        hi_res_col = ch4_col

        self.add_osc_elem('hor_scale', self.zero_col, hor_scale_row, edit_line_width, 'Horizontal scale, ms/div:', '0')
        self.add_check_box('hight_res_box', hi_res_col , hor_scale_row, 'High resolution')

        imp_row = hor_scale_row + 1

 
        self.add_label('impedance', self.zero_col, imp_row, 'Impedance:', 100).setProperty('class', 'meas_label_osc')
        self.impedance_group =  QButtonGroup()
        impedance_buttons = [
        self.add_radio_btn('rb_meg', ch1_col, imp_row, 'MEG'),
        self.add_radio_btn('rb_50ohm', ch2_col, imp_row, '50 Ohm')
        ]
        for rb in impedance_buttons :
            self.impedance_group.addButton(rb)
        
        
        coup_row = imp_row + 1
        self.add_label('coupling', self.zero_col, coup_row, 'Coupling:', 100).setProperty('class', 'meas_label_osc')
        self.coupling_group =  QButtonGroup(parent=self.box)
        coupling_buttons = [
            self.add_radio_btn('rb_dc', ch1_col, coup_row, 'DC'),
            self.add_radio_btn('rb_ac', ch2_col, coup_row, 'AC')
        ]
        for rb in coupling_buttons :
            self.coupling_group.addButton(rb)

        ch_row = coup_row + 1
        self.add_label('channel', self.zero_col, ch_row, 'Сhannel:', 100).setProperty('class', 'meas_label_osc')
        self.channel_group =  QButtonGroup(parent=self.box)
        channel_buttons = [
            self.add_radio_btn('re_ch1', ch1_col, ch_row, 'CH1'),
            self.add_radio_btn('re_ch2', ch2_col, ch_row, 'CH2'),
            self.add_radio_btn('re_ch3', ch3_col, ch_row, 'CH3'),
            self.add_radio_btn('re_ch4', ch4_col, ch_row, 'CH4')
        ]
        for rb in channel_buttons:
            self.channel_group.addButton(rb)

        # Status bar field
        self.elem['status_bar'] = QTextBrowser(parent=self.box)
        self.elem['status_bar'].setGeometry(QtCore.QRect(self.x_col[self.zero_col],self.y_row[ch_row+3], 800, 25))
        self.elem['status_bar'].setReadOnly(True)
        self.elem['status_bar'].setText('Ready')
        self.elem['status_bar'].setProperty('class', 'status_bar')
        

        # self.rb_impedance.toggled.connect(self.rb_impedance_toggled)

    def rb_impedance_toggled(self, checked):
        if checked:
            pass
            # self.elem['hor_scale'].setReadOnly(False)
        else:
            # self.elem['hor_scale'].setReadOnly(True)
            pass


    def add_gen_elem(self, key, col, row, width, text, text_min, value_min, text_max, value_max):
        align_rvc = Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
        align_lvc = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter 

        self.add_label(key, col, row, text, 130).setProperty('class', 'meas_label_gen')

        self.add_label(f"{key}_min", col+14, row, text_min, 45).setAlignment(align_rvc)
        self.add_line_edit(f"{key}_min", col+19, row, value_min, width).setAlignment(align_rvc)

        self.add_label(f"{key}_max", col+26, row, text_max, 45).setAlignment(align_rvc)
        self.add_line_edit(f"{key}_max", col+31, row, value_max, width).setAlignment(align_rvc)

        self.add_label(f"{key}_points", col+38, row, 'POINTS:', 50).setAlignment(align_lvc)
        self.add_line_edit(f"{key}_points", col+44, row, '0', width).setAlignment(align_rvc)

    def add_sa_elem(self, key, col, row, width,  text, value):
        label_width = 100
        self.add_label(key, col, row, text, label_width).setProperty('class', 'meas_label_sa')
        self.add_line_edit(f"{key}", col + label_width//10, row, value, width).setAlignment(Qt.AlignmentFlag.AlignRight)

    def add_osc_elem(self, key, col, row, width, text, value):
        label_width = 190
        self.add_label(key, col, row, text, label_width).setProperty('class', 'meas_label_osc')
        self.add_line_edit(f"{key}", col + label_width//10, row, value, width).setAlignment(Qt.AlignmentFlag.AlignRight)
        

    def enable_precise(self, state):
        for key in ['span_precise_label', 'span_precise_line',
                    'rbw_precise_label', 'rbw_precise_line',
                    'vbw_precise_label', 'vbw_precise_line']:
            self.elem[key].setEnabled(state)

    def add_custom_btn(self, key,  col, row, text, width, hight, elem_class = None):
        btn = self.add_btn(key, col, row, text, width)
        btn.setFixedHeight(hight)
        if elem_class is not None: 
            btn.setProperty('class', elem_class)
        return btn
    
    def add_progress_label(self, key, col, row, text, width):
        label = self.add_label(key, col, row, text, width)
        label.setProperty('class', 'meas_progress_label')
        label.setAlignment(Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.shift_position(label, shift_x=-4, shift_y=13)
        return label
    
    #Line edit handlers
    def line_edit_changed(self, line_edit):
        line_edit.setStyleSheet(f"color: {SURFGREEN};")

    def set_line_edit_unchanged(self):
        for line_edit in self.elem.values():
            if isinstance(line_edit, QLineEdit):
                line_edit.setStyleSheet(f"")
    


