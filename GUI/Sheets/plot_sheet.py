from .abstract_sheet import Sheet
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (
    QWidget, QPushButton, QApplication, 
    QGridLayout, QLabel, QLineEdit, QGroupBox)
from PyQt6.QtGui import QPen
from PyQt6.QtCore import QMutex

from GUI.palette import *
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.animation import FuncAnimation
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtWidgets import  QGroupBox

from GUI.palette import *
from GUI.QtCustomWidgets.custom_widgets import *

from System.logger import get_logger
logger = get_logger(__name__)

class PlotSheet(Sheet):

    def __init__(self, main_layout):
        super().__init__(main_layout)
        
        self.add_plot_sheet()

    
    def add_plot_sheet(self):
        self.box = QGroupBox("Infographic")

        self.layout.addWidget(self.box, 2, 1)
        
        # Create a proper container for the plot
        plot_container = QWidget(parent=self.box)
        plot_container.setStyleSheet("background-color: none; border: none;")
        plot_layout = QVBoxLayout(plot_container)
        plot_container.setLayout(plot_layout)

        # Set geometry to ensure visibility
        plot_container.setGeometry(QtCore.QRect(10, 20, 380, 200))
        self.figure = Infographic(plot_layout)


       

    def start_plot(self):
        self.figure.start_plot()
        
    def stop_plot(self):
        self.figure.stop_plot()

    def debug_plot_visibility(self):
        """Debug method to check if plot is properly positioned"""
        logger.info(f"Plot box geometry: {self.box.geometry()}")
        logger.info(f"Plot box is visible: {self.box.isVisible()}")
        if hasattr(self, 'figure') and hasattr(self.figure, 'canvas'):
            logger.info(f"Canvas is visible: {self.figure.canvas.isVisible()}")



# Qt5Agg for PyQt6
matplotlib.use('Qt5Agg')  # TODO: check without this

class Infographic():
    def __init__(self, layout):
        self.layout = layout
        self.mutex = QMutex()  # Add a mutex for thread safety
        self.meas_data = []
   
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent; border: none;")
        self.layout.addWidget(self.canvas)
        
        self.figure.subplots_adjust(left=0.2, right=0.95, bottom=0.25, top=0.95)
        self.ax.set_xlabel('Gen output, dBm', fontsize=8)
        self.ax.set_ylabel('Voltage, mV', fontsize=8)
        self.figure.patch.set_alpha(0)
        self.ax.patch.set_alpha(0)

        self.ax.grid(True, color=GRAY)

        self.ax.xaxis.label.set_color(YELLOW)
        self.ax.yaxis.label.set_color(YELLOW)

        self.ax.tick_params(axis='both', which='major', labelsize=8)
        self.ax.tick_params(axis='x', colors=YELLOW)
        self.ax.tick_params(axis='y', colors=YELLOW)


        self.ax.spines['bottom'].set_color(BLUE)
        self.ax.spines['left'].set_color(BLUE)
        self.ax.spines['top'].set_color(BLUE)
        self.ax.spines['right'].set_color(BLUE)
        

        self.max_points = 300  
        self.x = np.linspace(0, 10, self.max_points)
        self.y = np.zeros(self.max_points)
        
  
        # Initialize with empty data
        self.line, = self.ax.plot([], [], '-', color=YELLOW, linewidth=2)
        
        # self.current_index = 0

    def add_point(self, x, y):
        self.ax.plot(x, y, 'o', color=YELLOW)

    def update_plot_data(self, meas_data):
        """Update the meas_data from external source"""
        self.mutex.lock()
        try:
            self.meas_data = meas_data
        finally:
            self.mutex.unlock()

    def update_plot(self):
        logger.debug("Infographics:update_plot")
        self.mutex.lock()
        try:
            if len(self.meas_data) > 0:
                # Group data by frequency
                freq_data = {}
                for point in self.meas_data:
                    freq = point[0]
                    if freq not in freq_data:
                        freq_data[freq] = []
                    freq_data[freq].append((point[1], point[2]))
                
                # Plot each frequency
                for freq, data in freq_data.items():
                    x, y = zip(*data)
                    
                    # Add a new line for each frequency
                    line, = self.ax.plot(x, y, label=f'{freq/1e6:.0f} MHz')
                    line.set_color(YELLOW)
                    line.set_linewidth(0.5)
                
                # Adjust view if needed
                x_min, x_max = min(self.meas_data, key=lambda x: x[1])[1], max(self.meas_data, key=lambda x: x[1])[1]
                y_min, y_max = min(self.meas_data, key=lambda x: x[2])[2], max(self.meas_data, key=lambda x: x[2])[2]
                x_padding = (x_max - x_min) * 0.1 if x_max != x_min else 1
                y_padding = (y_max - y_min) * 0.1 if y_max != y_min else 1
                
                self.ax.set_xlim(x_min - x_padding, x_max + x_padding)
                self.ax.set_ylim(y_min - y_padding, y_max + y_padding)
                # self.ax.set_xlim(-60, 0)
                # self.ax.set_ylim(-60, 0)
                
                # Add legend
                # self.ax.legend()
                
                # Redraw the canvas
                self.canvas.draw_idle()
            else:
                # Clear plot when no data
                for line in self.ax.lines:
                    line.remove()
                self.ax.set_xlim(-60, 0)
                self.ax.set_ylim(-60, 0)
                self.canvas.draw_idle()
                
        finally:
            self.mutex.unlock()    


