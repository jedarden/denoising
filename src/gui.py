"""
gui.py

Provides a cross-platform, responsive desktop GUI for real-time speech denoising.
- Built with PyQt5 (or PyQt6)
- Allows device selection, start/stop, parameter adjustment, and status display
- Integrates with AudioIO and Denoiser modules
- Handles errors and device changes gracefully

Author: aiGI Auto-Coder
"""

import logging
from typing import List, Any

try:
    from PyQt5 import QtWidgets, QtCore
except ImportError:
    QtWidgets = None
    QtCore = None

# Try to import pyqtgraph for waveform visualization
try:
    import pyqtgraph as pg
except ImportError:
    pg = None

# No longer need dummy widget classes; use QWidget-compatible placeholders instead.

    def addItem(self, item):
        self.items.append(item)

    def setLayout(self, layout):
        self.layout = layout

    def setWindowTitle(self, title):
        self.window_title = title

    def setGeometry(self, *args):
        self.geometry = args

    def clicked(self):
        return self

    def connect(self, slot):
        self.signals["clicked"] = slot

    def currentIndexChanged(self):
        return self

    def critical(self, *a, **k):
        self.critical_called = True

class _DummyMainWindow:
    """
    Mock main window for headless/test environments.
    Stores state and simulates main window behavior for testing.
    """
    def __init__(self, *a, **k):
        self.central_widget = None
        self.window_title = ""
        self.geometry = None
        self.shown = False

    def setCentralWidget(self, widget):
        self.central_widget = widget

    def setWindowTitle(self, title):
        self.window_title = title

    def setGeometry(self, *args):
        self.geometry = args

    def show(self):
        self.shown = True

# Use QtWidgets.QMainWindow if available, else dummy
_BaseMainWindow = QtWidgets.QMainWindow if QtWidgets and hasattr(QtWidgets, "QMainWindow") else _DummyMainWindow

class DenoisingApp(_BaseMainWindow):
    """
    Main application window for the speech denoising app.
    """

    def __init__(self, audio_io, denoiser):
        super().__init__()
        self.audio_io = audio_io
        self.denoiser = denoiser
        self.device_list = []
        self.virtual_mic_available = True
        # Check for virtual microphone backend availability
        if hasattr(self.audio_io, "_virtual_microphone_service"):
            if self.audio_io._virtual_microphone_service is None:
                self.virtual_mic_available = False
                logging.warning("Virtual microphone backend is not available on this platform. Feature disabled.")
        if QtWidgets and hasattr(QtWidgets, "QLabel"):
            self.device_label = QtWidgets.QLabel("Input Device:", self)
            self.device_combo = QtWidgets.QComboBox(self)
            self.refresh_button = QtWidgets.QPushButton("Refresh Devices", self)
            self.denoise_checkbox = QtWidgets.QCheckBox("Denoising On", self)
            self.denoise_checkbox.setChecked(True)
            self.start_button = QtWidgets.QPushButton("Start", self)
            self.stop_button = QtWidgets.QPushButton("Stop", self)
            self.status_label = QtWidgets.QLabel("Status: Idle", self)
            # Add waveform plot widgets using pyqtgraph if available
            if pg is not None and QtWidgets is not None:
                self.input_waveform_plot = pg.PlotWidget(title="Noisy Input")
                self.output_waveform_plot = pg.PlotWidget(title="Denoised Output")
                self.input_waveform_plot.setYRange(-1, 1)
                self.output_waveform_plot.setYRange(-1, 1)
            elif QtWidgets is not None:
                # Use QLabel as a QWidget-compatible placeholder
                self.input_waveform_plot = QtWidgets.QLabel("Plot unavailable")
                self.output_waveform_plot = QtWidgets.QLabel("Plot unavailable")
            else:
                # Headless fallback: do not create plot widgets
                self.input_waveform_plot = None
                self.output_waveform_plot = None
        else:
            if QtWidgets is not None:
                self.device_label = QtWidgets.QLabel("Device")
                self.device_combo = QtWidgets.QComboBox()
                self.refresh_button = QtWidgets.QPushButton("Refresh Devices")
                self.denoise_checkbox = QtWidgets.QCheckBox("Denoising On")
                self.denoise_checkbox.setChecked(True)
                self.start_button = QtWidgets.QPushButton("Start")
                self.stop_button = QtWidgets.QPushButton("Stop")
                self.status_label = QtWidgets.QLabel("Status: Idle")
                self.input_waveform_plot = QtWidgets.QLabel("Plot unavailable")
                self.output_waveform_plot = QtWidgets.QLabel("Plot unavailable")
            else:
                self.device_label = None
                self.device_combo = None
                self.refresh_button = None
                self.denoise_checkbox = None
                self.start_button = None
                self.stop_button = None
                self.status_label = None
                self.input_waveform_plot = None
                self.output_waveform_plot = None
        self.init_ui()
        self.init_ui()

    def init_ui(self):
        """
        Set up the GUI layout and widgets.
        """
        # Only call Qt methods if available
        if hasattr(self, "setWindowTitle"):
            self.setWindowTitle("Real-Time Speech Denoising")
        if hasattr(self, "setGeometry"):
            self.setGeometry(100, 100, 500, 250)

        if QtWidgets and hasattr(QtWidgets, "QVBoxLayout"):
            layout = QtWidgets.QVBoxLayout()
            device_layout = QtWidgets.QHBoxLayout()
            device_layout.addWidget(self.device_label)
            device_layout.addWidget(self.device_combo)
            device_layout.addWidget(self.refresh_button)
            layout.addLayout(device_layout)
            # Add denoising A/B toggle
            layout.addWidget(self.denoise_checkbox)
            layout.addWidget(self.start_button)
            layout.addWidget(self.stop_button)
            layout.addWidget(self.status_label)

            # Add waveform plots to the layout
            layout.addWidget(self.input_waveform_plot)
            layout.addWidget(self.output_waveform_plot)
            central_widget = QtWidgets.QWidget(self)
            central_widget.setLayout(layout)
            if hasattr(self, "setCentralWidget"):
                self.setCentralWidget(central_widget)

            # Signals/slots
            self.refresh_button.clicked.connect(self.refresh_devices)
            self.start_button.clicked.connect(self.start_denoising)
            self.stop_button.clicked.connect(self.stop_denoising)
            self.device_combo.currentIndexChanged.connect(self.device_selected)

            self.refresh_devices()
            self.update_status("Idle")

    def refresh_devices(self):
        """
        Refresh the list of available audio devices.
        """
        try:
            self.device_list = self.audio_io.enumerate_devices()
            if hasattr(self.device_combo, "clear"):
                self.device_combo.clear()
            for dev in self.device_list:
                label = f"{dev['id']}: {dev['name']}"
                if hasattr(self.device_combo, "addItem"):
                    self.device_combo.addItem(label, dev['id'])
        except Exception as e:
            self.show_error(f"Failed to enumerate devices: {e}")

    def device_selected(self, index: int):
        """
        Handle device selection from the dropdown.
        """
        try:
            if index < 0 or index >= len(self.device_list):
                return
            device_id = self.device_list[index]['id']
            if not self.audio_io.select_device(device_id):
                self.show_error(f"Failed to select device {device_id}")
            else:
                self.update_status(f"Selected device {device_id}")
        except Exception as e:
            self.show_error(f"Device selection error: {e}")

    def start_denoising(self):
        """
        Start audio I/O and denoising.
        """
        def callback(in_data):
            import numpy as np
            audio = np.frombuffer(in_data, dtype=np.int16).astype(np.float32) / 32768.0
            try:
                # Check toggle for A/B test
                denoise_on = (
                    self.denoise_checkbox.isChecked()
                    if hasattr(self.denoise_checkbox, "isChecked")
                    else getattr(self.denoise_checkbox, "checked", True)
                )
                bypassed = False
                if denoise_on:
                    processed, bypassed = self.denoiser.process_buffer(audio)
                else:
                    processed = audio

                # Update waveform plots (in GUI thread if possible)
                if pg is not None and QtCore is not None:
                    def update_plots():
                        self.input_waveform_plot.clear()
                        self.input_waveform_plot.plot(audio, pen='r')
                        self.output_waveform_plot.clear()
                        self.output_waveform_plot.plot(processed, pen='g')
                    QtCore.QMetaObject.invokeMethod(
                        self.input_waveform_plot, "clear", QtCore.Qt.QueuedConnection
                    )
                    QtCore.QMetaObject.invokeMethod(
                        self.input_waveform_plot, "plot", QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(object, audio), QtCore.Q_ARG(object, 'r')
                    )
                    QtCore.QMetaObject.invokeMethod(
                        self.output_waveform_plot, "clear", QtCore.Qt.QueuedConnection
                    )
                    QtCore.QMetaObject.invokeMethod(
                        self.output_waveform_plot, "plot", QtCore.Qt.QueuedConnection,
                        QtCore.Q_ARG(object, processed), QtCore.Q_ARG(object, 'g')
                    )
                else:
                    # Fallback for dummy/test: just store data
                    self.input_waveform_plot.plot(audio)
                    self.output_waveform_plot.plot(processed)

                out_data = (processed * 32768.0).clip(-32768, 32767).astype(np.int16).tobytes()
                if denoise_on and bypassed:
                    self.update_status("Denoising bypassed: input too short, raw audio used")
                return out_data
            except Exception as e:
                self.show_error(f"Audio processing error: {e}")
                # Return silence if error
                return (np.zeros_like(audio) * 32768.0).astype(np.int16).tobytes()

        try:
            if not self.audio_io.start_stream(callback):
                self.show_error("Failed to start audio stream.")
                self.update_status("Error: Stream not started")
            else:
                # Only update status if not already set to a bypass message
                if not hasattr(self.status_label, "text") or "bypassed" not in getattr(self.status_label, "text", "").lower():
                    self.update_status("Denoising started (A/B toggle: {})".format(
                        "On" if (self.denoise_checkbox.isChecked() if hasattr(self.denoise_checkbox, "isChecked") else getattr(self.denoise_checkbox, "checked", True)) else "Off"
                    ))
        except Exception as e:
            self.show_error(f"Failed to start denoising: {e}")

    def stop_denoising(self):
        """
        Stop audio I/O and denoising.
        """
        try:
            if not self.audio_io.stop_stream():
                self.show_error("Failed to stop audio stream.")
                self.update_status("Error: Stream not stopped")
            else:
                self.update_status("Denoising stopped")
        except Exception as e:
            self.show_error(f"Failed to stop denoising: {e}")

    def update_status(self, message: str):
        """
        Update status label in the GUI.
        """
        if not isinstance(message, str):
            message = str(message)
        if hasattr(self.status_label, "setText"):
            self.status_label.setText(f"Status: {message}")

    def set_device_list(self, devices: List[dict]):
        """
        Update the device selection dropdowns.
        """
        if hasattr(self.device_combo, "clear"):
            self.device_combo.clear()
        for dev in devices:
            label = f"{dev['id']}: {dev['name']}"
            if hasattr(self.device_combo, "addItem"):
                self.device_combo.addItem(label, dev['id'])

    def show_error(self, message: str):
        """
        Show an error dialog or log the error.
        """
        logging.error(message)
        if QtWidgets and hasattr(QtWidgets, "QMessageBox"):
            QtWidgets.QMessageBox.critical(self, "Error", str(message))

# End of gui.py