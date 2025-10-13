from .instr_controller import InstrumentController
from PyQt6.QtCore import QObject
from Instruments.scpi_instr import Instrument
from Measurement.helper_functions import refresh_obj_view


class OscController(InstrumentController):
    """Controller for Oscilloscope."""
    ready = None
    sequence = None

    def __init__(self, instr: Instrument, instr_sheet: QObject) -> None:
        super().__init__(instr, instr_sheet)

        self.hide_channel_frames()

    def init_signals(self) -> None:
        """Initialize signals for instrument controller."""
        super().init_signals()

        button_groups = [
            # Vertical controls
            [
                ("VERT_SCALE", self.btn_vert_scale_click),
                ("VERT_POS", self.btn_vert_pos_click),
            ],
            # Horizontal controls
            [
                ("HOR_SCALE", self.btn_hor_scale_click),
                ("HOR_POS", self.btn_hor_pos_click),
            ],
            # Channel controls
            [
                ("CH1", self.btn_ch1_click),
                ("CH2", self.btn_ch2_click),
                ("CH3", self.btn_ch3_click),
                ("CH4", self.btn_ch4_click),
                ("HI_RES", self.btn_hi_res_click),
            ],
            # Trigger/Run controls
            [
                ("RUN", self.btn_run_click),
                ("SINGLE", self.btn_single_click),
                ("TRIG_FORCE", self.btn_trig_force_click),
            ],
        ]

        for group in button_groups:
            for btn_name, handler in group:
                self.btn_clicked(btn_name, handler)

    def btn_vert_scale_click(self) -> None:
        """Button vertical scale click handler."""
        value = float(self.read_line("VERT_SCALE")) / 1e3
        self.instr.set_vertical_scale(value)

    def btn_vert_pos_click(self) -> None:
        """Button vertical position click handler."""
        value = float(self.read_line("VERT_POS")) / 1e3
        self.instr.set_vertical_position(value)

    def btn_hor_scale_click(self) -> None:
        """Button horizontal scale click handler."""
        value = float(self.read_line("HOR_SCALE")) / 1e3
        self.instr.set_horizontal_scale(value)

    def btn_hor_pos_click(self) -> None:
        """Button horizontal position click handler."""
        value = float(self.read_line("HOR_POS"))
        self.instr.set_horizontal_position(value)

    def bth_ch_handler(self, channel: str) -> None:
        """Button channel click handler."""
        self.instr.selected_channel = channel
        btn = self.view.elem[f"BTN_{channel.upper()}"]

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

    def show_selected_channel(self) -> None:
        """Show selected channel frame"""
        channel = self.instr.get_selected_channel()
        self.selected_channel = channel
        self.hide_channel_frames()
        elem = self.view.elem
        if channel:
            elem[f"CH{channel}_FRAME"].show()
            elem["VERT_LABEL"].setProperty("class", f"osc_vert_label{channel}")
            refresh_obj_view(elem["VERT_LABEL"])

    def hide_channel_frames(self) -> None:
        """Hide all channel frames"""
        elem = self.view.elem
        for channel in [1, 2, 3, 4]:
            elem[f"CH{channel}_FRAME"].hide()
        elem["VERT_LABEL"].setProperty("class", "osc_label")
        refresh_obj_view(elem["VERT_LABEL"])

    def btn_ch1_click(self) -> None:
        """Button channel 1 click handler."""
        self.bth_ch_handler("CH1")

    def btn_ch2_click(self) -> None:
        """Button channel 2 click handler."""
        self.bth_ch_handler("CH2")

    def btn_ch3_click(self) -> None:
        """Button channel 3 click handler."""
        self.bth_ch_handler("CH3")

    def btn_ch4_click(self) -> None:
        """Button channel 4 click handler."""
        self.bth_ch_handler("CH4")

    def get_vertical_settings(self) -> dict:
        """Get vertical settings from instrument."""
        message = {
            "VERT_SCALE": self.instr.get_vertical_scale(),
            "VERT_POS": self.instr.get_vertical_position(),
        }

        return message

    def set_vertical_settings(self) -> None:
        """Set vertical settings to instrument."""
        message = self.get_vertical_settings()
        self.instr.state_changed.emit(message)

    def btn_run_click(self) -> None:
        """Button Run/Stop click handler."""
        if self.ready:
            self.instr.stop_acquisition()
            return

        self.instr.stop_after_runstop()
        self.instr.ready_for_acquisition()

    def btn_single_click(self) -> None:
        """Button Single/Seq click handler."""
        self.instr.stop_after_sequence()
        self.instr.ready_for_acquisition()

    def indicate_runseq_mode(self) -> None:
        """Indicate Run/Seq mode."""
        if not self.ready:
            self.make_red_runstop()
            return

        if self.sequence:
            self.make_green_singleseq()
        else:
            self.make_green_runstop()

    def make_red_runstop(self) -> None:
        """Make red Run/Stop button."""
        self.ready = False
        single = self.view.elem[f"BTN_SINGLE"]
        runstop = self.view.elem[f"BTN_RUN"]
        single.setChecked(False)
        runstop.setChecked(True)
        runstop.setProperty("class", "btn_runstop_stop")
        refresh_obj_view(runstop)

    def make_green_runstop(self) -> None:
        """Make green Run/Stop button."""
        single = self.view.elem[f"BTN_SINGLE"]
        runstop = self.view.elem[f"BTN_RUN"]
        single.setChecked(False)
        runstop.setChecked(True)
        runstop.setProperty("class", "btn_runstop_run")
        refresh_obj_view(runstop)

    def make_green_singleseq(self) -> None:
        """Make green Single/Seq button."""
        single = self.view.elem[f"BTN_SINGLE"]
        runstop = self.view.elem[f"BTN_RUN"]
        single.setChecked(True)
        runstop.setChecked(False)

    def btn_trig_force_click(self) -> None:
        """Button Trigger Force click handler."""
        self.instr.trigger_force()

    def trigger_pulled(self) -> None:
        """Handle trigger pulled event"""
        if self.sequence:
            if self.ready:
                self.ready = False
        self.indicate_runseq_mode()

    def btn_hi_res_click(self) -> None:
        """Button High Resolution click handler."""
        btn = self.view.elem[f"BTN_HI_RES"]
        if not btn.isChecked():
            self.instr.set_sample_mode()
            btn.setChecked(False)
        else:
            self.instr.set_high_res_mode()
            btn.setChecked(True)

    def signal_handler(self, message: dict) -> None:
        """Handle signals from the instrument and update the GUI accordingly."""
        super().signal_handler(message)
        elem = self.view.elem

        # Updating current measurement parameters
        lines = {
            "VERT_SCALE": ("VERT_SCALE_LINE", lambda v: str(v * 1e3)),
            "VERT_POS": ("VERT_POS_LINE", lambda v: str(v * 1e3)),
            "HOR_SCALE": ("HOR_SCALE_LINE", lambda v: str(v * 1e3)),
            "HOR_POS": ("HOR_POS_LINE", str),
        }

        for key, (line, conv) in lines.items():
            if key in message:
                elem[line].setText(conv(message[key]))

        # Updating active channels
        for channel in [1, 2, 3, 4]:
            key = f"CH{channel}"
            if key in message:
                elem[f"BTN_CH{channel}"].setChecked(message[key])

        # Updating Hight Resolution mode
        if "ACQUIRE_MODE" in message:
            elem["BTN_HI_RES"].setChecked(message["ACQUIRE_MODE"] == "HIRES")

        if "SELECT_CH" in message:
            channel = message["SELECT_CH"]
            if channel is not None:
                self.hide_channel_frames()
                if channel:
                    self.view.elem[f"CH{channel}_FRAME"].show()
                    elem["VERT_LABEL"].setProperty("class", f"osc_vert_label{channel}")
                    refresh_obj_view(elem["VERT_LABEL"])

        if "CH_ON" in message:
            channel = message["CH_ON"]
            elem["BTN_HI_RES"].setChecked(message["ACQUIRE_MODE"] == "HIRES")

        if "TERMINATIONS" in message:
            terminations = message["TERMINATIONS"]
            for channel in [1, 2, 3, 4]:
                termination = OscController.ch_impedance(terminations[f"CH{channel}"])
                elem[f"CH{channel}_IMP_LABEL"].setText(termination)

        if "TERMINATION" in message:
            termination = OscController.ch_impedance(message["TERMINATION"])
            channel = self.instr.selected_channel
            elem[f"CH{channel}_IMP_LABEL"].setText(termination)

        if "ACQUIRE_STOPAFTER" in message:
            response = message["ACQUIRE_STOPAFTER"]
            if response == "SEQUENCE":
                self.sequence = True
            elif response == "RUNSTOP":
                self.sequence = False
            self.indicate_runseq_mode()

        if "ACQUIRE_STATE" in message:
            self.ready = message["ACQUIRE_STATE"]
            self.indicate_runseq_mode()

        if "TRIGGER" in message:
            self.trigger_pulled()

    def disable_control_elements(self) -> None:
        """Disable control elements."""
        super().disable_control_elements()
        self.hide_channel_frames()


        

    @staticmethod
    def ch_impedance(termination) -> str:
        """Return impedance of channel termination."""
        if "FIFty" in termination:
            return "50"
        elif "MEG" in termination:
            return "MEG"

        if float(termination) > 50:
            return "MEG"
        return "50"
