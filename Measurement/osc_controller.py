from .instr_controller import InstrumentController

class OscController(InstrumentController):
    def __init__(self, instr, widget):
        super().__init__(instr, widget)