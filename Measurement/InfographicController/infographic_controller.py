from PyQt6.QtCore import QObject
import csv
import json
from ProtocolCreator.protocol_creator import MeasurementProtocol
import os
from Measurement.abstract_controller import Controller

from Measurement.MeasurementController.write_settings import WriteSettings
from Measurement.helper_functions import is_equal


from System.logger import get_logger

logger = get_logger(__name__)


class InfographicController(Controller):

    def __init__(self, meas_controller, view):
        super().__init__()
        self.view = view.ig
        self.model = meas_controller.model
        self.meas_controller = meas_controller
        self.connect_signals()

        self.frequency = None

    def connect_signals(self):
        elem = self.view.elem
        elem["FREQ_COMBO"].currentTextChanged.connect(self.selector_handler)
        elem["BTN_PROTOCOL"].clicked.connect(self.btn_protocol_click)
        elem["DET_NAME_LINE"].textChanged.connect(self.det_name_handler)

    def selector_handler(self):
        selected_freq = self.get_current_frequency()
        if selected_freq is None:
            return
        data = self.model.get_data_from_frequency(selected_freq)
        self.plot_data_from_frequency(data)

    def btn_protocol_click(self):
        btn = self.view.elem["BTN_PROTOCOL"]
        selected_frequency = self.get_current_frequency()
        if selected_frequency is None:
            return

        btn.setEnabled(False)
        if not self.create_protocol(selected_frequency):
            btn.setEnabled(True)

    def create_protocol(self, selected_frequency) -> bool:
        path = os.path.join(
            self.model.output_dir, f"{self.model.settings['FILENAME']}_results.csv"
        )
        if not os.path.exists(path):
            logger.warning(
                f"Protocol for {self.model.settings['FILENAME']} cannot be created"
            )
            self.meas_controller.status_bar.error(f"File not found: {path}")
            return False

        try:
            det_name = self.view.elem["DET_NAME_LINE"].text()
            str_freq = self.value_to_str(selected_frequency, "MHz")
            self.meas_controller.status_bar.warning(
                f'Creating protocol for "{det_name}" at {str_freq} MHz'
            )

            result_file = self.read_csv(path)
            data = self.sorting_data_from_frequency(result_file, selected_frequency)
            if not data:
                self.meas_controller.status_bar.error(
                    f'Data for "{det_name}" at {str_freq} MHz was not found'
                )
                return False

            self.start_creating_protocol(data, det_name, str_freq)
            return True
        except Exception as e:
            logger.error(f"Error creating protocol: {e}")

    def start_creating_protocol(self, data, det_name, str_freq):
        settings = WriteSettings.view_to_dict(self.meas_controller)
        self.protocol = MeasurementProtocol(data, settings)
        self.protocol.finished_signal.connect(
            lambda: self.protocol_finish_handler(det_name, str_freq)
        )
        self.protocol.start()

    def read_csv(self, path):
        with open(path, "r") as file:
            logger.info(f"Loading data from: {path}")
            next(file)  # skip header
            return list(csv.reader(file))

    def protocol_finish_handler(self, det_name, str_freq):
        finish_msg = f'Protocol for "{det_name}" at {str_freq} MHz created successfully'
        self.meas_controller.status_bar.info(finish_msg)
        self.view.elem["BTN_PROTOCOL"].setEnabled(True)

    def sorting_data_from_frequency(self, data_file, selected_frequency):
        data = []
        for row in data_file:
            if is_equal(row[0], selected_frequency, 1e4):
                data.append(row)
        return data

    def plot_data_from_frequency(self, data):
        self.clear_plot()
        for point in data:
            self.view.figure1.add_point(point[1], point[3])
            self.view.figure2.add_point(point[2], point[3])

    def add_selector_point(self, frequency):
        elem = self.view.elem["FREQ_COMBO"]
        text = f"{frequency/1e6:.2f} MHz"
        elem.addItem(text)
        elem.setCurrentIndex(elem.count() - 1)

    def get_current_frequency(self):
        text = self.view.elem["FREQ_COMBO"].currentText()
        if text == "":
            return None
        return float(text.replace(" MHz", "")) * 1e6

    def clear_selector(self):
        self.view.elem["FREQ_COMBO"].clear()

    def clear_plot(self):
        self.view.figure1.clear_plot()
        self.view.figure2.clear_plot()

    def set_selector(self):
        elem = self.view.elem["FREQ_COMBO"]
        for i in range(elem.count()):
            box_frequency = (
                float(elem.itemText(i).replace(" MHz", "")) * 1e6
                if " MHz" in elem.itemText(i)
                else None
            )
            if abs(self.frequency - box_frequency) < 1e4:
                elem.setCurrentIndex(i)
                return

    def set_det_name(self, name):
        if name is not None:
            name = name.replace("_", " ")
            name = name.rstrip()
            self.view.elem["DET_NAME_LINE"].setText(name)

    def det_name_handler(self):
        WriteSettings.write_det_name_to_model(self.meas_controller)

    def lock_control_elements(self):
        elem = self.view.elem
        elem["FREQ_COMBO"].setEnabled(False)
        elem["BTN_PROTOCOL"].setEnabled(False)

    def unlock_control_elements(self):
        elem = self.view.elem
        elem["FREQ_COMBO"].setEnabled(True)
        elem["BTN_PROTOCOL"].setEnabled(True)
