# DetCal (Detectors Calibration)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![PyQt](https://img.shields.io/badge/PyQt6-GUI-green)](https://www.riverbankcomputing.com/software/pyqt/)
[![VISA](https://img.shields.io/badge/VISA-Instrument%20Control-orange)](https://pyvisa.readthedocs.io/)

A Python application for automating detector calibration measurements using various test instruments. DetCal provides an intuitive interface to define measurement procedures, generate calibration tables, and create comprehensive PDF reports.

## Table of Contents

- [Features](#features)
- [Requirements](#installation)
- [Supported Instruments](#supported-instruments)
- [Usage](#usage)

## Features

- **Automated Calibration**: Streamline detector calibration across multiple frequencies and power levels
- **Real-time Monitoring**: Display measurement results as they are acquired
- **VISA Instrument Control**: Communicate with test equipment via SCPI commands
- **Calibration Reporting**: Generate professional PDF reports with calibration graphs and settings
- **Attenuation Compensation**: Automatically account for signal losses in transmission lines from external S21 files
- **Data Export**: Save measurement results in csv formats
- **Intuitive GUI**: User-friendly interface built with PyQt6

## Requirements

### Software
- **Python 3.8 or higher**
- **VISA driver**: NI-VISA (National Instruments VISA)
- **Operating System**: Windows 10/11. (Linux, or macOS didn't tested)

### Hardware
- Supported test instruments (see below)
- Ethernet connections for instrument control (USB or GPIB support can be implemented upon request)
- Device Under Test (DUT) - RF detector to be calibrated

## Supported Instruments
- Microwave generator: Rigol SR830
- Spectrum Analyzer: Rigol RSA5065N
- Digital Oscilloscope: Tektronix MDO34

## Usage
Turn on the instruments and start the application.
Connect to the instruments (Application tries to connect automatically from the start. If no connection - check IP address and recconect).
Set frequency range and step size.
Configure power levels for calibration.
Load S21 file for attenuation compensation (if needed).
Run Calibration: Start the automated measurement sequence.
Review Results: Analyze calibration data and graphs in real-time.
Export Data: Save calibration tables as CSV and generate PDF reports.
