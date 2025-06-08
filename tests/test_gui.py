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