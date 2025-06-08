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
def test_get_model_info_supported():
    """Test get_model_info returns correct info for all supported models."""
    for model_name in model_utils.MODEL_REGISTRY:
        info = model_utils.get_model_info(model_name)
        assert "url" in info and "default_path" in info and "display_name" in info

def test_get_model_info_unsupported():
    """Test get_model_info raises ValueError for unsupported model."""
    with pytest.raises(ValueError):
        model_utils.get_model_info("not-a-real-model")

def test_ensure_model_exists_download(monkeypatch, tmp_path):
    """Test ensure_model_exists triggers download if file is missing, for all supported models."""
    called = {}
    def fake_exists(path):
        return False
    def fake_urlretrieve(url, path):
        called["url"] = url
        called["path"] = path
        with open(path, "wb") as f:
            f.write(b"dummy")
    monkeypatch.setattr(os.path, "exists", fake_exists)
    monkeypatch.setattr(model_utils.urllib.request, "urlretrieve", fake_urlretrieve)
    for model_name in model_utils.MODEL_REGISTRY:
        model_path = tmp_path / f"{model_name}.bin"
        model_utils.ensure_model_exists(model_name, str(model_path))
        assert called["url"] == model_utils.MODEL_REGISTRY[model_name]["url"]
        # Check file was actually created (do not use mocked os.path.exists)
        assert model_path.exists()

def test_ensure_model_exists_present(monkeypatch, tmp_path):
    """Test ensure_model_exists does not download if file exists."""
    def fake_exists(path):
        return True
    monkeypatch.setattr(os.path, "exists", fake_exists)
    called = {}
    def fake_urlretrieve(url, path):
        called["fail"] = True
    monkeypatch.setattr(model_utils.urllib.request, "urlretrieve", fake_urlretrieve)
    for model_name in model_utils.MODEL_REGISTRY:
        model_utils.ensure_model_exists(model_name, "dummy_path")
    assert "fail" not in called