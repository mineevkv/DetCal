import time


class DevicesSetup:
    """
    A class to handle the setup of all devices for measurement.

    This class provides functions to set up each device individually and a
    function to set up all devices at once.
    """

    @staticmethod
    def setup(gen: object, sa: object, osc: object, settings: dict) -> None:
        """
        Set up all devices for measurement.

        Parameters:
                gen (object): The Generator Instrument.
                sa (object): The Spectrum Analyzer Instrument
                osc (object): The Oscilloscope Instrument.
                settings (dict): A dictionary containing the settings for the devices.
        """

        DevicesSetup._validate_devices(gen, sa, osc)
        DevicesSetup._validate_settings(settings)

        DevicesSetup.gen_setup(gen, settings)
        DevicesSetup.sa_setup(sa, settings)
        DevicesSetup.osc_setup(osc, settings)

    @staticmethod
    def gen_setup(gen: object, settings: dict) -> None:
        """
        Set up the generator device for measurement.

        Parameters:
            gen (object): The generator device.
            settings (dict): A dictionary containing the settings for the generator device.
        """

        gen.factory_preset()
        gen.set_min_level()

    @staticmethod
    def sa_setup(sa: object, settings: dict) -> None:
        """
        Set up the spectrum analyzer device for measurement.

        Parameters:
            sa (object): The spectrum analyzer device.
            settings (dict): A dictionary containing the settings for the spectrum analyzer device.
        """
        sa.set_swept_sa()
        sa.set_ref_level(settings["REF_LEVEL"])
        sa.set_sweep_time(settings["SWEEP_TIME"])
        sa.set_sweep_points(settings["SWEEP_POINTS"])
        sa.trace_clear_all()
        sa.set_format_trace_bin()

    @staticmethod
    def osc_setup(osc: object, settings: dict) -> None:
        """
        Set up the oscilloscope device for measurement.

        Parameters:
            osc (object): The oscilloscope device.
            settings (dict): A dictionary containing the settings for the oscilloscope device.
        """
        osc.reset()
        time.sleep(2)
        osc.get_settings_from_device()

        osc.channel_off(1)  # CH1 is default channel
        channel = settings["CHANNEL"]
        osc.select_channel(channel)
        if settings["IMPEDANCE_50OHM"]:
            osc.set_50Ohm_termination()
        if settings["COUPLING_DC"]:
            osc.set_coupling("DC")
        osc.set_vertical_scale(1)  # 1V/div
        osc.set_vertical_position(0)
        osc.channel_on(channel)
        osc.set_bandwidth("FULL")
        if settings["HIGH_RES"]:
            osc.set_high_res_mode()
        osc.set_horizontal_scale(settings["HOR_SCALE"])
        osc.set_horizontal_position(0)

        osc.set_measurement_source(channel)
        osc.set_measurement_type("AMPLITUDE")

        osc.set_trigger_type("EDGE")
        osc.set_trigger_source(channel)
        osc.set_trigger_level(0)

        osc.stop_after_sequence()
        osc.set_data_source(channel)
        osc.set_data_points(10000)
        osc.set_binary_data_format()
        time.sleep(0.1)

    @staticmethod
    def _validate_devices(gen: object, sa: object, osc: object) -> None:
        """Validate that all device instances are provided."""
        if not all([gen, sa, osc]):
            raise ValueError("All devices (gen, sa, osc) must be provided")

    @staticmethod
    def _validate_settings(settings: dict) -> None:
        """Validate that required settings are present."""
        required_settings = [
            "REF_LEVEL", "SWEEP_TIME", "SWEEP_POINTS", 
            "CHANNEL", "HOR_SCALE"
        ]
        
        missing = [setting for setting in required_settings if setting not in settings]
        if missing:
            raise ValueError(f"Missing required settings: {missing}")
