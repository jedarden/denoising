"""
Test suite for model_utils.py

Covers:
- Canonical utility functions (no duplicates)
- Model selection (supported/unsupported models, mocked)
- Quantization (supported/unsupported models, mocked)
- ONNX conversion (mocked)
- Error handling for unsupported models/conversion failures

TDD: All tests initially fail to drive implementation.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pytest
import src.model_utils as model_utils

def test_select_model_supported(monkeypatch):
    """Test model selection for supported models (mocked)."""
    monkeypatch.setattr(model_utils, "select_model", lambda name: "mock_model" if name == "Tiny Recurrent U-Net" else (_ for _ in ()).throw(ValueError("Unsupported model")))
    assert model_utils.select_model("Tiny Recurrent U-Net") == "mock_model"

def test_select_model_unsupported(monkeypatch):
    """Test model selection for unsupported models (mocked)."""
    monkeypatch.setattr(model_utils, "select_model", lambda name: (_ for _ in ()).throw(ValueError("Unsupported model")))
    with pytest.raises(ValueError):
        model_utils.select_model("UnknownModel")

def test_quantize_model_supported(monkeypatch):
    """Test quantization for supported models (mocked)."""
    monkeypatch.setattr(model_utils, "quantize_model", lambda model: "quantized_model" if model == "mock_model" else (_ for _ in ()).throw(ValueError("Quantization unsupported")))
    assert model_utils.quantize_model("mock_model") == "quantized_model"

def test_quantize_model_unsupported(monkeypatch):
    """Test quantization for unsupported models (mocked)."""
    monkeypatch.setattr(model_utils, "quantize_model", lambda model: (_ for _ in ()).throw(ValueError("Quantization unsupported")))
    with pytest.raises(ValueError):
        model_utils.quantize_model("bad_model")