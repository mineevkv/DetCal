
class Keys:
    gen = { 
            'RF_frequencies' : ('freq', 'MHz'),
            'RF_levels' : ('level', 'dBm')
        }

    sa = {
            'SPAN_wide' : ('span', 'MHz'),
            'RBW_wide' : ('rbw', 'kHz'),
            'VBW_wide' : ('vbw', 'kHz'),
            'REF_level' : ('ref_level', 'dB'),
            'SWEEP_points' : ('sweep_points', 'point'),
            'SPAN_narrow' : ('span_precise', 'MHz'),
            'RBW_narrow' : ('rbw_precise', 'kHz'),
            'VBW_narrow' : ('vbw_precise', 'kHz')
        }
    
    osc = {
            'HOR_scale' : ('hor_scale', 'ms')
        }
    
    def __init__(self):
        pass
    