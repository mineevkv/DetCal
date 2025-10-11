import os
from .latex_document import LatexDocument
from .helper_functions import *
from Measurement.helper_functions import remove_zeros
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from GUI.palette import *
from PyQt6.QtCore import pyqtSignal, QThread
import numpy as np

from System.logger import get_logger

logger = get_logger(__name__)


class ProtocolCreator(QThread):
    """ Base class for creating measurement protocols in a separate thread."""

    output_dir = "Output"
    finished_signal = pyqtSignal()

    def __init__(self):
        super().__init__()
        self._should_stop = False

    def stop(self) -> None:
        """Safely stop the protocol thread."""
        self._should_stop = True
        self.requestInterruption()  # QThread built-in method
        self.quit()  # Ensure the event loop exits
        if not self.wait(3000):  # Wait up to 3 seconds
            # Force termination if graceful shutdown fails
            self.terminate()
            self.wait()


class MeasurementProtocol(ProtocolCreator):
    """ Class for creating measurement protocols in a separate thread."""

    def __init__(self, data_file: list, settings: dict) -> None:
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

    def run(self) -> None:
        """" Run the protocol in a separate thread."""
        try:
            if self.isInterruptionRequested() or self._should_stop:
                return

            self.fill_document()

            if not self.isInterruptionRequested() and not self._should_stop:
                self.finished_signal.emit()

        except Exception as e:
            logger.error(f"Error in protocol thread: {e}")

    def get_frequency(self) -> float | None:
        """Get the frequency from the measurement data in MHz."""
        try:
            frequency = float(self.meas_data[1][0]) / 1e6
            return round(frequency, 2)
        except Exception as e:
            logger.error(f"Error getting frequency: {e}")
            return None

    def make_filename(self) -> str:
        """Make a filename for the protocol."""
        filename = self.meas_settings["FILENAME"]
        filename = (
            filename + "_" + remove_zeros(self.frequency).replace(".", "p") + "MHz"
        )
        return filename

    def fill_document(self) -> None:
        """Fill the document with content."""
        self.add_sapmle_section()
        self.add_equipments_section()
        self.add_settings_section()

        if self.add_plot_section():
            self.create_pdf()
            self.clean_up()

        else:
            logger.warning(
                "Protocol cannot be created! Check the data file and settings!"
            )

    def add_sapmle_section(self) -> None:
        # Add sections with content
        self.doc.add_section("Sample", "")
        filename = self.meas_settings["FILENAME"]
        filename = filename.replace("_", " ")
        filename = filename.rstrip()
        text = r"\texttt{" + filename + r"}" + f" at {remove_zeros(self.frequency)} MHz"
        self.doc.add_bullet_list([text])

    def add_equipments_section(self) -> None:
        # Add sections with content
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

    def parse_settings(self) -> dict:
        """Parse the measurement settings."""
        settings = self.meas_settings.copy()
        del settings["FILENAME"]
        del settings["REF_MANUAL"]

        freq_start, freq_stop, points = settings["RF_FREQUENCIES"]
        freq_start = f"{(float(freq_start)/1e6):.2f}"
        freq_stop = f"{(float(freq_stop)/1e6):.2f}"
        points = int(points)
        if points > 1:
            settings["RF_FREQUENCIES"] = (
                f"{remove_zeros(freq_start)} to {remove_zeros(freq_stop)} MHz [{points}]"
            )
        else:
            settings["RF_FREQUENCIES"] = (f"{remove_zeros(freq_start)} MHz")

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

    def add_plot_section(self) -> bool:
        # Add sections with content
        self.doc.add_newpage()
        self.doc.add_section("Results", "")

        try:

            if self.meas_data:
                if self.is_detector():
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

    def create_pdf(self) -> None:
        """ Create a PDF file from the LaTeX document. """
        try:
            pdf_path = self.doc.compile_pdf(output_dir=self.output_dir)
            logger.info(f"PDF generated at: {pdf_path}")
        except RuntimeError as e:
            logger.error(f"PDF compilation failed: {e}")
            logger.debug("But the .tex file was created successfully!")

    def create_plot(self, unit: str="mW") -> None:
        """ Create a plot from the measurement data. """
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

    def is_detector(self) -> bool:
        """ Check if the measurement data has detector input level. """
        meas_data_row = self.meas_data[0]
        if (
            self.meas_settings["RECALC_ATTEN"]
            and len(meas_data_row) > 6
            and meas_data_row[6] is not None
        ):
            return True
        else:
            return False

    def extract_and_plot_data(self, unit: str="mW") -> bool:
        """Extract measurement data and plot it"""
        try:
            if len(self.meas_data) <= 1:
                logger.warning("Not enough data points")
                return False

            # Extract data
            if self.is_detector():
                level_dBm = [float(data_row[6]) for data_row in self.meas_data]
                logger.info("Using recalculated Detector level")
            else:
                level_dBm = [float(data_row[2]) for data_row in self.meas_data]
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

    def apply_plot_settings(self, unit: str="mW") -> None:
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

    def clean_up(self) -> None:
        """Clean up the output directory."""
        png_files = [
            f
            for f in os.listdir(self.output_dir)
            if f.endswith(".png") and "measurement_data_" in f
        ]
        for f in png_files:
            os.remove(os.path.join(self.output_dir, f))
