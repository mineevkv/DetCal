from PyQt6.QtCore import QObject, pyqtSignal

class MeasurementModel(QObject):
    data_changed = pyqtSignal(list)  # Сигнал при изменении данных
    
    def __init__(self):
        super().__init__()