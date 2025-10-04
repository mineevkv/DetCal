from PyQt6.QtCore import QObject
import csv
import json
from ProtocolCreator.protocol_creator import MeasurementProtocol
import os
from Measurement.abstract_controller import Controller

from Measurement.MeasurementController.write_settings import WriteSettings
from Measurement.helper_functions import is_equal_frequencies


from System.logger import get_logger
logger = get_logger(__name__)

class InfographicController(Controller):
        
    def __init__(self,  meas_controller, view):
        super().__init__()
        self.view = view.ig
        self.model = meas_controller.model
        self.meas_controller = meas_controller
        self.connect_signals()

        self.frequency = None
        
    def connect_signals(self): 
        elem =self.view.elem
        elem['FREQ_COBMO'].currentTextChanged.connect(self.selector_handler)
        elem['BTN_PROTOCOL'].clicked.connect(self.btn_protocol_click)
        elem['DET_NAME_LINE'].textChanged.connect(self.det_name_handler)

    def selector_handler(self):
        selected_freq = self.get_current_frequency()
        if selected_freq is None:
            return
        data = self.model.get_data_from_frequency(selected_freq)
        self.plot_data_from_frequency(data)

    def btn_protocol_click(self):
        selected_frequency = self.get_current_frequency()
        if selected_frequency is None:
            return
        
        path = os.path.join(self.model.output_dir, f"{self.model.settings['FILENAME']}_results.csv")
        if not os.path.exists(path):
            logger.warning(f"Protocol for {self.model.settings['FILENAME']} cannot be created")
            error_msg = f"File not found: {path}" 
            logger.error(error_msg)
            self.meas_controller.status_bar.error(error_msg)
            return
        
        try:
            det_name = self.view.elem["DET_NAME_LINE"].text()
            str_freq = self.value_to_str(selected_frequency, "MHz")
            self.meas_controller.status_bar.warning(f'Creating protocol for "{det_name}" at {str_freq} MHz')
            with open(path, "r") as file:
                logger.info(f"Loading data from: {path}")
                next(file) # skip header
                result_file = list(csv.reader(file))
            data = self.sorting_data_from_frequency(result_file, selected_frequency)
            settings = WriteSettings.view_to_dict(self.meas_controller)
            _ = MeasurementProtocol(data, settings)
            finish_msg = f'Protocol for "{det_name}" at {str_freq} MHz created successfully'
            self.meas_controller.status_bar.info(finish_msg)
        except Exception as e:
            logger.error(f"Error creating protocol: {e}")
            

    def sorting_data_from_frequency(self, data_file, selected_frequency):
        data = []
        for row in data_file:
            if is_equal_frequencies(row[0], selected_frequency):
                data.append(row)
        return data


    def plot_data_from_frequency(self, data):
        self.clear_plot()
        for point in data:
            self.view.figure1.add_point(point[1], point[3])
            self.view.figure2.add_point(point[2], point[3])

    def add_selector_point(self, frequency):
        elem =  self.view.elem['FREQ_COBMO']
        text = f'{frequency/1e6:.2f} MHz'
        elem.addItem(text)
        elem.setCurrentIndex(elem.count() - 1)

    def get_current_frequency(self):
        text = self.view.elem['FREQ_COBMO'].currentText()
        if text == '':
            return None
        return float(text.replace(' MHz','')) * 1e6

    def clear_selector(self):
        self.view.elem['FREQ_COBMO'].clear()

    def clear_plot(self):
        self.view.figure1.clear_plot()
        self.view.figure2.clear_plot()

    def set_selector(self):
        elem = self.view.elem['FREQ_COBMO']
        for i in range(elem.count()): 
            box_frequency = float(elem.itemText(i).replace(' MHz','')) * 1e6 if ' MHz' in elem.itemText(i) else None
            if  abs(self.frequency - box_frequency) < 1e4:
                elem.setCurrentIndex(i)
                return
            
    def set_det_name(self, name):
        if name is not None:
            name = name.replace('_', ' ')
            name = name.rstrip()
            self.view.elem['DET_NAME_LINE'].setText(name)

    def det_name_handler(self):
        WriteSettings.write_det_name_to_model(self.meas_controller)
            
    def lock_control_elem(self):
        elem = self.view.elem
        elem['FREQ_COBMO'].setEnabled(False)
        elem['BTN_PROTOCOL'].setEnabled(False)

    def unlock_control_elem(self):
        elem = self.view.elem
        elem['FREQ_COBMO'].setEnabled(True)
        elem['BTN_PROTOCOL'].setEnabled(True)