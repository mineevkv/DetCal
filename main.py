import os
import sys
from PyQt6.QtWidgets import QApplication

from Measurement.MeasurementController.meas_controller import MeasurementController
from Documentations.protocol_creator import MeasurementProtocol

import csv
import json

from System.logger import get_logger
logger = get_logger(__name__)

def main():
    os.system('cls')

    app = QApplication(sys.argv)
    with open("GUI/CSS/styles.css","r") as file:
        app.setStyleSheet(file.read())
    
    controller = MeasurementController()
    controller.run()
    
    sys.exit(app.exec())
  
if __name__ == "__main__":
    # main()

    with open("results.csv", "r") as file:
        result_file = list(csv.reader(file))

    with open("Settings/meas_settings.json", "r") as file:
        settings = json.load(file)

    doc = MeasurementProtocol(result_file, settings)
    # doc.fill_document()

