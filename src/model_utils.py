"""
model_utils.py

Utilities for model selection, quantization, and ONNX conversion.
- Supports Tiny Recurrent U-Net, SpeechDenoiser, and similar models
- Provides functions for model selection, quantization, and conversion
- Handles errors for unsupported models and conversion failures

Author: aiGI Auto-Coder
"""

import logging
import os
import platform
from typing import Any, Optional

try:
    import torch
    import torch.nn as nn
    import torch.quantization
except ImportError:
    torch = None

try:
    import onnx
except ImportError:
    onnx = None

SUPPORTED_MODELS = {
    "Tiny Recurrent U-Net": "trunet",
    "SpeechDenoiser": "speech_denoiser"
}

def _is_cpu_only() -> bool:
    # Enforce CPU-only logic
    if torch is not None:
        return not torch.cuda.is_available()
    return True

def select_model(name: str) -> Any:
    """
    Select and return a supported denoising model by name.

    Args:
        name (str): Model name.

    Returns:
        Any: Model object.

    Raises:
        ValueError: If model is unsupported.
        ImportError: If required backend is missing.
    """
    if not isinstance(name, str):
        raise TypeError("Model name must be a string.")
    if name not in SUPPORTED_MODELS:
        logging.error(f"Unsupported model: {name}")
        raise ValueError(f"Unsupported model: {name}")
    if torch is None:
        logging.error("PyTorch is required for model selection.")
        raise ImportError("PyTorch is not installed.")
    if not _is_cpu_only():
        logging.error("GPU detected. Only CPU execution is supported.")
        raise RuntimeError("Only CPU execution is supported.")
    # Instantiate real model architectures
    if name == "Tiny Recurrent U-Net":
        class TinyRecurrentUNet(nn.Module):
            """
            Minimal Tiny Recurrent U-Net for speech denoising.
            """
            def __init__(self, input_dim=1, hidden_dim=32, num_layers=2):
                super().__init__()
                self.encoder = nn.Sequential(
                    nn.Conv1d(input_dim, hidden_dim, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(hidden_dim, hidden_dim, kernel_size=3, padding=1),
                    nn.ReLU()
                )
                self.rnn = nn.GRU(hidden_dim, hidden_dim, num_layers, batch_first=True, bidirectional=True)
                self.decoder = nn.Sequential(
                    nn.Conv1d(hidden_dim * 2, hidden_dim, kernel_size=3, padding=1),
                    nn.ReLU(),
                    nn.Conv1d(hidden_dim, input_dim, kernel_size=3, padding=1)
                )

            def forward(self, x):
                # x: (batch, channels, time)
                enc = self.encoder(x)
                # RNN expects (batch, time, features)
                rnn_in = enc.permute(0, 2, 1)
                rnn_out, _ = self.rnn(rnn_in)
                # Back to (batch, features, time)
                rnn_out = rnn_out.permute(0, 2, 1)
                out = self.decoder(rnn_out)
                return out

        return TinyRecurrentUNet()
    elif name == "SpeechDenoiser":
        class SpeechDenoiser(nn.Module):
            """
            Minimal SpeechDenoiser model for speech enhancement.
            """
            def __init__(self, input_dim=1, hidden_dim=64):
                super().__init__()
                self.conv1 = nn.Conv1d(input_dim, hidden_dim, kernel_size=5, padding=2)
                self.relu1 = nn.ReLU()
                self.conv2 = nn.Conv1d(hidden_dim, hidden_dim, kernel_size=5, padding=2)
                self.relu2 = nn.ReLU()
                self.conv3 = nn.Conv1d(hidden_dim, input_dim, kernel_size=5, padding=2)

            def forward(self, x):
                x = self.conv1(x)
                x = self.relu1(x)
                x = self.conv2(x)
                x = self.relu2(x)
                x = self.conv3(x)
                return x

        return SpeechDenoiser()
        class DummySpeechDenoiser(nn.Module):
            def __init__(self):
                super().__init__()
                self.dummy = nn.Linear(10, 10)
            def forward(self, x):
                return self.dummy(x)
        return DummySpeechDenoiser()
    else:
        # Should never reach here due to earlier check
        raise ValueError(f"Unsupported model: {name}")

def quantize_model(model: Any) -> Any:
    """
    Quantize a supported model for CPU efficiency.

    Args:
        model (Any): Model object.

    Returns:
        Any: Quantized model.

    Raises:
        ValueError: If quantization is unsupported.
        TypeError: If model is not a torch.nn.Module.
    """
    if torch is None:
        logging.error("PyTorch is required for quantization.")
        raise ImportError("PyTorch is not installed.")
    if not isinstance(model, nn.Module):
        logging.error("Model must be a torch.nn.Module for quantization.")
        raise TypeError("Model must be a torch.nn.Module for quantization.")
    if not _is_cpu_only():
        logging.error("Quantization only supported on CPU.")
        raise RuntimeError("Quantization only supported on CPU.")
    try:
        model.eval()
        quantized_model = torch.quantization.quantize_dynamic(
            model, {nn.Linear}, dtype=torch.qint8
        )
        return quantized_model
    except Exception as e:
        logging.error(f"Quantization failed: {e}")
        raise ValueError(f"Quantization failed: {e}")

def convert_to_onnx(model: Any, output_path: str, input_shape=(1, 10)) -> None:
    """
    Convert a model to ONNX format.

    Args:
        model (Any): Model object.
        output_path (str): Path to save ONNX file.
        input_shape (tuple): Shape of dummy input for export.

    Raises:
        ValueError: If conversion fails.
        TypeError: If model or output_path is invalid.
    """
    if torch is None:
        logging.error("PyTorch is required for ONNX export.")
        raise ImportError("PyTorch is not installed.")
    if not isinstance(model, nn.Module):
        logging.error("Model must be a torch.nn.Module for ONNX export.")
        raise TypeError("Model must be a torch.nn.Module for ONNX export.")
    if not isinstance(output_path, str):
        logging.error("Output path must be a string.")
        raise TypeError("Output path must be a string.")
    if not _is_cpu_only():
        logging.error("ONNX export only supported on CPU.")
        raise RuntimeError("ONNX export only supported on CPU.")
    try:
        dummy_input = torch.randn(*input_shape)
        torch.onnx.export(
            model,
            dummy_input,
            output_path,
            export_params=True,
            opset_version=12,
            do_constant_folding=True,
            input_names=['input'],
            output_names=['output'],
            dynamic_axes={'input': {0: 'batch_size'}, 'output': {0: 'batch_size'}}
        )
        if not os.path.exists(output_path):
            raise ValueError("ONNX export failed: file not created.")
    except Exception as e:
        logging.error(f"ONNX export failed: {e}")
        raise ValueError(f"ONNX export failed: {e}")

def check_compatibility(model_path: str, backend: str) -> bool:
    """
    Check if the model is compatible with the selected backend and platform.

    Args:
        model_path (str): Path to model file.
        backend (str): "onnx" or "pytorch".

    Returns:
        bool: True if compatible, False otherwise.
    """
    if not isinstance(model_path, str) or not isinstance(backend, str):
        logging.error("model_path and backend must be strings.")
        raise TypeError("model_path and backend must be strings.")
    backend = backend.lower()
    if backend not in ("onnx", "pytorch"):
        logging.error(f"Unsupported backend: {backend}")
        raise ValueError(f"Unsupported backend: {backend}")
    if backend == "onnx":
        if onnx is None:
            logging.error("ONNX is not installed.")
            return False
        if not os.path.exists(model_path):
            logging.error(f"ONNX model file does not exist: {model_path}")
            return False
        try:
            onnx_model = onnx.load(model_path)
            onnx.checker.check_model(onnx_model)
            return True
        except Exception as e:
            logging.error(f"ONNX model compatibility check failed: {e}")
            return False
    elif backend == "pytorch":
        if torch is None:
            logging.error("PyTorch is not installed.")
            return False
        if not os.path.exists(model_path):
            logging.error(f"PyTorch model file does not exist: {model_path}")
            return False
        try:
            torch.load(model_path, map_location="cpu")
            return True
        except Exception as e:
            logging.error(f"PyTorch model compatibility check failed: {e}")
            return False
    return False

# End of model_utils.py