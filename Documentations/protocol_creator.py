import os
from .latex_document import LatexDocument
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from GUI.palette import *

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
                    title="Measurement protocol",
                    author="IAP RAS",
                    packages=["amsmath", "graphicx", "hyperref", "booktabs", "verbatim"]
                    )
        
        self.doc = LatexDocument(**kwargs)

        self.fill_document()

    def fill_document(self):

        # Add abstract
        abstract_text = "This is the debug template for measurements reports of detector calibration process."
        self.doc.add_abstract(abstract_text)
    
        self.add_settings_section()
        self.create_pdf()
        self.create_plot()


    def add_settings_section(self):
        # Add sections with content
        self.doc.add_section("Parameters", 
                   "This is the parameters section.")
        
        table_data = [[f'{key.replace("_", " ")}', str(value)] for key, value in self.meas_settings.items()]
        self.doc.add_table(table_data, caption="Parameters", label="params")

    def create_pdf(self):
        try:
            pdf_path = self.doc.compile_pdf(output_dir = os.getcwd())
            logger.info(f"PDF generated at: {pdf_path}")
        except RuntimeError as e:
            logger.error(f"PDF compilation failed: {e}")
            logger.debug("But the .tex file was created successfully!")

    def create_plot(self):
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: transparent; border: none;")
        
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

        # self.ax.set_xlim(-20, 15)
        # self.ax.set_ylim(0, 500)


        self.ax.spines['bottom'].set_color(BLUE)
        self.ax.spines['left'].set_color(BLUE)
        self.ax.spines['top'].set_color(BLUE)
        self.ax.spines['right'].set_color(BLUE)
        
 
        self.x, self.y = self.meas_data[2], self.meas_data[3]
        # self.x = np.linspace(0, 10, self.max_points)
        # self.y = np.zeros(self.max_points)
        
  
        print(self.meas_data)
        # Initialize with empty data
        self.ax.plot(self.x, self.y, '-', color=YELLOW, linewidth=2)

        plt.savefig("measurement_data.png", dpi=300)



        # self.protocol.add_section("Measurement Data", self.meas_data)
        # self.protocol.add_section("Measurement Settings", self.meas_settings)



