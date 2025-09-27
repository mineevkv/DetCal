import os
import sys
from PyQt6.QtWidgets import QApplication

from main_controller import MainController


from System.logger import get_logger
logger = get_logger(__name__)

def main():
    os.system('cls')

    app = QApplication(sys.argv)
    with open("GUI/CSS/styles.css","r") as file:
        app.setStyleSheet(file.read())
    
    controller = MainController()
    
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
  

