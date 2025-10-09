from Instruments.scpi_instr import Instrument

from System.logger import get_logger

logger = get_logger(__name__)


class DSG830(Instrument):
    """
    Rigol DSG830 microwave generator
    """

    MAX_LEVEL = 20
    MIN_LEVEL = -110

    MAX_FREQUENCY = 3e9
    MIN_FREQUENCY = 9e3

    def __init__(self, ip: str) -> None:
        super().__init__(ip)
        self.type = "Microwave Generator"

    @Instrument.device_checking
    def factory_preset(self) -> None:
        """Reset the instrument to factory settings."""
        self.send(":SYSTem:PRESet:TYPE FACtory")

    # Frequency control (FREQ)
    @Instrument.device_checking
    def set_frequency(self, frequency: float) -> None:
        """Set the output frequency in Hz"""
        if self.MIN_FREQUENCY <= frequency <= self.MAX_FREQUENCY:
            self.send(f":FREQuency {frequency}")
            self.state_changed.emit({"FREQUENCY": frequency})
        else:
            logger.warning("Frequency out of range")

    @Instrument.device_checking
    def get_frequency(self) -> float:
        """Query the output frequency in Hz"""
        return float(self.send(":FREQuency?"))

    # Level of output signal power (LEVEL)
    @Instrument.device_checking
    def set_level(self, level: float) -> None:
        """
        Set the output level in dBm
        """
        if self.MIN_LEVEL <= level <= self.MAX_LEVEL:
            self.send(f":LEV {level}dBm")
            self.state_changed.emit({"LEVEL": level})
        else:
            logger.warning("Output level out of range")

    def set_min_level(self) -> None:
        """Set the output level to the minimum level"""
        self.set_level(self.MIN_LEVEL)

    @Instrument.device_checking
    def get_level(self) -> float:
        """Query the output level in dBm"""
        return float(self.send(":LEV?"))

    # Turn ON/OFF the output signal (RF/on)
    @Instrument.device_checking
    def get_output_state(self) -> int:
        """
        Query the on/off state of the RF output
        """
        return int(self.send(":OUTPut?"))

    @Instrument.device_checking
    def rf_on(self) -> None:
        """Turn the RF output on"""
        self.send(":OUTPut ON")
        self.state_changed.emit({"RF_STATE": True})

    @Instrument.device_checking
    def rf_off(self) -> None:
        """Turn the RF output off"""
        self.send(":OUTPut OFF")
        self.state_changed.emit({"RF_STATE": False})

    # Turn Modulation ON/OFF of the output signal (Mod/on)
    @Instrument.device_checking
    def get_modulation_state(self) -> int:
        """Query the on/off state of the Modulation"""
        return int(self.send(":MODulation:STATe?"))

    @Instrument.device_checking
    def modulation_on(self) -> None:
        """Turn the Modulation ON"""
        self.send(":MODulation:STATe ON")
        self.state_changed.emit({"MOD_STATE": True})

    @Instrument.device_checking
    def modulation_off(self) -> None:
        """Turn the Modulation OFF"""
        self.send(":MODulation:STATe OFF")
        self.state_changed.emit({"MOD_STATE": False})

    @Instrument.device_checking
    def get_settings_from_device(self) -> None:
        """Query all settings from the device and emit state_changed signal"""

        self.state_changed.emit(
            {
                "FREQUENCY": self.get_frequency(),
                "LEVEL": self.get_level(),
                "RF_STATE": self.get_output_state(),
                "MOD_STATE": self.get_modulation_state(),
            }
        )
