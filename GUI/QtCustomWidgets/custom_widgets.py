from PyQt6.QtWidgets import QLineEdit

class ClickableLineEdit(QLineEdit):
    """QLineEdit with a click event"""
    def __init__(self, text: str, parent: object=None) -> None:
        super().__init__(parent)
        self.setText(text)

    def event(self, event: object) -> bool:
        """Events handler"""
        if event.type() == event.Type.MouseButtonPress and not self.isEnabled():
            self.setEnabled(True)
            self.setFocus()
            return True
        return super().event(event)