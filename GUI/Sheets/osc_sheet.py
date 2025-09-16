from .instr_sheet import InstrumentSheet

from PyQt6.QtWidgets import  QGroupBox

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class OscilloscopeSheet(InstrumentSheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)
        # self.box.setTitle("Oscilloscope")

   

        scale_row = self.ip_row + 2
        pos_row = scale_row + 1

        scale_label_width = 60
        scale_edit_line_width = 40

        args = scale_label_width, scale_edit_line_width
        self.add_control_elem('vert_scale', self.zero_col, scale_row, 'Scale, mV:', '20', *args)
        self.add_control_elem('vert_pos', self.zero_col, pos_row , 'Position:', '0', *args)

        hor_col = self.zero_col + 19
        self.add_control_elem('hor_scale', hor_col, scale_row, 'Scale, ms:', '5', *args)
        self.add_control_elem('hor_pos', hor_col, pos_row , 'Position:', '0', *args)

        self.add_label('vert',  7, self.ip_row + 1, 'VERTICAL').setProperty('class', 'osc_label')
        self.add_label('hor', hor_col + 7, self.ip_row + 1, 'HORISONTAL').setProperty('class', 'osc_label')

        ch_row = pos_row + 2
        ch_btn_width = 40
        dx = 5
        self.add_btn('ch1', self.zero_col, ch_row, "CH1", ch_btn_width)
        self.add_btn('ch2', self.zero_col + dx, ch_row, "CH2", ch_btn_width)
        self.add_btn('ch3', self.zero_col + 2*dx, ch_row, "CH3", ch_btn_width)
        self.add_btn('ch4', self.zero_col + 3*dx, ch_row, "CH4", ch_btn_width)

        param = ch_row - 1, '1 MEG', ch_btn_width
        self.add_label('ch1_imp', self.zero_col,  *param).setProperty('class', 'osc_imp_label')
        self.add_label('ch2_imp', self.zero_col + dx, *param).setProperty('class', 'osc_imp_label')
        self.add_label('ch3_imp', self.zero_col + 2*dx, *param).setProperty('class', 'osc_imp_label')
        self.add_label('ch4_imp', self.zero_col + 3*dx, *param).setProperty('class', 'osc_imp_label')

        self.add_btn('run', 31, self.zero_row, 'Run/Stop')
        self.add_btn('single', 31, self.zero_row+1, 'Single')

        trig_col = self.zero_col + 26
        self.add_label('trig',  trig_col, ch_row, 'Trigger:')
        self.add_btn('trig_force', trig_col + 5, ch_row, "Force")
