from PyQt6.QtWidgets import QWidget

class MainWindow(QWidget):
    sheet = dict()

    def __init__(self):
        super().__init__()
