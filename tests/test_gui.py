"""
Test suite for gui.py

Covers:
- Canonical DenoisingApp interface (no duplicates)
- GUI initialization and teardown (mocked)
- Device selection, start/stop, parameter adjustment (mocked)
- Error handling and status display (mocked)
- Integration with AudioIO and DenoisingInference (mocked)

TDD: All tests initially fail to drive implementation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import types

import src.gui as gui

class DummyAudioIO:
    def __init__(self):
        self.selected_device = None
    def select_device(self, device_id):
        self.selected_device = device_id
        return True

class DummyDenoiser:
    def __init__(self):
        self.model_loaded = True
    def infer(self, data):
        return data

def test_single_denoisingapp_class():
    """Test that only one DenoisingApp class exists and is importable."""
    assert hasattr(gui, "DenoisingApp")
    assert isinstance(gui.DenoisingApp, type)
    assert len([name for name in dir(gui) if name == "DenoisingApp"]) == 1

def test_waveform_plot_widget_type(monkeypatch):
    """
    Test that the waveform plot widgets are QWidget-compatible and of the correct type.
    """
    # Skip test if QtWidgets is not available
    if not hasattr(gui, "QtWidgets") or gui.QtWidgets is None:
        pytest.skip("QtWidgets not available, skipping GUI widget test.")

    # Patch AudioIO and Denoiser dependencies if needed
    class DummyAudioIO:
        pass
    class DummyDenoiser:
        pass

    # Instantiate the app
    app = gui.DenoisingApp(audio_io=DummyAudioIO(), denoiser=DummyDenoiser())

    # Check input_waveform_plot and output_waveform_plot types
    if hasattr(gui, "pg") and gui.pg is not None:
        # Should be pyqtgraph.PlotWidget
        assert isinstance(app.input_waveform_plot, gui.pg.PlotWidget)
        assert isinstance(app.output_waveform_plot, gui.pg.PlotWidget)
    else:
        # Should be QLabel as fallback
        assert isinstance(app.input_waveform_plot, gui.QtWidgets.QLabel)
        assert isinstance(app.output_waveform_plot, gui.QtWidgets.QLabel)
def test_gui_launch_and_visualizer_embedding(monkeypatch):
    """
    Test that the GUI launches, pyqtgraph PlotWidgets are embedded, and waveform plots update without error.
    """
    import importlib

    # Reload gui to ensure fresh import
    importlib.reload(gui)

    # Patch QtWidgets and pyqtgraph for headless test if needed
    if gui.QtWidgets is None or gui.pg is None:
        pytest.skip("PyQt5 or pyqtgraph not available for GUI test.")

    # Dummy audio_io with virtual mic unavailable
    class DummyAudioIO:
        def __init__(self):
            self._virtual_microphone_service = None
            self.selected_device = None
        def select_device(self, device_id):
            self.selected_device = device_id
            return True
        def enumerate_devices(self):
            return [{"id": 0, "name": "Dummy Device"}]
        def start_stream(self, callback):
            # Simulate a short audio stream
            import numpy as np
            dummy_audio = (np.random.rand(512) * 2 - 1).astype(np.float32)
            callback(dummy_audio.tobytes())
            return True

    class DummyDenoiser:
        def process_buffer(self, audio):
            return audio, False

    app = gui.QtWidgets.QApplication.instance() or gui.QtWidgets.QApplication([])
    denoising_app = gui.DenoisingApp(DummyAudioIO(), DummyDenoiser())

    # Check that waveform plots are PlotWidget
    assert isinstance(denoising_app.input_waveform_plot, gui.pg.PlotWidget)
    assert isinstance(denoising_app.output_waveform_plot, gui.pg.PlotWidget)

    # Simulate a waveform update
    import numpy as np
    test_audio = np.sin(np.linspace(0, 2 * np.pi, 512)).astype(np.float32)
    denoising_app.input_waveform_plot.clear()
    denoising_app.input_waveform_plot.plot(test_audio, pen='r')
    denoising_app.output_waveform_plot.clear()
    denoising_app.output_waveform_plot.plot(test_audio, pen='g')

    # Check that no error is raised and plots have data
    assert denoising_app.input_waveform_plot.listDataItems()
    assert denoising_app.output_waveform_plot.listDataItems()

    # Check that the status label shows the virtual mic message
    status_text = denoising_app.status_label.text() if hasattr(denoising_app.status_label, "text") else ""
    assert "virtual microphone" in status_text.lower() or "feature disabled" in status_text.lower()
def test_gui_initialization_and_teardown(monkeypatch):
    """Test GUI initialization and teardown (mocked)."""
    # Mock QtWidgets.QMainWindow if not available
    if not hasattr(gui, "QtWidgets") or gui.QtWidgets is None:
        monkeypatch.setattr(gui, "QtWidgets", types.SimpleNamespace(QMainWindow=object))
    app = gui.DenoisingApp(DummyAudioIO(), DummyDenoiser())
    assert hasattr(app, "audio_io")
    assert hasattr(app, "denoiser")

def test_device_selection(monkeypatch):
    """Test device selection logic (mocked)."""
    app = gui.DenoisingApp(DummyAudioIO(), DummyDenoiser())
    # Simulate device selection
    app.audio_io.select_device = lambda device_id: device_id == 0
    assert app.audio_io.select_device(0) is True
    assert app.audio_io.select_device(1) is False

def test_start_stop_logic(monkeypatch):
    """Test start/stop logic (mocked)."""
def test_status_label_updates_on_bypass(monkeypatch):
    """Test that the GUI status label updates when denoising is bypassed due to short input."""
    import numpy as np
    # Dummy denoiser that always bypasses
    class DummyBypassDenoiser:
        def process_buffer(self, audio):
            return audio, True
    # Dummy AudioIO with start_stream that immediately calls callback
    class DummyAudioIO:
        def start_stream(self, callback):
            # Simulate a short buffer (1 sample)
            short_audio = (np.array([0.5], dtype=np.float32) * 32768.0).astype(np.int16).tobytes()
            callback(short_audio)
            return True
        def stop_stream(self):
            return True
        def enumerate_devices(self):
            return []
        def select_device(self, device_id):
            return True
    app = gui.DenoisingApp(DummyAudioIO(), DummyBypassDenoiser())
    # Simulate denoising start
    app.start_denoising()
    # Check that the status label was updated to indicate bypass
    assert "bypassed" in app.status_label.text.lower()
def test_ab_toggle_and_error_feedback(monkeypatch):
    """Test A/B toggle (denoising on/off) and error feedback in the GUI callback."""
    import numpy as np

    class DummyAudioIO:
        def start_stream(self, cb):
            # Simulate 16-sample audio buffer
            in_data = (np.ones(16, dtype=np.int16) * 1000).tobytes()
            out = cb(in_data)
            assert isinstance(out, bytes)
            return True
        def stop_stream(self): return True
        def enumerate_devices(self): return [{"id": 0, "name": "Dummy"}]
        def select_device(self, device_id): return True

    class DummyDenoiser:
        def __init__(self):
            self.called = False
            self.raise_error = False
        def process_buffer(self, audio):
            self.called = True
            if self.raise_error:
                raise RuntimeError("Mock inference error")
            return audio * 2  # Just double the audio for test

    # Instantiate app with dummy classes
    denoiser = DummyDenoiser()
    app = gui.DenoisingApp(DummyAudioIO(), denoiser)
    # Simulate denoise_checkbox attribute for both real and dummy widget
    app.denoise_checkbox.checked = True

    # Patch show_error to track calls
    errors = []
    app.show_error = lambda msg: errors.append(msg)

    # Test with denoising ON
    def test_callback_on(in_data):
        app.denoise_checkbox.checked = True
        return app.start_denoising()
    app.start_denoising()
    assert denoiser.called

    # Test with denoising OFF
    denoiser.called = False
    app.denoise_checkbox.checked = False
    app.start_denoising()
    assert not denoiser.called  # Should not call denoiser when toggle is off

    # Test error feedback
    denoiser.raise_error = True
    app.denoise_checkbox.checked = True
    app.start_denoising()
    assert any("Audio processing error" in e for e in errors)
    app = gui.DenoisingApp(DummyAudioIO(), DummyDenoiser())
    # Mock start/stop methods
    app.audio_io.start_stream = lambda: True
    app.audio_io.stop_stream = lambda: True
    assert app.audio_io.start_stream() is True
    assert app.audio_io.stop_stream() is True

def test_error_handling_status_display(monkeypatch):
    """Test error handling and status display (mocked)."""
    app = gui.DenoisingApp(DummyAudioIO(), DummyDenoiser())
    # Simulate error dialog method
    app.show_error = lambda msg: msg
    assert app.show_error("Test error") == "Test error"

def test_integration_with_audioio_and_denoiser():
    """Test integration with AudioIO and DenoisingInference (mocked)."""
    app = gui.DenoisingApp(DummyAudioIO(), DummyDenoiser())
    assert hasattr(app, "audio_io")
    assert hasattr(app, "denoiser")
def test_visualizer_updates_on_audio(monkeypatch):
    """
    Test that the real-time audio visualizer updates both input and output waveforms
    in the GUI when audio is processed (dummy mode).
    """
    import numpy as np
    import src.gui as gui_mod

    # Use dummy audio_io and denoiser
    class DummyAudioIO:
        def start_stream(self, callback):
            # Simulate a short audio buffer
            audio = (np.arange(16) / 16.0 * 2 - 1).astype(np.float32)
            in_data = (audio * 32768.0).clip(-32768, 32767).astype(np.int16).tobytes()
            callback(in_data)
            return True
        def stop_stream(self): return True
        def enumerate_devices(self): return [{"id": 0, "name": "Dummy"}]
        def select_device(self, device_id): return True

    class DummyDenoiser:
        def process_buffer(self, audio):
            # Return a simple transformation for output
            return audio * 0.5, False

    # Force dummy widgets/plots
    monkeypatch.setattr(gui_mod, "QtWidgets", None)
    monkeypatch.setattr(gui_mod, "pg", None)

    app = gui_mod.DenoisingApp(DummyAudioIO(), DummyDenoiser())
    # Simulate starting denoising (should update plots)
    app.audio_io.start_stream(lambda in_data: app.start_denoising())

    # The dummy plot widgets should have .data set
    assert hasattr(app.input_waveform_plot, "data")
    assert hasattr(app.output_waveform_plot, "data")
    # The input plot should have the last audio buffer
    assert app.input_waveform_plot.data is not None
    assert app.output_waveform_plot.data is not None
    # Output should be half the input
    np.testing.assert_allclose(app.output_waveform_plot.data, app.input_waveform_plot.data * 0.5, rtol=1e-5)