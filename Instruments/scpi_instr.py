from Instruments.visacom import VisaCom
from functools import wraps
import pyvisa
from PyQt6.QtCore import QThread, QObject, pyqtSignal
from abc import abstractmethod
import time

from System.logger import get_logger

logger = get_logger(__name__)


class Instrument(VisaCom, QObject):
    """Abstract class for SCPI Instrument"""

    MODELS = []  # Abstract list of supported instrument models

    state_changed = pyqtSignal(dict)  # Signal to notify settings changes
    progress_changed = pyqtSignal(int)  # Signal to current progress status (0-100)

    def __init__(self, ip: str) -> None:
        VisaCom.__init__(self)
        QObject.__init__(self)
        self.initialized = False
        self.connect_thread = None
        self.ip = None
        self.model = "None"
        self.type = "No Instrument"

        self.set_ip(ip)

    def __del__(self):
        if self.instr is not None:
            self.instr.close()
            logger.info(f"Disconnected from {self.model} at {self.ip}")

    def is_initialized(self):
        return self.initialized and self.instr is not None

    # decorator
    @staticmethod
    def device_checking(func: callable) -> callable:
        """
        Decorator to check if device is connected and initialized
        """

        def wrapper(self, *args, **kwargs) -> callable:
            if self.is_initialized():
                return func(self, *args, **kwargs)
            logger.error("Device is not initialized")

        return wrapper

    @abstractmethod
    def get_settings_from_device(self) -> None:
        """Query all settings from the device and emit state_changed signal"""
        pass

    def get_idn(self) -> str:
        """Query the *IDN? command from the instrument."""
        idn = self.send("*IDN?")
        time.sleep(0.2)
        return idn

    def reset(self) -> None:
        """Reset the instrument to factory settings."""
        self.send("*RST")
        self.state_changed.emit({"reset": True})

    def get_model(self) -> None:
        """
        Query the *IDN? command from the instrument.
        Sets the model attribute of the instrument.
        """
        idn = self.get_idn()
        _, self.model, _, _ = idn.split(",")

    def get_type(self) -> str:
        """Get the type of the instrument."""
        return self.type

    def set_ip(self, ip: str) -> None:
        """Set the IP address of the instrument."""
        if ip is not None:
            self.ip = ip
            self.state_changed.emit({"ip": self.ip})

    def get_ip(self) -> str | None:
        """Get the IP address of the instrument."""
        if self.is_initialized():
            return self.ip
        else:
            return None

    def connect(self) -> None:
        """Connect to the instrument."""
        if self.connect_thread is not None and self.connect_thread.isRunning():
            logger.debug(f"{self.__class__.__name__}: connect already running")
            return #TODO: delete this condition after adding submit dialog

        self.connect_thread = ConnectThread(self)
        logger.debug(f"{self.__class__.__name__}: connect thread created")
        self.connect_thread.start()

    def __str__(self) -> str:
        """User-friendly string representation."""
        status = "connected" if self.is_initialized() else "disconnected"
        return f"{self.type} {self.model} at {self.ip} ({status})"

    def __repr__(self) -> str:
        """Developer-friendly string representation."""
        return (
            f"{self.__class__.__name__}("
            f"ip='{self.ip}', "
            f"model='{self.model}', "
            f"type='{self.type}', "
            f"connected={self.is_initialized()})"
        )


class ConnectThread(QThread):
    """Thread to connect to instrument"""

    def __init__(self, parent: Instrument) -> None:
        super().__init__()
        self.parent = parent

    def __del__(self):
        logger.debug(f"{self.__class__.__name__}: thread deleted")

    def run(self) -> None:
        """
        Thread to connect to instrument

        Connects to the instrument using the IP address set by set_ip method.

        Emits state_changed signal with the following values:
            - IP: IP address of the instrument
            - CONNECTED: True if connected, False otherwise
            - MODEL: model of the instrument
            - TYPE: type of the instrument
            - THREAD: thread object
        """
        self.parent.progress_changed.emit(10)
        try:
            self.parent.instr = VisaCom.get_visa_resource(
                VisaCom.get_visa_string_ip(self.parent.ip)
            )
            self.parent.progress_changed.emit(50)
            if self.parent.instr is None:
                return
            self.parent.initialized = True
            self.parent.get_model()
            logger.info(f"Connected to instrument at {self.parent.ip}")
            self.parent.progress_changed.emit(60)

        except pyvisa.errors.VisaIOError:
            logger.error(f"Error connecting to instrument at {self.parent.ip}")
            self.parent.instr = None
            self.parent.initialized = False
            self.parent.model = "None"
        finally:
            self.parent.state_changed.emit(
                {
                    "IP": self.parent.ip,
                    "CONNECTED": self.parent.initialized,
                    "MODEL": self.parent.model,
                    "TYPE": self.parent.get_type(),
                    "THREAD": self.parent.connect_thread,
                }
            )
            self.parent.progress_changed.emit(80)
            self.parent.get_settings_from_device()
            self.parent.progress_changed.emit(100)
