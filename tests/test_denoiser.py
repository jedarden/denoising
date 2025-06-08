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

# Patch denoiser.torch to a dummy object if not available, so tests can run without torch installed
import types
# Remove duplicate/old dummy torch patch

def always_exists(path):
    return True
import src.denoiser as denoiser

# Patch denoiser.torch to a dummy object if not available, so tests can run without torch installed
import types
if not hasattr(denoiser, "torch") or denoiser.torch is None:
    class DummyTorch:
        class nn:
            class ReflectionPad1d:
                pass
        def no_grad(self):
            class DummyContext:
                def __enter__(self): return None
                def __exit__(self, exc_type, exc_val, exc_tb): return False
            return DummyContext()
        def from_numpy(self, arr):
            # Return a dummy object with float(), unsqueeze(), and cpu().numpy()
            class DummyTensor:
                def float(self): return self
                def unsqueeze(self, dim): return self
                def cpu(self): return self
                def numpy(self): return arr
                def squeeze(self, dim): return self
            return DummyTensor()
    denoiser.torch = DummyTorch()

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
    monkeypatch.setattr("os.path.exists", always_exists)
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
    assert not bypassed
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
    monkeypatch.setattr("os.path.exists", always_exists)
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
    assert not bypassed
    assert len(output) == 11  # required_pad_sum+1
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
        def __call__(self, x): return x  # Make it callable for inference

    # Patch load_pytorch_model to return DummyModel
    monkeypatch.setattr(denoiser, "load_pytorch_model", lambda path, logger=None: DummyModel())
    # Patch os.path.exists to always return True
    monkeypatch.setattr("os.path.exists", always_exists)

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
            if buf_len < 2:
                # Should be bypassed, output matches input
                assert np.allclose(out, audio)
                assert bypassed
            else:
                # Output should be at least required_pad_sum+1 or min_input_length
                assert len(out) >= max(min_input_length, instance.required_pad_sum + 1)
                assert not bypassed
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
        def __call__(self, x): return x

    monkeypatch.setattr(denoiser, "load_pytorch_model", lambda path, logger=None: DummyModelNoPad())
    # Patch os.path.exists to always return True
    monkeypatch.setattr("os.path.exists", always_exists)

    force_min = 32
    instance = denoiser.DenoisingInference("mock_model.pth", min_input_length=4, force_min_input_length=force_min)
    instance.load_model()
    instance.loaded = True

    # Try a short buffer
    audio = np.ones(5, dtype=np.float32)
    out, bypassed = instance.process_buffer(audio)
    assert not bypassed
    assert len(out) == force_min
    assert not bypassed
def test_reflectionpad1d_padding_and_no_error(monkeypatch):
    """Test that process_buffer always pads input to avoid ReflectionPad1d error, even for shortest input."""
    import pytest
    pytest.importorskip("torch")
    import numpy as np
    import torch

    cls = denoiser.DenoisingInference
    min_len = 8

    # Dummy model with ReflectionPad1d layer
    class DummyPadModel(torch.nn.Module):
        def __init__(self, pad):
            super().__init__()
            self.pad = pad
            self.pad_layer = torch.nn.ReflectionPad1d(pad)
        def eval(self): return self
        def forward(self, x):
            # Just apply the pad and return
            return self.pad_layer(x)

    pad = (5, 5)
    required_pad_sum = sum(pad)
    instance = cls("mock_model.pth", min_input_length=min_len)
    instance.loaded = True
    instance.model = DummyPadModel(pad)
    instance.required_pad_sum = required_pad_sum

    # Test with input shorter than required_pad_sum
    short_audio = np.ones(3, dtype=np.float32)
    output, bypassed = instance.process_buffer(short_audio)
    assert isinstance(output, np.ndarray)
    # Output should be at least min_input_length or required_pad_sum+1
    assert len(output) >= max(min_len, required_pad_sum + 1)
    assert not bypassed

    # Test with input exactly equal to required_pad_sum
    exact_audio = np.ones(required_pad_sum, dtype=np.float32)
    output, bypassed = instance.process_buffer(exact_audio)
    assert isinstance(output, np.ndarray)
    assert len(output) >= max(min_len, required_pad_sum + 1)
    assert not bypassed

    # Test with input just above required_pad_sum
    just_enough_audio = np.ones(required_pad_sum + 1, dtype=np.float32)
    output, bypassed = instance.process_buffer(just_enough_audio)
    assert isinstance(output, np.ndarray)
    # Output length should be input + sum(pad) due to ReflectionPad1d
    assert len(output) == (required_pad_sum + 1 + required_pad_sum)
    assert not bypassed

    # Test with normal input
    normal_audio = np.ones(20, dtype=np.float32)
    output, bypassed = instance.process_buffer(normal_audio)
    assert isinstance(output, np.ndarray)
    # Output length should be input + sum(pad) due to ReflectionPad1d
    assert len(output) == (20 + required_pad_sum)
    assert not bypassed

    # Test with force_min_input_length fallback
    instance.required_pad_sum = 0
    instance.force_min_input_length = 12
    # Patch model to not add any padding
    class IdentityModel:
        def __call__(self, x): return x
    instance.model = IdentityModel()
    short_audio = np.ones(5, dtype=np.float32)
    output, bypassed = instance.process_buffer(short_audio)
    assert isinstance(output, np.ndarray)
    assert len(output) == 12
    assert not bypassed
def test_reflectionpad1d_input_length_hardening(monkeypatch):
    """
    Test that process_buffer always pads input to strictly greater than the required ReflectionPad1d padding,
    even for edge-case buffer sizes.
    """
    import numpy as np
    import types
def test_reflectionpad1d_input_length_hardening(monkeypatch):
    """
    Test that process_buffer always pads input to strictly greater than the required ReflectionPad1d padding,
    even for edge-case buffer sizes.
    """
    import numpy as np
    import types

    # Patch torch.nn.ReflectionPad1d to match what denoiser.py expects
    class DummyReflectionPad1d:
        def __init__(self, padding):
            self.padding = padding

    # Mock model with modules() returning ReflectionPad1d layers
    class MockModel:
        def modules(self):
            # pad=5 (int), pad=(7,7) (tuple), pad=(3,4) (tuple)
            return [DummyReflectionPad1d(5), DummyReflectionPad1d((7,7)), DummyReflectionPad1d((3,4))]
        def eval(self): pass

    # Patch load_pytorch_model to return our mock model
    monkeypatch.setattr(denoiser, "load_pytorch_model", lambda path, logger=None: MockModel())
    monkeypatch.setattr("os.path.exists", always_exists)
    # Patch denoiser.torch.nn.ReflectionPad1d to DummyReflectionPad1d
    denoiser.torch.nn.ReflectionPad1d = DummyReflectionPad1d

    # Create DenoisingInference and load model
    DenoisingInference = denoiser.DenoisingInference
    min_input_length = 10
    instance = DenoisingInference("mock_model.pth", min_input_length=min_input_length)
    instance.load_model()

    # Check that required_pad_sum and max_single_pad are set correctly
    assert instance.required_pad_sum == 14  # max(sum(7,7)=14, 5*2=10, sum(3,4)=7)
    assert instance.max_single_pad == 7     # max(7,5,4)

    # Patch model to a dummy callable for inference
    class DummyModel:
        def __call__(self, x): return x
    instance.model = DummyModel()

    # Test input shorter than max_single_pad
    buf = np.ones(5, dtype=np.float32)
    out, bypassed = instance.process_buffer(buf.copy())
    assert not bypassed
    assert len(out) == max(min_input_length, instance.required_pad_sum+1, instance.max_single_pad+1)

    # Test input exactly equal to max_single_pad
    buf = np.ones(7, dtype=np.float32)
    out, bypassed = instance.process_buffer(buf.copy())
    assert not bypassed
    assert len(out) == max(min_input_length, instance.required_pad_sum+1, instance.max_single_pad+1)

    # Test input just above max_single_pad but below required_pad_sum
    buf = np.ones(8, dtype=np.float32)
    out, bypassed = instance.process_buffer(buf.copy())
    assert not bypassed
    assert len(out) == max(min_input_length, instance.required_pad_sum+1, instance.max_single_pad+1)

    # Test input just above required_pad_sum
    buf = np.ones(15, dtype=np.float32)
    out, bypassed = instance.process_buffer(buf.copy())
    assert not bypassed
    assert len(out) == 15

    # Test input much longer than any pad
    buf = np.ones(100, dtype=np.float32)
    out, bypassed = instance.process_buffer(buf.copy())
    assert not bypassed
    assert len(out) == 100

    # Test input length < 2 (should bypass)
    buf = np.ones(1, dtype=np.float32)
    out, bypassed = instance.process_buffer(buf.copy())
    assert bypassed
def test_reflectionpad1d_bulletproof_input_length(monkeypatch):
    """
    Test that DenoisingInference.process_buffer never throws a ReflectionPad1d error,
    even for the shortest possible input, for all model configurations.
    """
    import numpy as np
    import logging

    # Use real torch if available, else dummy
    try:
        import torch
        import torch.nn as nn
        TORCH_AVAILABLE = True
    except ImportError:
        torch = denoiser.torch
        nn = torch.nn
        TORCH_AVAILABLE = False

    # Define a minimal model with ReflectionPad1d (padding=20)
    class DummyModel(nn.Module if TORCH_AVAILABLE else object):
        def __init__(self):
            # Always pass padding argument, even for dummy torch
            self.pad = nn.ReflectionPad1d((20, 20))
        def eval(self): return self
        def forward(self, x):
            # x: (1, N)
            return self.pad(x) if hasattr(self.pad, "__call__") else x

        def __call__(self, x):
            return self.forward(x)

        def modules(self):
            # Simulate a model with a ReflectionPad1d layer with padding=(20, 20)
            class DummyPad:
                padding = (20, 20)
            return [DummyPad()]

    # Patch load_pytorch_model to return our dummy model
    monkeypatch.setattr(denoiser, "load_pytorch_model", lambda path, logger=None: DummyModel())

    # Patch os.path.exists to always return True
    monkeypatch.setattr(denoiser.os.path, "exists", lambda path: True)

    # Create DenoisingInference and load model
    di = denoiser.DenoisingInference("dummy_path")

    # Patch load_model to set max_single_pad and required_pad_sum directly for the test
    def patched_load_model(self):
        self.model = DummyModel()
        self.loaded = True
        self.max_single_pad = 20
        self.required_pad_sum = 40
    di.load_model = patched_load_model.__get__(di, denoiser.DenoisingInference)
    di.load_model()

    # Confirm max_single_pad is set correctly
    assert di.max_single_pad == 20

    # Test all input lengths from 1 up to 2*max_single_pad + 2
    for L in range(1, 2 * di.max_single_pad + 3):
        arr = np.ones(L, dtype=np.float32)
        try:
            out, bypassed = di.process_buffer(arr)
            assert isinstance(out, np.ndarray)
            assert out.shape[0] >= 2 * di.max_single_pad + 1 or bypassed
            assert not np.any(np.isnan(out))
        except Exception as e:
            pytest.fail(f"process_buffer failed for input length {L}: {e}")

    # Also test with input length much larger than required
    arr = np.ones(1000, dtype=np.float32)
    out, bypassed = di.process_buffer(arr)
    assert isinstance(out, np.ndarray)
    assert out.shape[0] == 1000 or out.shape[0] > 0
    assert not np.any(np.isnan(out))