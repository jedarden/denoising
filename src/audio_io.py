"""
audio_io.py

Handles real-time, cross-platform audio input/output using PyAudio.
- Captures microphone input in small buffers (10–20 ms)
- Outputs denoised audio in real time
- Enumerates audio devices
- Handles buffer underrun/overrun, silence, and high noise
- Designed for CPU-only, offline operation

Author: aiGI Auto-Coder
"""

import logging
import platform
from typing import Callable, List, Optional

try:
    import pyaudio
except ImportError:
    pyaudio = None

class AudioIO:
    """
    Cross-platform, real-time audio I/O interface for speech denoising.
    """

    def __init__(
        self,
        sample_rate: int = 16000,
        buffer_ms: int = 20,
        channels: int = 1,
        input_device: Optional[int] = None,
        output_device: Optional[int] = None,
        virtual_microphone_service=None,
    ):
        """
        Initialize AudioIO with stream parameters and device selection.

        Args:
            sample_rate (int): Audio sample rate in Hz.
            buffer_ms (int): Buffer size in milliseconds.
            channels (int): Number of audio channels.
            input_device (Optional[int]): Input device index.
            output_device (Optional[int]): Output device index.
        """
        if pyaudio is None:
            logging.error("PyAudio is not installed.")
            raise ImportError("PyAudio is not installed.")
        if not isinstance(sample_rate, int) or sample_rate <= 0:
            raise ValueError("sample_rate must be a positive integer.")
        if not isinstance(buffer_ms, int) or buffer_ms <= 0:
            raise ValueError("buffer_ms must be a positive integer.")
        if not isinstance(channels, int) or channels <= 0:
            raise ValueError("channels must be a positive integer.")
        if input_device is not None and not isinstance(input_device, int):
            raise TypeError("input_device must be an integer or None.")
        if output_device is not None and not isinstance(output_device, int):
            raise TypeError("output_device must be an integer or None.")

        self.sample_rate = sample_rate
        self.buffer_ms = buffer_ms
        self.channels = channels
        self.input_device = input_device
        self.output_device = output_device
        self._pyaudio = pyaudio.PyAudio()
        self._stream = None
        self._callback = None
        self._virtual_microphone_service = virtual_microphone_service

    def enumerate_devices(self) -> List[dict]:
        """
        List available audio input/output devices.

        Returns:
            List[dict]: List of device info dicts.
        """
        devices = []
        try:
            count = self._pyaudio.get_device_count()
            for i in range(count):
                info = self._pyaudio.get_device_info_by_index(i)
                devices.append({
                    "id": i,
                    "name": info.get("name", f"Device {i}"),
                    "maxInputChannels": info.get("maxInputChannels", 0),
                    "maxOutputChannels": info.get("maxOutputChannels", 0),
                    "defaultSampleRate": info.get("defaultSampleRate", 0),
                })
        except Exception as e:
            logging.error(f"Failed to enumerate devices: {e}")
            raise RuntimeError(f"Failed to enumerate devices: {e}")
        return devices

    def select_device(self, device_id: int) -> bool:
        """
        Select an audio device by ID.

        Args:
            device_id (int): Device index.

        Returns:
            bool: True if device is valid and selected, False otherwise.
        """
        if not isinstance(device_id, int) or device_id < 0:
            logging.error("device_id must be a non-negative integer.")
            raise ValueError("device_id must be a non-negative integer.")
        try:
            info = self._pyaudio.get_device_info_by_index(device_id)
            self.input_device = device_id
            return True
        except Exception as e:
            logging.error(f"Failed to select device {device_id}: {e}")
            return False

    def set_sample_rate(self, sample_rate: int) -> bool:
        """
        Set the audio sample rate.

        Args:
            sample_rate (int): New sample rate in Hz.

        Returns:
            bool: True if valid, False otherwise.
        """
        if not isinstance(sample_rate, int) or sample_rate <= 0:
            logging.error("sample_rate must be a positive integer.")
            return False
        self.sample_rate = sample_rate
        return True

    def is_cpu_only(self) -> bool:
        """
        Check if the implementation is CPU-only (no GPU/accelerator).

        Returns:
            bool: Always True for this implementation.
        """
        return True

    def start_stream(self, callback: Callable[[bytes], bytes]) -> bool:
        """
        Start real-time audio stream.

        Args:
            callback (Callable[[bytes], bytes]): Function to process input buffer and return output buffer.

        Returns:
            bool: True if stream started successfully.
        """
        if not callable(callback):
            logging.error("callback must be callable.")
            raise TypeError("callback must be callable.")
        self._callback = callback
        try:
            buffer_size = int(self.sample_rate * self.buffer_ms / 1000)
            self._stream = self._pyaudio.open(
                format=pyaudio.paInt16,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                output=True,
                input_device_index=self.input_device,
                output_device_index=self.output_device,
                frames_per_buffer=buffer_size,
                stream_callback=self._internal_callback,
            )
            self._stream.start_stream()
            return True
        except Exception as e:
            logging.error(f"Failed to start stream: {e}")
            return False

    def _internal_callback(self, in_data, frame_count, time_info, status):
        """
        Internal callback for PyAudio stream.
        """
        try:
            if self._callback is not None:
                out_data = self._callback(in_data)
            else:
                out_data = in_data
            # Route denoised audio to virtual microphone if enabled
            if self._virtual_microphone_service is not None:
                try:
                    self._virtual_microphone_service.stream_audio_frame(out_data)
                except Exception as vm_exc:
                    logging.error(f"Error streaming to virtual microphone: {vm_exc}")
        except Exception as e:
            logging.error(f"Error in audio callback: {e}")
            out_data = in_data
        return (out_data, pyaudio.paContinue)

    def stop_stream(self) -> bool:
        """
        Stop the real-time audio stream.

        Returns:
            bool: True if stream stopped successfully.
        """
        try:
            if self._stream is not None:
                self._stream.stop_stream()
                self._stream.close()
                self._stream = None
            return True
        except Exception as e:
            logging.error(f"Failed to stop stream: {e}")
            return False

    def __del__(self):
        try:
            if self._stream is not None:
                self._stream.stop_stream()
                self._stream.close()
            if hasattr(self, "_pyaudio") and self._pyaudio is not None:
                self._pyaudio.terminate()
        except Exception as e:
            logging.error(f"Exception during AudioIO cleanup: {e}")

# End of audio_io.py