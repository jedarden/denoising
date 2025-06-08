"""
denoiser.py

Handles loading, quantization, and inference for speech denoising models.
- Supports PyTorch models (e.g., Tiny Recurrent U-Net, SpeechDenoiser)
- CPU-only, offline inference
- Quantization utilities for efficient real-time operation
- Error handling for model load failures and unsupported formats

Author: aiGI Auto-Coder
"""

import logging
import os
from typing import Any, Union

import numpy as np

try:
    import torch
    import torch.nn as nn
except ImportError:
    torch = None

from src.model_utils import select_model, quantize_model

class DenoisingInference:
    """
    Loads and runs efficient, CPU-only denoising models (PyTorch only).
    """

    def __init__(self, model_path: str):
        """
        Initialize the denoising model.

        Args:
            model_path (str): Path to the PyTorch model file.
        """
        if not isinstance(model_path, str):
            raise TypeError("model_path must be a string.")
        self.model_path = model_path
        self.model = None
        self._quantized = False
        self.device = "cpu"
        self.loaded = False

    def load_model(self):
        """
        Load the denoising model from file.
        Raises error on failure.
        """
        if torch is None:
            logging.error("PyTorch is not installed.")
            raise ImportError("PyTorch is not installed.")
        if not os.path.exists(self.model_path):
            logging.error(f"PyTorch model file not found: {self.model_path}")
            raise FileNotFoundError(f"PyTorch model file not found: {self.model_path}")
        try:
            self.model = torch.load(self.model_path, map_location="cpu")
            self.model.eval()
            self.loaded = True
        except Exception as e:
            logging.error(f"Failed to load PyTorch model: {e}")
            raise RuntimeError(f"Failed to load PyTorch model: {e}")

    def quantize_model(self):
        """
        Quantize the model for CPU efficiency (if supported).
        """
        if torch is None:
            logging.error("PyTorch is not installed.")
            raise ImportError("PyTorch is not installed.")
        if not isinstance(self.model, nn.Module):
            logging.error("Model must be a torch.nn.Module for quantization.")
            raise TypeError("Model must be a torch.nn.Module for quantization.")
        try:
            self.model = quantize_model(self.model)
            self._quantized = True
        except Exception as e:
            logging.error(f"Quantization failed: {e}")
            raise RuntimeError(f"Quantization failed: {e}")

    def process_buffer(self, audio_buffer: np.ndarray) -> np.ndarray:
        """
        Run denoising inference on a single audio buffer.

        Args:
            audio_buffer (np.ndarray): Input audio buffer.

        Returns:
            np.ndarray: Denoised audio buffer.
        """
        if not self.loaded:
            logging.error("Model is not loaded.")
            raise RuntimeError("Model is not loaded.")
        if not isinstance(audio_buffer, np.ndarray):
            logging.error("audio_buffer must be a numpy ndarray.")
            raise TypeError("audio_buffer must be a numpy ndarray.")
        if torch is None:
            logging.error("PyTorch is not installed.")
            raise ImportError("PyTorch is not installed.")
        try:
            with torch.no_grad():
                input_tensor = torch.from_numpy(audio_buffer).float().unsqueeze(0)
                output_tensor = self.model(input_tensor)
                return output_tensor.squeeze(0).cpu().numpy()
        except Exception as e:
            logging.error(f"PyTorch inference failed: {e}")
            raise RuntimeError(f"PyTorch inference failed: {e}")

    def is_quantized(self) -> bool:
        """
        Check if the model is quantized.

        Returns:
            bool: True if quantized, False otherwise.
        """
        return self._quantized

    def unload_model(self):
        """
        Unload the denoising model and free resources.
        """
        self.model = None
        self.session = None
        self.loaded = False
        return True

    def infer(self, input_data: Union[list, np.ndarray]) -> Union[list, np.ndarray]:
        """
        Run denoising inference on input data.

        Args:
            input_data (list or np.ndarray): Input audio data.

        Returns:
            list or np.ndarray: Denoised audio data.
        """
        if input_data is None:
            logging.error("input_data cannot be None.")
            raise ValueError("input_data cannot be None.")
        if isinstance(input_data, list):
            input_data = np.array(input_data, dtype=np.float32)
        if not isinstance(input_data, np.ndarray):
            logging.error("input_data must be a list or numpy ndarray.")
            raise TypeError("input_data must be a list or numpy ndarray.")
        output = self.process_buffer(input_data)
        if isinstance(output, np.ndarray):
            return output
        return np.array(output)

    def set_backend(self, backend: str) -> bool:
        """
        Set the inference backend.

        Args:
            backend (str): Backend name ("onnx" or "pytorch").

        Returns:
            bool: True if backend is valid, False otherwise.
        """
        if not isinstance(backend, str):
            logging.error("backend must be a string.")
            raise TypeError("backend must be a string.")
        backend = backend.lower()
        if backend in ("onnx", "pytorch"):
            self.backend = backend
            return True
        logging.error(f"Unsupported backend: {backend}")
        return False

# End of denoiser.py