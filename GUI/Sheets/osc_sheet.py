from .instr_sheet import InstrumentSheet

from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget
from PyQt6.QtWidgets import QGroupBox, QFrame
from PyQt6.QtGui import QPainter, QPen, QColor, QBrush

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class OscilloscopeSheet(InstrumentSheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)


        scale_row = self.ip_row + 2
        pos_row = scale_row + 1

        scale_label_width = 65
        scale_edit_line_width = 40

        hor_col = self.zero_col + 19

        ch_row = pos_row + 2
        ch_btn_width = 34
        dx = 5

        args = scale_label_width, scale_edit_line_width
        self.add_control_elem('VERT_SCALE', self.zero_col, scale_row, 'Scale, mV:', '20', *args)
        self.add_control_elem('VERT_POS', self.zero_col, pos_row , 'Offset, mV:', '0', *args)

        
        self.add_control_elem('HOR_SCALE', hor_col, scale_row, 'Scale, ms:', '5', *args)
        self.add_control_elem('HOR_POS', hor_col, pos_row , 'Offset, %:', '0', *args)

        self.add_label('VERT',  7, self.ip_row + 1, 'VERTICAL').setProperty('class', 'osc_label')
        self.add_label('HOR', hor_col + 7, self.ip_row + 1, 'HORISONTAL').setProperty('class', 'osc_label')

        self.add_frame('CH1', self.zero_col, ch_row, 4, 4, 42, 29, 'ch1_frame')      
        self.add_btn('CH1', self.zero_col, ch_row, "CH1", ch_btn_width).setProperty('class', 'btn_ch1')
        self.elem['BTN_CH1'].setCheckable(True)

        self.add_frame('CH2', self.zero_col + dx, ch_row, 4, 4, 42, 29, 'ch2_frame')
        self.add_btn('CH2', self.zero_col + dx, ch_row, "CH2", ch_btn_width).setProperty('class', 'btn_ch2')
        self.elem['BTN_CH2'].setCheckable(True)

        self.add_frame('CH3', self.zero_col + 2*dx, ch_row, 4, 4, 42, 29, 'ch3_frame')
        self.add_btn('CH3', self.zero_col + 2*dx, ch_row, "CH3", ch_btn_width).setProperty('class', 'btn_ch3')
        self.elem['BTN_CH3'].setCheckable(True)
        
        self.add_frame('CH4', self.zero_col + 3*dx, ch_row, 4, 4, 42, 29, 'ch4_frame')
        self.add_btn('CH4', self.zero_col + 3*dx, ch_row, "CH4", ch_btn_width).setProperty('class', 'btn_ch4')
        self.elem['BTN_CH4'].setCheckable(True)
        
        self.add_btn('HI_RES', self.zero_col + 4*dx, ch_row, "HiRes", 50).setCheckable(True)

        param = ch_row - 1, 'MEG', ch_btn_width
        self.add_label('CH1_IMP', self.zero_col,  *param).setProperty('class', 'osc_imp_label')
        self.add_label('CH2_IMP', self.zero_col + dx, *param).setProperty('class', 'osc_imp_label')
        self.add_label('CH3_IMP', self.zero_col + 2*dx, *param).setProperty('class', 'osc_imp_label')
        self.add_label('CH4_IMP', self.zero_col + 3*dx, *param).setProperty('class', 'osc_imp_label')

        self.add_btn('RUN', 31, self.zero_row, 'Run/Stop')
        self.add_btn('SINGLE', 31, self.zero_row+1, 'Single')

        trig_col = self.zero_col + 26
        self.add_label('TRIG',  trig_col, ch_row, 'Trigger:')
        self.add_btn('TRIG_FORCE', trig_col + 5, ch_row, "Force")

      
        