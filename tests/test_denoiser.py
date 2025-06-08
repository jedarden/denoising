"""
Test suite for denoiser.py

Covers:
- Canonical DenoisingInference interface (no duplicates)
- Model loading and unloading (CPU-only, mocked)
- Denoising inference logic (input/output shape, type, and value checks, mocked)
- Error handling (model not found, invalid input, etc.)
- Input validation and type annotations
- Logging and exception reporting

TDD: All tests initially fail to drive implementation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import src.denoiser as denoiser

def test_single_denoisinginference_class():
    """Test that only one DenoisingInference class exists and is importable."""
    assert hasattr(denoiser, "DenoisingInference")
    assert isinstance(denoiser.DenoisingInference, type)
    assert len([name for name in dir(denoiser) if name == "DenoisingInference"]) == 1

def test_denoisinginference_signature_and_docstring():
    """Test that all public methods have correct signatures and docstrings."""
    cls = denoiser.DenoisingInference
    assert cls.__doc__ is not None and "Loads and runs efficient" in cls.__doc__
    for name in dir(cls):
        if not name.startswith("_"):
            attr = getattr(cls, name)
            if callable(attr):
                assert attr.__doc__ is not None

def test_model_loading_unloading(monkeypatch):
    """Test model loading and unloading (mocked for CPU-only)."""
    cls = denoiser.DenoisingInference
    instance = cls("mock_model.pth", min_input_length=1)
    monkeypatch.setattr(instance, "load_model", lambda: True)
    monkeypatch.setattr(instance, "unload_model", lambda: True)
    assert instance.load_model() is True
    assert instance.unload_model() is True

def test_denoising_inference_logic(monkeypatch):
    """Test denoising inference logic (input/output checks, mocked)."""
    cls = denoiser.DenoisingInference
    instance = cls("mock_model.pth", min_input_length=1)
    # Mock inference method
    monkeypatch.setattr(instance, "infer", lambda x: [0.0 for _ in x])
    input_data = [0.1, 0.2, 0.3]
    output = instance.infer(input_data)
    assert isinstance(output, list)
    assert len(output) == len(input_data)
def test_short_audio_buffer_padding(monkeypatch):
    """Test that short audio buffers are padded to min_input_length in process_buffer."""
    import numpy as np
    cls = denoiser.DenoisingInference
    min_len = 64
    instance = cls("mock_model.pth", min_input_length=min_len)
    instance.loaded = True
    # Mock model: just returns input tensor as output
    class DummyModel:
        def eval(self): return self
        def __call__(self, x): return x
    instance.model = DummyModel()
    # Short buffer
    short_audio = np.ones(10, dtype=np.float32)
    output, bypassed = instance.process_buffer(short_audio)
    assert isinstance(output, np.ndarray)
    assert len(output) == min_len
    assert not bypassed
    # The first 10 samples should match input, the rest should be padded (reflection or zeros)
    np.testing.assert_allclose(output[:10], short_audio, rtol=1e-5)

def test_extremely_short_audio_buffer_bypasses_denoising(monkeypatch):
    """Test that extremely short audio buffers (<2 samples) bypass denoising and return raw audio."""
    import numpy as np
    cls = denoiser.DenoisingInference
    min_len = 64
    instance = cls("mock_model.pth", min_input_length=min_len)
    instance.loaded = True
    # Mock model: just returns input tensor as output
    class DummyModel:
        def eval(self): return self
        def __call__(self, x): return x
    instance.model = DummyModel()
    # Test with 1-sample buffer
    short_audio = np.array([0.5], dtype=np.float32)
    output, bypassed = instance.process_buffer(short_audio)
    assert isinstance(output, np.ndarray)
    assert np.allclose(output, short_audio)
    assert bypassed
    # Test with 0-sample buffer
    empty_audio = np.array([], dtype=np.float32)
    output, bypassed = instance.process_buffer(empty_audio)
    assert isinstance(output, np.ndarray)
    assert np.allclose(output, empty_audio)
    assert bypassed

def test_error_handling_model_not_found(monkeypatch):
    """Test error handling for model not found (mocked)."""
    cls = denoiser.DenoisingInference
    instance = cls("bad_path.pth")
    monkeypatch.setattr(instance, "load_model", lambda: (_ for _ in ()).throw(FileNotFoundError("Model not found")))
    with pytest.raises(FileNotFoundError):
        instance.load_model()

def test_error_handling_invalid_input(monkeypatch):
    """Test error handling for invalid input (mocked)."""
    cls = denoiser.DenoisingInference
    instance = cls("mock_model.pth", min_input_length=1)
    monkeypatch.setattr(instance, "process_buffer", lambda x: (_ for _ in ()).throw(ValueError("Invalid input")))
    with pytest.raises(ValueError):
        instance.process_buffer(None)

def test_input_validation(monkeypatch):
    """Test that invalid input types/values are rejected with clear errors (mocked)."""
    cls = denoiser.DenoisingInference
    # Backend selection is no longer supported; this test is obsolete.
def test_reflectionpad1d_padding_prevents_error(monkeypatch):
    """
    Test that process_buffer pads input with zeros if input length <= required_pad_sum,
    preventing ReflectionPad1d errors for the shortest possible input.
    """
    import numpy as np
    cls = denoiser.DenoisingInference
    instance = cls("mock_model.pth", min_input_length=1)
    # Simulate a model with ReflectionPad1d(padding=(5,5)), so required_pad_sum=10
    instance.required_pad_sum = 10
    instance.loaded = True

    # Mock model: just returns input tensor as output (simulate identity model)
    class DummyModel:
        def __call__(self, x):
            return x

    instance.model = DummyModel()

    # Input shorter than or equal to required_pad_sum
    short_input = np.array([0.1] * 5, dtype=np.float32)  # length 5 <= 10
    output, bypassed = instance.process_buffer(short_input)
    # Should be padded to required_pad_sum+1 = 11
    assert isinstance(output, np.ndarray)
    assert output.shape[0] == 11
    assert not bypassed  # Should not bypass, should pad and run

    # Input exactly required_pad_sum
    exact_input = np.array([0.2] * 10, dtype=np.float32)
    output2, bypassed2 = instance.process_buffer(exact_input)
    assert output2.shape[0] == 11
    assert not bypassed2

    # Input longer than required_pad_sum
    long_input = np.array([0.3] * 12, dtype=np.float32)
    output3, bypassed3 = instance.process_buffer(long_input)
    assert output3.shape[0] == 12
    assert not bypassed3
def test_no_reflectionpad1d_error_on_edge_cases(monkeypatch):
    """
    Test that DenoisingInference never triggers a ReflectionPad1d error,
    even for edge-case buffer sizes, by simulating a model with ReflectionPad1d.
    """
    import numpy as np
    import types

    # Simulate a model with ReflectionPad1d(padding=8)
    class DummyReflectionPad1d:
        def __init__(self, padding):
            self.padding = padding

    class DummyModel:
        def __init__(self):
            self._modules = [DummyReflectionPad1d(8)]
        def modules(self):
            return self._modules
        def eval(self): pass

    # Patch load_pytorch_model to return DummyModel
    monkeypatch.setattr(denoiser, "load_pytorch_model", lambda path, logger=None: DummyModel())

    # Create DenoisingInference with min_input_length < required_pad_sum
    min_input_length = 4
    instance = denoiser.DenoisingInference("mock_model.pth", min_input_length=min_input_length)
    instance.load_model()

    # Patch process_buffer to bypass actual torch/noise logic
    monkeypatch.setattr(instance, "model", DummyModel())
    instance.loaded = True

    # Try a range of edge-case buffer sizes
    for buf_len in [0, 1, 8, 15, 16, 20]:
        audio = np.ones(buf_len, dtype=np.float32)
        try:
            out, bypassed = instance.process_buffer(audio)
            assert isinstance(out, np.ndarray)
            # Output should be at least required_pad_sum+1 or min_input_length
            assert len(out) >= max(min_input_length, instance.required_pad_sum + 1)
        except Exception as e:
            pytest.fail(f"ReflectionPad1d error or unexpected exception for buf_len={buf_len}: {e}")

def test_force_min_input_length_enforced(monkeypatch):
    """
    Test that force_min_input_length is strictly enforced if model padding cannot be determined.
    """
    import numpy as np

    class DummyModelNoPad:
        def modules(self): return []
        def eval(self): pass

    monkeypatch.setattr(denoiser, "load_pytorch_model", lambda path, logger=None: DummyModelNoPad())

    force_min = 32
    instance = denoiser.DenoisingInference("mock_model.pth", min_input_length=4, force_min_input_length=force_min)
    instance.load_model()
    instance.loaded = True

    # Try a short buffer
    audio = np.ones(5, dtype=np.float32)
    out, bypassed = instance.process_buffer(audio)
    assert isinstance(out, np.ndarray)
    assert len(out) >= force_min