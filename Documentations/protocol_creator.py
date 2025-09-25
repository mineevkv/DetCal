import os
from .latex_document import LatexDocument
from .helper_functions import *
from Measurement.helper_functions import remove_zeros
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from GUI.palette import *
import numpy as np

from System.logger import get_logger
logger = get_logger(__name__)



class ProtocolCreator:
    def __init__(self):
        pass


class MeasurementProtocol(ProtocolCreator):
    def __init__(self, data_file, settings):
        super().__init__()

        self.meas_data = data_file
        self.meas_settings = settings

        kwargs = dict(document_class="article",
                    document_class_options=["12pt", "a4paper"],
                    title="Protocol of RF Detector Calibration",
                    author="IAP RAS",
                    packages=["amsmath", "graphicx", "hyperref", "booktabs", "verbatim"]
                    )
        
        self.doc = LatexDocument(**kwargs)

        self.fill_document()

    def fill_document(self):
    
        self.add_equipments_section()
        self.add_settings_section()
        
        self.add_plot_section()

        self.create_pdf()
        



    def add_equipments_section(self):
        self.doc.add_section("Measurement equipment", "")
        self.doc.add_numbered_list([r"Microwave generator: \texttt{Rigol DSG830}",
                                    r"Spectrum analyzer: \texttt{Rigol RSA5065N}",
                                    r"Oscilloscope: \texttt{Tektronix MDO34}"])

    def add_settings_section(self):
        # Add sections with content
        self.doc.add_section("Parameters", 
                   "Parameters from DetCal application settings file.")
        table_data = self.parse_settings()
        # table_data = [[str(key),  str(value)] for key, value in self.meas_settings.items()]
        table_data = [[f'{key.replace("_", " ")}', str(value)] for key, value in self.meas_settings.items()]
        self.doc.add_table(table_data, caption="Measurement parameters", label="params")


    def parse_settings(self):
        settings = self.meas_settings

        freq_start, freq_stop, points = settings['RF_frequencies']
        freq_start = f"{(float(freq_start)/1e6):.2f}"
        freq_stop = f"{(float(freq_stop)/1e6):.2f}"
        points = int(points)
        settings['RF_frequencies'] = f'{remove_zeros(freq_start)} to {remove_zeros(freq_stop)} MHz [{points}]'

        level_start, level_stop, points = settings['RF_levels']
        settings['RF_levels'] = f'{level_start} to {level_stop} dBm [{points}]'

        keys = (
            "SPAN_wide",
            "SPAN_narrow",
            "RBW_wide",
            "RBW_narrow",
            "VBW_wide",
            "VBW_narrow",
        )

        for key in keys:
            elem = settings[key]
            elem = f"{(float(elem)/1e3):.3f}"
            elem = f"{remove_zeros(elem)} kHz"
            settings[key] = elem

        settings['REF_level']= f"{settings['REF_level']} dBm"
        settings['SWEEP_points'] = f"{int(settings['SWEEP_points'])}"

        elem = settings['HOR_scale']
        elem = f"{(float(elem)*1e3):.3f}"
        elem = f"{remove_zeros(elem)} ms/div"
        settings['HOR_scale'] = elem


        return settings
    
    def add_plot_section(self):
        self.doc.add_newpage()
        self.doc.add_section("Results", "")
        self.create_plot()

        frequency = float(self.meas_data[1][0])/1e6
        frequency = f"{frequency:.2f}"
        self.doc.add_figure(image_path = "measurement_data.png",
                            caption=f"Detector response at {remove_zeros(frequency)} MHz",
                            label = "Figure", 
                            width="1.0\\textwidth")

    def create_pdf(self):
        try:
            pdf_path = self.doc.compile_pdf(output_dir = os.getcwd())
            logger.info(f"PDF generated at: {pdf_path}")
        except RuntimeError as e:
            logger.error(f"PDF compilation failed: {e}")
            logger.debug("But the .tex file was created successfully!")

    def create_plot(self):
        try:
            # Create fresh figure
            self.figure, self.ax = plt.subplots(figsize=(cm_to_inches(16), cm_to_inches(12)))
            self.canvas = FigureCanvas(self.figure)
            
            # Set background transparency
            self.figure.patch.set_alpha(0)
            self.ax.patch.set_alpha(0)
            
            # Extract and plot
            success = self.extract_and_plot_data()
            
            if success:
                self.apply_plot_settings()
                self.figure.tight_layout()
                self.canvas.draw()
                print("Plot created successfully")
            else:
                print("Failed to create plot")
                
        except Exception as e:
            print(f"Error creating plot: {e}")
        
        # Save figure as PNG
        self.figure.savefig('measurement_data.png', dpi=600, bbox_inches='tight', pad_inches=0)

    def extract_and_plot_data(self):
        """Extract measurement data and plot it"""
        try:
            if len(self.meas_data) <= 1:
                print("Not enough data points")
                return False
                
            # Extract data
            level = [float(meas_data[2]) for meas_data in self.meas_data[1:]] #TODO: [6]
            voltage = [float(meas_data[3]) for meas_data in self.meas_data[1:]]
            
            if not level or not voltage:
                print("No valid data to plot")
                return False
            
            self.x = np.array(level)
            self.y = np.array(voltage)
            
            print(f"Data ranges - X: {self.x.min():.2f} to {self.x.max():.2f}, "
                f"Y: {self.y.min():.4f} to {self.y.max():.4f}")
            
            # Plot the data
            self.ax.plot(self.x, self.y, '-', color=BLUE, linewidth=2,
                         marker='o', markersize=4)
            
            return True
            
        except Exception as e:
            print(f"Error in extract_and_plot_data: {e}")
            return False

    def apply_plot_settings(self):
        """Apply comprehensive plot settings"""
        # Labels and titles
        self.ax.set_xlabel('Input power, dBm', fontsize=10, color=DARK, fontweight='bold')
        self.ax.set_ylabel('Detector signal, V', fontsize=10, color=DARK, fontweight='bold')
        
        # Tick parameters
        self.ax.tick_params(axis='both', which='major', labelsize=9, colors=DARK)
        self.ax.tick_params(axis='both', which='minor', labelsize=8, colors=DARK)
        
        # Grid
        self.ax.grid(True, color=GRAY, alpha=0.7, linestyle='-', linewidth=0.5)
        
        # Spine colors
        for spine in self.ax.spines.values():
            spine.set_color(DARK)
            spine.set_linewidth(1.5)
        
        # Auto-scale with padding
        padding_x = (self.x.max() - self.x.min()) * 0.1
        padding_y = (self.y.max() - self.y.min()) * 0.1
        
        self.ax.set_xlim(self.x.min() - padding_x, self.x.max() + padding_x)
        self.ax.set_ylim(self.y.min() - padding_y, self.y.max() + padding_y)
        
        # Formatting
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(8))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(8))

        # self.protocol.add_section("Measurement Data", self.meas_data)
        # self.protocol.add_section("Measurement Settings", self.meas_settings)



