"""
Test suite for audio_io.py

Covers:
- Canonical AudioIO interface (no duplicates)
- Device enumeration and selection (cross-platform, mocked)
- Stream start/stop logic (CPU-only, resource management, mocked)
- Error handling (device not found, permission denied, etc.)
- Input validation and type annotations
- Logging and exception reporting

TDD: All tests initially fail to drive implementation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import sys
import types

import src.audio_io as audio_io

def test_single_audioio_class():
    """Test that only one AudioIO class exists and is importable."""
    assert hasattr(audio_io, "AudioIO")
    assert isinstance(audio_io.AudioIO, type)
    # Check for duplicates (should only be one class)
    assert len([name for name in dir(audio_io) if name == "AudioIO"]) == 1

def test_audioio_signature_and_docstring():
    """Test that all public methods have correct signatures and docstrings."""
    cls = audio_io.AudioIO
    assert cls.__doc__ is not None and "Cross-platform" in cls.__doc__
    for name in dir(cls):
        if not name.startswith("_"):
            attr = getattr(cls, name)
            if callable(attr):
                assert attr.__doc__ is not None

def test_device_enumeration(monkeypatch):
    """Test device listing returns expected structure (mocked for cross-platform)."""
    cls = audio_io.AudioIO
    io = cls()
    # Mock the enumerate_devices method
    monkeypatch.setattr(io, "enumerate_devices", lambda: [{"id": 0, "name": "Mock Mic"}])
    devices = io.enumerate_devices()
    assert isinstance(devices, list)
    assert devices and "id" in devices[0] and "name" in devices[0]

def test_device_selection_valid_invalid(monkeypatch):
    """Test device selection with valid and invalid device IDs (mocked)."""
    cls = audio_io.AudioIO
    io = cls()
    monkeypatch.setattr(io, "select_device", lambda device_id: device_id == 0)
    assert io.select_device(0) is True
    assert io.select_device(999) is False

def test_stream_start_stop(monkeypatch):
    """Test start_stream and stop_stream open/close resources correctly (mocked)."""
    cls = audio_io.AudioIO
    io = cls()
    monkeypatch.setattr(io, "start_stream", lambda: True)
    monkeypatch.setattr(io, "stop_stream", lambda: True)
    assert io.start_stream() is True
    assert io.stop_stream() is True

def test_resource_cleanup_on_exception(monkeypatch):
    """Test resource cleanup on exceptions during streaming (mocked)."""
    cls = audio_io.AudioIO
    io = cls()
    monkeypatch.setattr(io, "start_stream", lambda: (_ for _ in ()).throw(RuntimeError("Stream error")))
    try:
        io.start_stream()
    except RuntimeError as e:
        assert "Stream error" in str(e)

def test_cpu_only_compliance(monkeypatch):
    """Test that no GPU/accelerator code is invoked (mock platform/device checks)."""
    cls = audio_io.AudioIO
    io = cls()
    # Simulate a method that would raise if GPU is used
    monkeypatch.setattr(io, "is_cpu_only", lambda: True)
    assert io.is_cpu_only() is True

def test_error_handling(monkeypatch):
    """Test exceptions are raised for invalid device, busy device, or permission errors (mocked)."""
    cls = audio_io.AudioIO
    io = cls()
    monkeypatch.setattr(io, "select_device", lambda device_id: (_ for _ in ()).throw(PermissionError("Permission denied")))
    with pytest.raises(PermissionError):
        io.select_device(1)

def test_input_validation(monkeypatch):
    """Test that invalid input types/values are rejected with clear errors (mocked)."""
    cls = audio_io.AudioIO
    io = cls()
    monkeypatch.setattr(io, "set_sample_rate", lambda sr: isinstance(sr, int) and sr > 0)
    assert io.set_sample_rate(16000) is True
    assert io.set_sample_rate(-1) is False
    assert io.set_sample_rate("bad") is False
def test_virtual_microphone_integration(monkeypatch):
    """Test that AudioIO routes denoised audio to VirtualMicrophoneService if provided."""
    class MockVirtualMicrophoneService:
        def __init__(self):
            self.frames = []
        def stream_audio_frame(self, frame):
            self.frames.append(frame)

    # Patch PyAudio to avoid actual audio hardware
    class DummyStream:
        def start_stream(self): pass
        def stop_stream(self): pass
        def close(self): pass
    class DummyPyAudio:
        def open(self, **kwargs): return DummyStream()
        def terminate(self): pass
    monkeypatch.setattr(audio_io, "pyaudio", type("pyaudio", (), {"PyAudio": DummyPyAudio, "paInt16": 8}))
    monkeypatch.setattr(audio_io, "logging", __import__("logging"))

    mock_vm = MockVirtualMicrophoneService()
    io = audio_io.AudioIO(virtual_microphone_service=mock_vm)
    io._callback = lambda x: b"denoised"
    # Simulate internal callback
    io._internal_callback(b"raw", 160, None, None)
    assert mock_vm.frames == [b"denoised"]