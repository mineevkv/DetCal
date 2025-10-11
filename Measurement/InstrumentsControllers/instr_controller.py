from PyQt6.QtCore import QTimer, QObject
from abc import  abstractmethod
from GUI.sibmit_dialog import SubmitDialog
from Instruments.scpi_instr import Instrument
from typing import  Any

from Measurement.abstract_controller import Controller

from GUI.palette import *

from System.logger import get_logger

logger = get_logger(__name__)


class InstrumentController(Controller):
    """
    Abstract class for instrument controller.

    This class is used as a base class for all instrument controllers.
    It contains an instrument object and an instrument sheet object.
    It also contains methods for initializing signals, setting the connection field,
    and initializing the progress timer.

    """

    def __init__(self, instr: Instrument, instr_sheet: QObject) -> None:
        super().__init__()
        self.instr = instr
        self.view = instr_sheet

        self.init_signals()
        self.set_connection_field()
        self.init_progress_timer()

        self.disable_control_elements()
        self.instr.connect()

    # Controller
    @abstractmethod
    def init_signals(self) -> None:
        """
        Initialize signals for instrument controller.

        This method is used to initialize the signals for the instrument controller.
        It sets up the connections for the buttons and the instrument state and progress changed signals.

        """
        self.view.elem["BTN_IP"].clicked.connect(self.btn_connect_click)
        self.instr.state_changed.connect(self.signal_handler)
        self.instr.progress_changed.connect(self.progress)

    @abstractmethod
    def unlock_buttons(self) -> None:
        """
        Unlock buttons for instrument controller.

        This method is used to unlock the buttons for the instrument controller.
        It hides the QLabels (buttons shields) that are not needed for the current state of the instrument.
        """
        for key, element in self.view.elem.items():
            if "FREEZEBTN_" in key:
                element.hide()

    @abstractmethod
    def lock_buttons(self) -> None:
        """
        Lock buttons for instrument controller.

        This method is used to lock the buttons for the instrument controller.
        It shows the QLabels (buttons shields) that are cover the buttons.
        """
        for key, element in self.view.elem.items():
            if "FREEZEBTN_" in key:
                element.show()

    @abstractmethod
    def signal_handler(self, message: dict) -> None:
        """
        Handle signals from instrument.

        This method is used to handle signals from the instrument.
        It updates the instrument sheet with the new values from the instrument.
        """
        # Validate message structure
        if not isinstance(message, dict):
            raise TypeError(f"Expected dict, got {type(message).__name__}")

        handlers = {
            "IP": self._handle_ip_update,
            "MODEL": self._handle_model_update,
            "TYPE": self._handle_type_update,
            "THREAD": self._handle_thread_update,
        }

        for key, value in message.items():
            if key in handlers:
                try:
                    handlers[key](value)
                except Exception as e:
                    logger.error(f"Error handling {key}: {e}")

    def _handle_ip_update(self, ip_address: str) -> None:
        """Handle IP address updates."""
        self.view.elem["IP_CLICKLINE"].setText(ip_address)
        self.set_connection_field()

    def _handle_model_update(self, model: str) -> None:
        """Handle model information updates."""
        self.view.elem["MODEL_LABEL"].setText(model)

    def _handle_type_update(self, instrument_type: str) -> None:
        """Handle instrument type updates."""
        self.view.box.setTitle(instrument_type)

    def _handle_thread_update(self, thread_info: Any) -> None:
        """Handle thread completion."""
        self.instr.connect_thread = None

    def lock_control_elements(self) -> None:
        """Lock control elements."""
        self.lock_buttons()

    def unlock_control_elements(self) -> None:
        """Unlock control elements."""
        self.unlock_buttons()

    def is_connect(self) -> bool:
        """Check if instrument is connected."""
        if self.instr is not None and self.instr.is_initialized():
            return True
        else:
            return False

    def set_connection_field(self) -> None:
        """Set connection field."""
        label = self.view.elem["IP_STATUS_LABEL"]
        line_edit = self.view.elem["IP_CLICKLINE"]

        if self.is_connect():
            label.setText("Connected")
            label.setStyleSheet(f"color: {GREEN}")
            line_edit.setEnabled(False)
        else:
            label.setStyleSheet(f"color: {RED}")
            label.setText("No connection")
            line_edit.setEnabled(True)

    def btn_connect_click(self) -> None:
        """Button connect click."""
        new_ip = self.view.elem["IP_CLICKLINE"].text()
        new_ip = new_ip.strip()

        if not self.is_valid_ip(new_ip):
            logger.warning(f"Invalid IP address: {new_ip}")
            return

        if self.is_connect():
            logger.debug(f"{self.__class__.__name__}: connect already running")
            question = (
                "Connection is in progress!\nDo you want to cancel and reconnect?"
            )
            if not SubmitDialog.show_submit_dialog(question):
                return
            else:
                self.instr.connect_thread.terminate()
                logger.debug(
                    f"{self.__class__.__name__}: connect thread terminated by user"
                )

            # current_ip = self.instr.get_ip()
            # if current_ip == new_ip:
            #     logger.info(f"Already connected to {new_ip}")
            #     return

        if self.instr is not None:
            self.instr.set_ip(new_ip)
            self.instr.connect()
            self.timer.start(300)

    def init_progress_timer(self) -> None:
        """Initialize progress timer."""
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.progress_update)
        self.timer.start(300)

    def progress(self, value) -> None:
        """Set the progress in the progress bar."""
        self.view.elem["PROGRESS"].setValue(value)
        if value > 99:
            self.progress_hide()
            self.check_initialization()

    def progress_update(self) -> None:
        """Update progress bar."""
        value = self.view.elem["PROGRESS"].value()
        if value < 100:
            self.progress(value + 1)

    def progress_hide(self) -> None:
        """Hide progress bar."""
        self.timer.stop()
        self.progress(0)

    def is_valid_ip(self, ip: str) -> bool:
        """
        Check if given IP address is valid
        """
        parts = ip.split(".")
        if len(parts) != 4:
            return False
        for part in parts:
            if not part.isdigit():
                return False
            if int(part) < 0 or int(part) > 255:
                return False
        return True

    def check_initialization(self) -> None:
        """Check if instrument is initialized and enable/disable control elements."""
        if self.instr.is_initialized():
            self.enable_control_elements()
        else:
            self.disable_control_elements()

    def disable_control_elements(self) -> None:
        """Disable control elements."""
        for key in self.view.elem.keys():
            if key not in self.view.ip_keys:
                self.view.elem[key].setEnabled(False)

    def enable_control_elements(self) -> None:
        """Enable control elements."""
        if self.instr.model in self.instr.MODELS:
            for key in self.view.elem.keys():
                self.view.elem[key].setEnabled(True)
        else:
            logger.error(
                f"Instrument model {self.instr.model} not supported by this sheet"
            )
            self.disable_control_elements()

    def btn_clicked(self, btn_name: str, btn_handler: callable) -> None:
        """Connect a button to a handler function."""
        self.view.elem[f"BTN_{btn_name}"].clicked.connect(btn_handler)

    def read_line(self, line_edit: str) -> str:
        """Read text from a line edit."""
        return self.view.elem[f"{line_edit}_LINE"].text()
