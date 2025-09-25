import os
import sys
from PyQt6.QtWidgets import QApplication

from Measurement.MeasurementController.meas_controller import MeasurementController
from Documentations.protocol_creator import MeasurementProtocol
from Instruments.rsa5000vna_parcer import RSA506N_S21_Parser

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

def protocol():
    # Temp example fo generating protocol TODO: fix
    with open("results.csv", "r") as file:
        result_file = list(csv.reader(file))

    with open("Settings/meas_settings.json", "r") as file:
        settings = json.load(file)

    doc = MeasurementProtocol(result_file, settings)

def vna_parcing():
        # Parse the file
    parser = RSA506N_S21_Parser("S21files/gen_det.trs")
    data = parser.parse_file()
    
    # Access the data directly
    frequency = data['frequency']
    magnitude_db = data['magnitude_db']
    print (frequency, magnitude_db)
  
if __name__ == "__main__":
    main()
    # vna_parcing()


