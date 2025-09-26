from PyQt6.QtCore import QObject
import csv
import json
from Documentations.protocol_creator import MeasurementProtocol

from Measurement.helper_functions import is_equal_frequencies


from System.logger import get_logger
logger = get_logger(__name__)

class InfographicController(QObject):
        
    def __init__(self,  model, view,):
        super().__init__(model, view)
        self.view = view.ig
        self.model = model
        self.connect_signals()
        
    def connect_signals(self): 
        elem =self.view.elem
        elem['freq_cobmo'].currentTextChanged.connect(self.selector_handler)
        elem['btn_protocol'].clicked.connect(self.btn_protocol_click)

    def selector_handler(self):
        selected_freq = self.view.get_current_frequency()
        if selected_freq is None:
            return
        data = self.model.get_data_from_frequency(selected_freq)
        self.view.plot_data_from_frequency(data)

    def btn_protocol_click(self):
        selected_frequency = self.view.get_current_frequency()
        if selected_frequency is None:
            return
        
        with open("results.csv", "r") as file:
            next(file) # skip header
            result_file = list(csv.reader(file))
            data = []
            for row in result_file:
                if is_equal_frequencies(row[0], selected_frequency):
                    data.append(row)

        with open("Settings/meas_settings.json", "r") as file:
            settings = json.load(file)
            doc = MeasurementProtocol(data, settings)