from PyQt6.QtCore import QThread, pyqtSignal
import os
import json

from Instruments.rsa5065n import RSA5065N
from Instruments.dsg830 import DSG830
from Instruments.mdo34 import MDO34


from System.logger import get_logger

logger = get_logger(__name__)


class Initializer(QThread):
    """Class for instrument initialization"""

    finished = pyqtSignal(object, object, object, object)  # emits (gen, sa, osc, error)
    settings_folder = "Settings"
    ip_list = "instr_ip.json"

    def __init__(self):
        super().__init__()
        self.load_instr_ip_settings()

    def load_instr_ip_settings(self) -> None:
        """
        Loads instrument IP settings from a JSON file.

        The file should contain key-value pairs where the key is
        the instrument name (e.g. ip_DSG830, ip_RSA5065N, ip_MDO34)
        and the value is the IP address of the instrument.

        If the file is not found, an error message is logged.
        """
        path = os.path.join(self.settings_folder, self.ip_list)
        if not os.path.exists(path):
            error_msg = f"Instrument IP file not found: {path}"
            logger.error(error_msg)
            raise FileNotFoundError(error_msg)
        ip_settings = Initializer.load_ip_from_file(path)
        for key, value in ip_settings.items():
            setattr(self, key, value)

    @staticmethod
    def load_ip_from_file(filename: str) -> dict:
        """
        Loads instrument IP settings from a JSON file.

        The file should contain key-value pairs where the key is the
        instrument name (e.g. ip_DSG830, ip_RSA5065N, ip_MDO34) and
        the value is the IP address of the instrument.

        If the file is not found, an error message is logged.

        Returns:
            dict: A dictionary containing the instrument IP settings.
        """
        try:
            with open(filename, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load instrument IPs from {filename}: {e}")
            return {}

    def run(self) -> None:
        """
        Initializes the instruments by creating their objects.

        This method attempts to create objects for the instruments specified
        in the instrument IP settings file. If any of the instruments fail
        to initialize, an error message is logged and the
        finished signal is emitted with None for the instruments that failed
        to initialize.

        Emits:
        ----------
            pyqtSignal: finished(QObject, QObject, QObject, Exception):
            Notifies that the initialization is complete.
        """
        try:
            required_ips = ['ip_DSG830', 'ip_RSA5065N', 'ip_MDO34']
            for ip_attr in required_ips:
                if not hasattr(self, ip_attr):
                    raise AttributeError(f"Missing IP address: {ip_attr}")

            instr = {
                "gen": DSG830(self.ip_DSG830),
                "sa": RSA5065N(self.ip_RSA5065N),
                "osc": MDO34(self.ip_MDO34),
            }
            self.finished.emit(instr["gen"], instr["sa"], instr["osc"], None)
        except Exception as e:
            self.finished.emit(None, None, None, e)
            logger.error(f"Failed to initialize instruments objects: {e}")
