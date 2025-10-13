from .abstract_sheet import Sheet
from PyQt6 import QtCore
import numpy as np
import matplotlib
matplotlib.use('Qt5Agg') # Qt5Agg for PyQt6
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import QVBoxLayout, QWidget, QComboBox, QGridLayout

from GUI.palette import *

from System.logger import get_logger

logger = get_logger(__name__)


class InfographicSheet(Sheet):
    """
    Class for the infographic sheet in the main window.

    This class is used to create the infographic sheet in the main window.
    It contains a plot for the power levels vs output voltages from detector.
    """

    def __init__(self, main_layout: QGridLayout) -> None:
        super().__init__(main_layout)

        self.box.setTitle("Infographic")

        self.add_plot_sheet()

        width_combo = 120
        row_combo = 2
        row_detname = row_combo + 2
        row_btn = row_detname + 2

        self.add_frequency_selector(
            "FREQ_COMBO", self.zero_col, row_combo, width_combo, self.elem_height
        )
        self.add_line_edit(
            "DET_NAME", self.zero_col, row_detname, "rf_det_name", width_combo
        ).setProperty("class", "det_name_line")
        self.add_custom_btn(
            "PROTOCOL",
            self.zero_col,
            row_btn,
            "Generate Protocol",
            width_combo,
            45,
            "btn_protocol",
        )

    def add_frequency_selector(
        self, key: str, col: int, row: int, width: int, height: int
    ) -> QComboBox:
        """Add a combo box for frequency selection."""
        self.elem[key] = QComboBox(parent=self.box)
        self.elem[key].setGeometry(
            QtCore.QRect(self.x_col[col], self.y_row[row], width, height)
        )
        return self.elem[key]

    def add_plot_sheet(self) -> None:
        """Add a plots for the power levels vs output voltages from detector."""
        # Create a proper container for the plot
        plot_container1 = QWidget(parent=self.box)
        plot_container1.setStyleSheet("background-color: none; border: none;")
        plot_layout1 = QVBoxLayout(plot_container1)
        plot_container1.setLayout(plot_layout1)
        # Set geometry to ensure visibility
        dx = 120
        plot_container1.setGeometry(
            QtCore.QRect(self.x_col[self.zero_col] + dx, 20, 380, 200)
        )
        self.figure1 = PlotFigure(plot_layout1)

        # Create a proper container for the plot
        plot_container2 = QWidget(parent=self.box)
        plot_container2.setStyleSheet("background-color: none; border: none;")
        plot_layout2 = QVBoxLayout(plot_container2)
        plot_container2.setLayout(plot_layout2)
        # Set geometry to ensure visibility
        plot_container2.setGeometry(
            QtCore.QRect(self.x_col[self.zero_col] + 350 + dx, 20, 380, 200)
        )
        self.figure2 = PlotFigure(plot_layout2)
        self.figure2.ax.set_xlabel("SA input, dBm", fontsize=8)


class PlotFigure:
    """Class for the plot figure."""

    def __init__(self, layout) -> None:
        self.layout = layout
        self.meas_data = []

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent; border: none;")
        self.layout.addWidget(self.canvas)

        self.figure.subplots_adjust(left=0.2, right=0.95, bottom=0.25, top=0.95)
        self.ax.set_xlabel("Gen output, dBm", fontsize=8)
        self.ax.set_ylabel("Voltage, mV", fontsize=8)
        self.figure.patch.set_alpha(0)
        self.ax.patch.set_alpha(0)

        self.ax.grid(True, color=GRAY)

        self.ax.xaxis.label.set_color(YELLOW)
        self.ax.yaxis.label.set_color(YELLOW)

        self.ax.tick_params(axis="both", which="major", labelsize=8)
        self.ax.tick_params(axis="x", colors=YELLOW)
        self.ax.tick_params(axis="y", colors=YELLOW)

        # self.ax.set_xlim(-20, 15)
        self.ax.set_ylim(0, 500)

        self.ax.spines["bottom"].set_color(BLUE)
        self.ax.spines["left"].set_color(BLUE)
        self.ax.spines["top"].set_color(BLUE)
        self.ax.spines["right"].set_color(BLUE)

        self.max_points = 300
        self.x, self.y = [], []

        # Initialize with empty data
        (self.line,) = self.ax.plot([], [], "-", color=YELLOW, linewidth=2)

    def add_point(self, x: float, y: float, autoscale=False) -> None:
        """
        Add a point to the plot.

        Parameters
        ----------
        x : float
            x-coordinate of the point to add
        y : float
            y-coordinate of the point to add
        autoscale : bool, optional
            Whether to autoscale the plot after adding the point, by default False
        """
        self.x = np.append(self.x, x)
        self.y = np.append(self.y, y)
        self.line.set_data(self.x, self.y)
        # self.ax.set_xlim(-20, 15)
        self.ax.set_ylim(0, max(self.y) * 1.2)
        if autoscale:
            self.ax.relim()
            self.ax.autoscale_view()
        self.canvas.draw_idle()

    def plot_line(self, x, y, autoscale=False) -> None:
        """Plot a line on the plot."""
        self.x = np.asarray(x)
        self.y = np.asarray(y)
        self.line.set_data(self.x, self.y)
        # self.ax.set_xlim(-20, 15)
        self.ax.set_ylim(0, max(self.y) * 1.2)
        if autoscale:
            self.ax.relim()
            self.ax.autoscale_view()
        self.canvas.draw_idle()

    def clear_plot(self) -> None:
        """Clear the plot."""
        self.x = []
        self.y = []
        self.line.set_data(self.x, self.y)
        self.canvas.draw_idle()
