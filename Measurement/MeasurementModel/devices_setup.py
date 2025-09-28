import time

class DevicesSetup():
    def __init__(self):
        pass

    @staticmethod
    def setup(**kwargs):
        gen = kwargs['gen']
        sa = kwargs['sa']
        osc = kwargs['osc']
        settings = kwargs['settings']
    
        DevicesSetup.gen_setup(gen, settings)
        DevicesSetup.sa_setup(sa, settings)
        DevicesSetup.osc_setup(osc, settings)


    @staticmethod
    def gen_setup(gen, settings):
        gen.factory_preset()
        gen.set_min_level()
        

    @staticmethod
    def sa_setup(sa, settings):
        sa.set_swept_sa()
        sa.set_ref_level(settings['REF_LEVEL'])
        sa.set_sweep_time(settings['SWEEP_TIME'])
        sa.set_sweep_points(settings['SWEEP_POINTS'])
        sa.trace_clear_all()
        sa.set_format_trace_bin()

    @staticmethod
    def osc_setup(osc, settings):
        osc.reset()
        time.sleep(2)
        osc.get_settings_from_device()

        osc.channel_off(1) # CH1 is default channel
        channel = settings['CHANNEL']
        osc.select_channel(channel)
        if settings['IMPEDANCE_50OHM']:
            osc.set_50Ohm_termination()
        if settings['COUPLING_DC']:
            osc.set_coupling('DC')
        osc.set_vertical_scale(1) # 1V/div
        osc.set_vertical_position(0)
        osc.channel_on(channel)
        osc.set_bandwidth('FULL')
        if settings['HIGH_RES']:
            osc.set_high_res_mode()
        osc.set_horizontal_scale(settings['HOR_SCALE'])
        osc.set_horizontal_position(0)

        osc.set_measurement_source(channel)
        osc.set_measurement_type('AMPLITUDE')

        osc.set_trigger_type('EDGE')
        osc.set_trigger_source(channel)
        osc.set_trigger_level(0)

        osc.stop_after_sequence()
        osc.set_data_source(channel)
        osc.set_data_points(10000)
        osc.set_binary_data_format()
        time.sleep(0.1)
        