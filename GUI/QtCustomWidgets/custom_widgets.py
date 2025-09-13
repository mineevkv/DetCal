from PyQt6.QtWidgets import QLineEdit

class ClickableLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
             
    def event(self, event):
        """Events handler"""
        if event.type() == event.Type.MouseButtonPress and not self.isEnabled():
            self.setEnabled(True)
            self.setFocus()
            return True
        return super().event(event)