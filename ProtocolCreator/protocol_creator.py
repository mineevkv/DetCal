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
    output_dir = "Output"

    def __init__(self):
        pass


class MeasurementProtocol(ProtocolCreator):
    def __init__(self, data_file, settings):
        super().__init__()

        self.meas_data = data_file
        self.meas_settings = settings
        self.frequency = self.get_frequency()


        kwargs = dict(
            document_class="article",
            document_class_options=["12pt", "a4paper"],
            title="Protocol of RF Detector Calibration",
            author="IAP RAS",
            packages=["amsmath", "graphicx", "hyperref", "booktabs", "verbatim"],
            filename=self.make_filename(),
        )

        self.doc = LatexDocument(**kwargs)

        self.fill_document()

    def get_frequency(self):
        try: 
            frequency = float(self.meas_data[1][0]) / 1e6
            return round(frequency, 2)
        except Exception as e:
            logger.error(f"Error getting frequency: {e}")
            return None
            
    def make_filename(self):
        filename = self.meas_settings["FILENAME"]
        filename = filename + "_" + remove_zeros(self.frequency).replace(".", "P") + "MHz"
        return filename
            

    def fill_document(self):
        self.add_sapmle_section()
        self.add_equipments_section()
        self.add_settings_section()

        if self.add_plot_section():
            self.create_pdf()
            self.clean_up()
        else:
            logger.warning(
                "Protocol can't be created! Check the data file and settings!"
            )

    def add_sapmle_section(self):
        self.doc.add_section("Sample", "")
        filename = self.meas_settings["FILENAME"]
        filename = filename.replace("_", " ")
        filename = filename.rstrip()
        text = r"\texttt{" + filename + r"}" + f" at {remove_zeros(self.frequency)} MHz"
        self.doc.add_bullet_list([text])

    def add_equipments_section(self):
        self.doc.add_section("Measurement equipment", "")
        self.doc.add_numbered_list(
            [
                r"Microwave generator: \texttt{Rigol DSG830}",
                r"Spectrum analyzer: \texttt{Rigol RSA5065N}",
                r"Oscilloscope: \texttt{Tektronix MDO34}",
            ]
        )

    def add_settings_section(self):
        # Add sections with content
        self.doc.add_section(
            "Parameters", "Parameters from DetCal application settings."
        )
        table_data = self.parse_settings()
        # table_data = [[str(key),  str(value)] for key, value in self.meas_settings.items()]
        table_data = [
            [f'{key.replace("_", " ")}', str(value)]
            for key, value in table_data.items()
        ]
        self.doc.add_table(table_data, caption="Measurement parameters", label="params")

    def parse_settings(self):
        settings = self.meas_settings.copy()
        del settings["FILENAME"]

        freq_start, freq_stop, points = settings["RF_FREQUENCIES"]
        freq_start = f"{(float(freq_start)/1e6):.2f}"
        freq_stop = f"{(float(freq_stop)/1e6):.2f}"
        points = int(points)
        settings["RF_FREQUENCIES"] = (
            f"{remove_zeros(freq_start)} to {remove_zeros(freq_stop)} MHz [{points}]"
        )

        level_start, level_stop, points = settings["RF_LEVELS"]
        settings["RF_LEVELS"] = f"{level_start} to {level_stop} dBm [{points}]"

        keys = (
            "SPAN_WIDE",
            "SPAN_NARROW",
            "RBW_WIDE",
            "RBW_NARROW",
            "VBW_WIDE",
            "VBW_NARROW",
        )

        for key in keys:
            elem = settings[key]
            elem = f"{(float(elem)/1e3):.3f}"
            elem = f"{remove_zeros(elem)} kHz"
            settings[key] = elem

        settings["REF_LEVEL"] = f"{settings['REF_LEVEL']} dBm"
        settings["SWEEP_POINTS"] = f"{int(settings['SWEEP_POINTS'])}"

        elem = settings["HOR_SCALE"]
        elem = f"{(float(elem)*1e3):.3f}"
        elem = f"{remove_zeros(elem)} ms/div"
        settings["HOR_SCALE"] = elem

        return settings

    def add_plot_section(self):
        self.doc.add_newpage()
        self.doc.add_section("Results", "")

        try:
            

            if self.meas_data:
                if (
                    self.meas_settings["RECALC_ATTEN"]
                    and len(self.meas_data) > 6
                    and self.meas_data[6] is not None
                ):
                    power_input = "Detector"
                else:
                    power_input = "Spectrum Analyzer"
                caption_field = (
                    f"{power_input} response at {remove_zeros(self.frequency)} MHz"
                )
            else:
                return False

            self.create_plot("mW")
            self.doc.add_figure(
                image_path="measurement_data_mW.png",
                caption=caption_field,
                label="Figure",
                width="1.0\\textwidth",
            )

            self.create_plot("dBm")
            self.doc.add_figure(
                image_path="measurement_data_dBm.png",
                caption=caption_field,
                label="Figure",
                width="1.0\\textwidth",
            )
            return True
        except Exception as e:
            logger.error(f"Error adding plot section: {e}")

    def create_pdf(self):
        try:
            pdf_path = self.doc.compile_pdf(output_dir=self.output_dir)
            logger.info(f"PDF generated at: {pdf_path}")
        except RuntimeError as e:
            logger.error(f"PDF compilation failed: {e}")
            logger.debug("But the .tex file was created successfully!")

    def create_plot(self, unit="mW"):
        try:
            # Create fresh figure
            self.figure, self.ax = plt.subplots(
                figsize=(cm_to_inches(16), cm_to_inches(18))
            )
            self.canvas = FigureCanvas(self.figure)

            # Set background transparency
            self.figure.patch.set_alpha(0)
            self.ax.patch.set_alpha(0)

            # Extract and plot
            success = self.extract_and_plot_data(unit)

            if success:
                self.apply_plot_settings(unit)
                self.figure.tight_layout()
                self.canvas.draw()
                logger.info("Plot created successfully")
            else:
                logger.warning("Failed to create plot")

        except Exception as e:
            logger.error(f"Error creating plot: {e}")

        # Save figure as PNG
        path = os.path.join(self.output_dir, f"measurement_data_{unit}.png")
        self.figure.savefig(path, dpi=600, bbox_inches="tight", pad_inches=0)

    def extract_and_plot_data(self, unit="mW"):
        """Extract measurement data and plot it"""
        try:
            if len(self.meas_data) <= 1:
                logger.warning("Not enough data points")
                return False

            # Extract data
            if (
                self.meas_settings["RECALC_ATTEN"]
                and len(self.meas_data) > 6
                and self.meas_data[6] is not None
            ):
                level_dBm = [
                    float(meas_data[6]) for meas_data in self.meas_data
                ]  # meas_data[1] - Gen level, meas_data[6] - Det level
                logger.info("Using recalculated Detector level")
            else:
                level_dBm = [
                    float(meas_data[2]) for meas_data in self.meas_data
                ]  # meas_data[1] - Gen level, meas_data[6] - Det level
                logger.warning("Using Spectrum Analyzer level")

            voltage = [float(meas_data[3]) for meas_data in self.meas_data]

            if not level_dBm or not voltage:
                logger.warning("No valid data to plot")
                return False

            self.x = np.array(voltage)
            if unit == "mW":
                level_mW = [
                    10 ** (float(level_dBm[i]) / 10) for i in range(len(level_dBm))
                ]
                self.y = np.array(level_mW)
            if unit == "dBm":
                self.y = np.array(level_dBm)

            logger.info(
                f"Data ranges - X: {self.x.min():.4f} to {self.x.max():.4f}, "
                f"Y: {self.y.min():.2f} to {self.y.max():.2f}"
            )

            # Plot the data
            self.ax.plot(
                self.x, self.y, "-", color=BLUE, linewidth=2, marker="o", markersize=4
            )

            return True

        except Exception as e:
            logger.error(f"Error in extract_and_plot_data: {e}")
            return False

    def apply_plot_settings(self, unit="mW"):
        """Apply comprehensive plot settings"""
        # Labels and titles
        self.ax.set_xlabel(
            "Detector signal, V", fontsize=10, color=DARK, fontweight="bold"
        )
        self.ax.set_ylabel(
            f"Input power, {unit}", fontsize=10, color=DARK, fontweight="bold"
        )

        # Tick parameters
        self.ax.tick_params(axis="both", which="major", labelsize=9, colors=DARK)
        self.ax.tick_params(axis="both", which="minor", labelsize=8, colors=DARK)

        # Grid
        self.ax.grid(True, color=GRAY, alpha=0.7, linestyle="-", linewidth=0.5)
        self.ax.grid(
            True, color=GRAY, alpha=0.3, linestyle="--", linewidth=0.3, which="minor"
        )
        self.ax.minorticks_on()

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
        self.ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        self.ax.yaxis.set_major_locator(plt.MaxNLocator(16))

        # self.protocol.add_section("Measurement Data", self.meas_data)
        # self.protocol.add_section("Measurement Settings", self.meas_settings)

    def clean_up(self):
        png_files = [f for f in os.listdir(self.output_dir) if f.endswith(".png") and "measurement_data_" in f]
        for f in png_files:
            os.remove(os.path.join(self.output_dir, f))
