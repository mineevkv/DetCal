
class Keys:
    gen = { 
            'RF_FREQUENCIES' : ('FREQ', 'MHz'),
            'RF_LEVELS' : ('LEVEL', 'dBm')
        }

    sa = {
            'SPAN_WIDE' : ('SPAN', 'MHz'),
            'RBW_WIDE' : ('RBW', 'kHz'),
            'VBW_WIDE' : ('VBW', 'kHz'),
            'REF_LEVEL' : ('REF_LEVEL', 'dB'),
            'SWEEP_POINTS' : ('SWEEP_POINTS', 'point'),
            'SPAN_NARROW' : ('SPAN_PRECISE', 'MHz'),
            'RBW_NARROW' : ('RBW_PRECISE', 'kHz'),
            'VBW_NARROW' : ('VBW_PRECISE', 'kHz')
        }
    
    osc = {
            'HOR_SCALE' : ('HOR_SCALE', 'ms')
        }
    
    def __init__(self):
        pass
    