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

from src.model_utils import select_model, quantize_model, load_pytorch_model

class DenoisingInference:
    """
    Loads and runs efficient, CPU-only denoising models (PyTorch only).
    """

    def __init__(self, model_path: str, min_input_length: int = 64):
        """
        Initialize the denoising model.

        Args:
            model_path (str): Path to the PyTorch model file.
            min_input_length (int): Minimum input length required for the model (for padding).
        """
        if not isinstance(model_path, str):
            raise TypeError("model_path must be a string.")
        self.model_path = model_path
        self.model = None
        self._quantized = False
        self.device = "cpu"
        self.loaded = False
        self.min_input_length = min_input_length
        self.required_pad_sum = 0  # Will be set after model load
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
            self.model = load_pytorch_model(self.model_path, logger=logging)
            self.model.eval()
            self.loaded = True
            # Scan for ReflectionPad1d layers and compute required_pad_sum
            self.required_pad_sum = 0
            if hasattr(self.model, "modules"):
                try:
                    for m in self.model.modules():
                        if hasattr(torch.nn, "ReflectionPad1d") and isinstance(m, torch.nn.ReflectionPad1d):
                            pad = m.padding
                            # pad can be int or tuple
                            if isinstance(pad, int):
                                pad_sum = pad * 2
                            elif isinstance(pad, (tuple, list)):
                                pad_sum = sum(pad)
                            else:
                                pad_sum = 0
                            if pad_sum > self.required_pad_sum:
                                self.required_pad_sum = pad_sum
                except Exception as e:
                    logging.warning(f"Could not determine ReflectionPad1d padding: {e}")
            logging.info(f"Model loaded. Required ReflectionPad1d pad sum: {self.required_pad_sum}")
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

    def process_buffer(self, audio_buffer: np.ndarray) -> tuple:
        """
        Run denoising inference on a single audio buffer.

        Args:
            audio_buffer (np.ndarray): Input audio buffer.

        Returns:
            tuple: (output_audio: np.ndarray, bypassed: bool)
                output_audio: Denoised audio buffer or raw audio if bypassed.
                bypassed: True if denoising was skipped due to short input, False otherwise.

        Raises:
            RuntimeError: If model is not loaded or input is invalid.
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
        # 1. If extremely short, bypass and return raw audio (legacy behavior)
        if len(audio_buffer) < 2:
            logging.warning(f"Input audio buffer too short to pad safely (len={len(audio_buffer)}). Denoising bypassed, returning raw audio.")
            return audio_buffer, True
        # 2. If input is too short for ReflectionPad1d, pad to max(min_input_length, required_pad_sum+1)
        elif self.required_pad_sum > 0 and len(audio_buffer) <= self.required_pad_sum:
            min_required = max(self.min_input_length, self.required_pad_sum + 1)
            pad_len = min_required - len(audio_buffer)
            audio_buffer = np.pad(audio_buffer, (0, pad_len), mode="constant")
            logging.warning(
                f"Input audio buffer too short for ReflectionPad1d (len={len(audio_buffer)} <= pad_sum={self.required_pad_sum}). "
                f"Padded with zeros to {min_required} samples to avoid ReflectionPad1d error."
            )
        # 3. If input is short but can be padded (legacy min_input_length logic)
        elif len(audio_buffer) < self.min_input_length:
            pad_len = self.min_input_length - len(audio_buffer)
            if len(audio_buffer) > 1:
                audio_buffer = np.pad(audio_buffer, (0, pad_len), mode="reflect")
            else:
                audio_buffer = np.pad(audio_buffer, (0, pad_len), mode="constant")
            logging.warning(f"Input audio buffer too short (len={len(audio_buffer)-pad_len}), padded to {self.min_input_length} samples.")

        try:
            with torch.no_grad():
                input_tensor = torch.from_numpy(audio_buffer).float().unsqueeze(0)
                output_tensor = self.model(input_tensor)
                return output_tensor.squeeze(0).cpu().numpy(), False
        except Exception as e:
            logging.error(f"PyTorch inference failed: {e}")
            raise RuntimeError(f"PyTorch inference failed: {e} (input length: {len(audio_buffer)})")
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