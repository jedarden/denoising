"""
model_utils.py

Utilities for model selection and quantization.
- Supports Tiny Recurrent U-Net, SpeechDenoiser, and similar models
- Provides functions for model selection and quantization
- Handles errors for unsupported models and failures

Author: aiGI Auto-Coder
"""
import logging
import os
import urllib.request

# Registry of supported models with their download URLs and default paths
MODEL_REGISTRY = {
    "silero": {
        "display_name": "Silero Denoiser",
        "default_path": "models/silero-denoiser.jit",
        "url": None,
        "format": ".jit",
        "notes": (
            "Fast, robust, and widely used for speech denoising. "
            "Automatic download is currently unavailable. "
            "Manual download required. See: https://github.com/snakers4/silero-models"
        )
    },
    "facebook-denoiser": {
        "display_name": "Facebook Denoiser",
        "default_path": "models/facebook-denoiser.pth",
        "url": None,
        "format": ".pth",
        "notes": (
            "Official Facebook Denoiser model. "
            "Automatic download is currently unavailable. "
            "Manual download required. See: https://github.com/facebookresearch/denoiser"
        )
    },
    "dcunet": {
        "display_name": "DCUNet (SpeechBrain)",
        "default_path": "models/dcunet-16khz.ckpt",
        "url": None,
        "format": ".ckpt",
        "notes": (
            "DCUNet model from SpeechBrain. "
            "Automatic download is currently unavailable. "
            "Manual download required. See: https://github.com/speechbrain/speechbrain"
        )
    }
}

def get_model_info(model_name: str):
    """Return model info dict for a given model name."""
    if model_name not in MODEL_REGISTRY:
        raise ValueError(f"Unsupported model: {model_name}. Supported: {list(MODEL_REGISTRY.keys())}")
    return MODEL_REGISTRY[model_name]

def ensure_model_exists(model_name: str, model_path: str = None, url: str = None) -> None:
    """
    Ensure the denoising model file exists at model_path.
    If missing, attempt to download it from a public URL.
    If all automated downloads fail, provide a clear error message with manual download instructions.

    Args:
        model_name (str): Name of the model in MODEL_REGISTRY.
        model_path (str, optional): Path to the model file. If None, uses the default path from registry.
        url (str, optional): URL to download the model from. If None, uses the default public link.

    Raises:
        RuntimeError: If download fails and manual download is required.
    """
    info = get_model_info(model_name)
    model_path = model_path or info["default_path"]
    download_url = url or info["url"]
    display_name = info["display_name"]
    notes = info.get("notes", "")

    MANUAL_INSTRUCTIONS = (
        f"\n\n"
        f"Automatic download of the {display_name} model is not available.\n"
        f"To proceed, please manually download the model file as described below:\n"
        f"{notes}\n"
        f"Place the downloaded file at:\n"
        f"  {os.path.abspath(model_path)}\n"
        f"Create the directory if it does not exist.\n"
        f"Example:\n"
        f"  mkdir -p {os.path.dirname(os.path.abspath(model_path))}\n"
        f"  mv <downloaded_file> {os.path.abspath(model_path)}\n"
    )

    if os.path.exists(model_path):
        logging.info(f"Model file found: {model_path}")
        return

    if download_url is None:
        raise RuntimeError(MANUAL_INSTRUCTIONS)

    # If a URL is provided (future-proofing), attempt download
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    logging.info(f"Model file not found at {model_path}. Attempting download from {download_url} ...")
    try:
        urllib.request.urlretrieve(download_url, model_path)
        logging.info(f"Model downloaded and saved to {model_path}")
    except Exception as e:
        raise RuntimeError(
            f"Failed to download model from {download_url}.\n"
            f"Error: {e}\n"
            f"{MANUAL_INSTRUCTIONS}"
        )
        return

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    logging.info(f"Model file not found at {model_path}. Attempting download from {download_url} ...")
    try:
        urllib.request.urlretrieve(download_url, model_path)
        logging.info(f"Model downloaded and saved to {model_path}")
    except Exception as e:
        logging.error(f"Failed to download model: {e}")
        raise RuntimeError(
            f"Failed to download model from {download_url}.\n"
            f"Error: {e}\n"
            f"{MANUAL_INSTRUCTIONS}"
        )
from typing import Any

try:
    import torch
    import torch.nn as nn
    import torch.quantization
except ImportError:
    torch = None

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

# Removed convert_to_onnx and ONNX-related compatibility checks

def check_compatibility(model_path: str) -> bool:
    """
    Check if the model is compatible with PyTorch and the current platform.

    Args:
        model_path (str): Path to model file.

    Returns:
        bool: True if compatible, False otherwise.
    """
    if not isinstance(model_path, str):
        logging.error("model_path must be a string.")
        raise TypeError("model_path must be a string.")
    if torch is None:
        logging.error("PyTorch is not installed.")
        return False
    if not os.path.exists(model_path):
        logging.error(f"PyTorch model file does not exist: {model_path}")
        return False
    try:
        model = torch.load(model_path, map_location="cpu")
        if not isinstance(model, nn.Module):
            logging.error("Loaded object is not a torch.nn.Module.")
            return False
        return True
    except Exception as e:
        logging.error(f"PyTorch model compatibility check failed: {e}")
        return False