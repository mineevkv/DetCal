
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from System.logger import get_logger

logger = get_logger(__name__)


class SubmitDialog():
    """
    Class to show a confirmation dialog box with a Yes/No buttons.
    """
    def __init__(self) -> None:
        pass


    @staticmethod
    def show_submit_dialog(question: str) -> None:
        """
        Shows a confirmation dialog box with a Yes/No buttons.

        :param question: The question to be asked in the dialog box.
        :return: None
        """
        # Create message box with Yes/No buttons
        msg_box = QMessageBox()
        msg_box.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        msg_box.setWindowTitle("Confirmation")
        msg_box.setText(question)
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        # Add Yes and No buttons
        yes_button = msg_box.addButton("Yes", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("No", QMessageBox.ButtonRole.NoRole)
        
        # Set default button
        msg_box.setDefaultButton(no_button)
        
        # Show the dialog and wait for response
        msg_box.exec()
        
        # Check which button was clicked
        if msg_box.clickedButton() == yes_button:
            logger.debug("User confirmed submission")
            return True
        else:
            logger.debug("User cancelled submission")
            return False
            