import configparser
import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Any

class RSA506N_S21_Parser:
    def __init__(self, filename: str):
        self.filename = filename
        self.config = configparser.ConfigParser()
        self.frequency = None
        self.s21_complex = None
        self.magnitude_db = None
        self.phase_degrees = None
        
    def parse_file(self) -> Dict[str, Any]:
        """Parse the RSA506N VNA trace file"""
        # Read the file
        with open(self.filename, 'r') as file:
            content = file.read()
        
        # Parse the INI-like format
        self.config.read_string(content)
        
        # Extract measurement parameters
        params = self._extract_parameters()
        
        # Extract trace data
        self._extract_trace_data()
        
        return {
            'parameters': params,
            'frequency': self.frequency,
            's21_complex': self.s21_complex,
            'magnitude_db': self.magnitude_db,
            'phase_degrees': self.phase_degrees
        }
    
    def _extract_parameters(self) -> Dict[str, Any]:
        """Extract measurement parameters from the file"""
        params = {}
        
        # General parameters
        if 'General' in self.config:
            general = self.config['General']
            params['measurement_mode'] = general.get('MeasMode', 'S21')
            params['points'] = int(general.get('PointsNums', '1001'))
            params['trace_format'] = general.get('TraceFormat', 'LogMag')
        
        # VNA parameters
        if 'VNA' in self.config:
            vna = self.config['VNA']
            params['start_freq'] = float(vna.get('m_f64StartFreq', '100000'))  # 100 kHz
            params['stop_freq'] = float(vna.get('m_f64StopFreq', '6500000000'))  # 6.5 GHz
            params['center_freq'] = float(vna.get('m_f64CentFreq', '3250050000'))  # 3.25 GHz
            params['span'] = float(vna.get('m_f64Span', '6499900000'))  # 6.5 GHz
            params['sweep_points'] = int(vna.get('m_s32SweepPoints', '1001'))
        
        return params
    
    def _extract_trace_data(self):
        """Extract S21 trace data from the file"""
        if 'Trace' not in self.config:
            raise ValueError("No trace data found in file")
        
        trace_section = self.config['Trace']
        size = int(trace_section.get('size', '1001'))
        
        # Extract real and imaginary parts
        real_parts = []
        imag_parts = []
        
        for i in range(1, size + 1):
            ampy_key = f"{i}\\ampy"
            ampz_key = f"{i}\\ampz"
            
            if ampy_key in trace_section and ampz_key in trace_section:
                real_parts.append(float(trace_section[ampy_key]))
                imag_parts.append(float(trace_section[ampz_key]))
        
        # Convert to numpy arrays
        real_parts = np.array(real_parts)
        imag_parts = np.array(imag_parts)
        
        # Create complex S21 data
        self.s21_complex = real_parts + 1j * imag_parts
        
        # Calculate magnitude in dB and phase in degrees
        self.magnitude_db = 20 * np.log10(np.abs(self.s21_complex))
        self.phase_degrees = np.angle(self.s21_complex, deg=True)
        
        # Create frequency array
        params = self._extract_parameters()
        self.frequency = np.linspace(params['start_freq'], params['stop_freq'], size)
    
    def plot_results(self, save_path: str = None):
        """Plot the S21 measurement results"""
        if self.frequency is None:
            self.parse_file()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Magnitude in dB
        ax1.plot(self.frequency / 1e9, self.magnitude_db)
        ax1.set_xlabel('Frequency (GHz)')
        ax1.set_ylabel('S21 (dB)')
        ax1.set_title('S21 Magnitude Response')
        ax1.grid(True)
        
        # Plot 2: Phase in degrees
        ax2.plot(self.frequency / 1e9, self.phase_degrees)
        ax2.set_xlabel('Frequency (GHz)')
        ax2.set_ylabel('Phase (degrees)')
        ax2.set_title('S21 Phase Response')
        ax2.grid(True)
        
        # Plot 3: Real part
        ax3.plot(self.frequency / 1e9, np.real(self.s21_complex))
        ax3.set_xlabel('Frequency (GHz)')
        ax3.set_ylabel('Real Part')
        ax3.set_title('S21 Real Component')
        ax3.grid(True)
        
        # Plot 4: Imaginary part
        ax4.plot(self.frequency / 1e9, np.imag(self.s21_complex))
        ax4.set_xlabel('Frequency (GHz)')
        ax4.set_ylabel('Imaginary Part')
        ax4.set_title('S21 Imaginary Component')
        ax4.grid(True)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        plt.show()
    
    def analyze_measurement(self):
        """Perform basic analysis of the S21 measurement"""
        if self.frequency is None:
            self.parse_file()
        
        print("=== RSA506N S21 Measurement Analysis ===")
        print(f"Frequency range: {self.frequency[0]/1e6:.2f} MHz - {self.frequency[-1]/1e9:.2f} GHz")
        print(f"Number of points: {len(self.frequency)}")
        print(f"Frequency step: {(self.frequency[1] - self.frequency[0])/1e6:.2f} MHz")
        
        # Magnitude analysis
        max_gain = np.max(self.magnitude_db)
        min_gain = np.min(self.magnitude_db)
        avg_gain = np.mean(self.magnitude_db)
        
        print(f"\n--- Magnitude Analysis ---")
        print(f"Maximum gain: {max_gain:.2f} dB")
        print(f"Minimum gain: {min_gain:.2f} dB")
        print(f"Average gain: {avg_gain:.2f} dB")
        
        # Find -3dB bandwidth
        max_gain_idx = np.argmax(self.magnitude_db)
        max_gain_freq = self.frequency[max_gain_idx]
        cutoff_level = max_gain - 3
        
        above_cutoff = self.magnitude_db > cutoff_level
        indices = np.where(above_cutoff)[0]
        
        if len(indices) > 0:
            f_low = self.frequency[indices[0]]
            f_high = self.frequency[indices[-1]]
            bandwidth = f_high - f_low
            
            print(f"\n--- Bandwidth Analysis ---")
            print(f"Peak gain frequency: {max_gain_freq/1e9:.3f} GHz")
            print(f"Peak gain: {max_gain:.2f} dB")
            print(f"3-dB bandwidth: {bandwidth/1e6:.2f} MHz")
            print(f"Lower 3-dB point: {f_low/1e9:.3f} GHz")
            print(f"Upper 3-dB point: {f_high/1e9:.3f} GHz")
        
        return {
            'max_gain': max_gain,
            'min_gain': min_gain,
            'avg_gain': avg_gain,
            'bandwidth_3db': bandwidth if len(indices) > 0 else None,
            'center_frequency': max_gain_freq
        }
    
    def save_to_touchstone(self, filename: str):
        """Save data to Touchstone format (.s2p)"""
        if self.frequency is None:
            self.parse_file()
        
        with open(filename, 'w') as f:
            # Write header
            f.write("! RSA506N VNA S21 Measurement\n")
            f.write("! Converted from gen_det.txt\n")
            f.write("# Hz S DB R 50\n")
            
            # Write data points
            for i, freq in enumerate(self.frequency):
                s21 = self.s21_complex[i]
                f.write(f"{freq:.0f} {np.real(s21):.6e} {np.imag(s21):.6e}\n")