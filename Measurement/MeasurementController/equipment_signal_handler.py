from ..gen_controller import GenController
from ..sa_controller import SAController
from ..osc_controller import OscController

from .abstract_signal_handler import SignalHandler


from System.logger import get_logger
logger = get_logger(__name__)

class EquipmentSignalHandler(SignalHandler):
    def __init__(self):
        super().__init__()

    @staticmethod
    def handler(meas_controller, message):
        logger.debug('MeasController: equipment signals handler')

        for instr, controller in (
            ('gen', GenController),
            ('sa', SAController),
            ('osc', OscController)
        ):
            if instr in message:
                try:
                    if hasattr(meas_controller.model, instr) and getattr(meas_controller.model, instr):
                        logger.debug(f'Create {controller.__name__}')
                        setattr(meas_controller, f'{instr}_controller',
                                controller(getattr(meas_controller.model, instr), getattr(meas_controller.view, instr)))
                except AttributeError as e:
                    logger.error(f"Failed to set instrument controllers: {e}")