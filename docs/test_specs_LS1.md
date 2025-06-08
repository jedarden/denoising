# LS1 Test Specifications and Acceptance Criteria

## Overview

This document defines comprehensive test specifications for LS1, covering all modules:
- [`audio_io.py`](audio_io.py)
- [`denoiser.py`](denoiser.py)
- [`gui.py`](gui.py)
- [`main.py`](main.py)
- [`model_utils.py`](model_utils.py)

It includes edge cases, cross-platform/CPU-only requirements, and plans for test scaffolding and CI integration.

---

## 1. Audio I/O Module (`audio_io.py`)

### 1.1. Buffering and Real-Time Operation

- **Test: Buffer Size Handling**
  - Arrange: Initialize `AudioIO` with buffer_ms = 10, 20, 50.
  - Act: Start stream, feed synthetic audio.
  - Assert: Buffers are processed at correct intervals, no drift.

- **Test: Buffer Underrun**
  - Arrange: Simulate slow denoising callback.
  - Act: Observe buffer queue.
  - Assert: Underrun is detected and handled gracefully (no crash, warning issued).

- **Test: Buffer Overrun**
  - Arrange: Simulate fast input, slow output.
  - Act: Observe buffer queue.
  - Assert: Overrun is detected and handled gracefully.

- **Test: Silence Input**
  - Arrange: Feed all-zero (silent) audio buffer.
  - Act: Process through pipeline.
  - Assert: Output remains silent, no artifacts.

- **Test: High Noise Input**
  - Arrange: Feed buffer with high-amplitude white noise.
  - Act: Process through pipeline.
  - Assert: System remains stable, output is denoised or unchanged.

- **Test: Cross-Platform Device Enumeration**
  - Arrange: Run on Windows and OSX.
  - Act: Enumerate input/output devices.
  - Assert: All available devices are listed, selection works.

- **Test: Stream Start/Stop**
  - Arrange: Start and stop stream multiple times.
  - Act: Observe resource usage and state.
  - Assert: No resource leaks, state resets correctly.

---

## 2. Denoising Inference Module (`denoiser.py`)

### 2.1. Model Loading and Inference

- **Test: Model Load (ONNX/PyTorch)**
  - Arrange: Provide valid ONNX and PyTorch model files.
  - Act: Call `load_model()`.
  - Assert: Model loads without error, backend is respected.

- **Test: Model Load Failure**
  - Arrange: Provide invalid/corrupt model file.
  - Act: Call `load_model()`.
  - Assert: Error is raised and handled, no crash.

- **Test: Quantization**
  - Arrange: Load model, call `quantize_model()`.
  - Act: Run inference before and after quantization.
  - Assert: Output is similar, quantized model is used.

- **Test: Inference on Silence**
  - Arrange: Feed silent buffer.
  - Act: Run inference.
  - Assert: Output is silent, no artifacts.

- **Test: Inference on High Noise**
  - Arrange: Feed high-noise buffer.
  - Act: Run inference.
  - Assert: Output is denoised, no instability.

- **Test: Inference Latency**
  - Arrange: Feed buffer, measure time.
  - Act: Run inference.
  - Assert: Latency < buffer duration (e.g., <20ms for 20ms buffer).

- **Test: CPU-Only Operation**
  - Arrange: Run on system with no GPU.
  - Act: Load and run model.
  - Assert: No GPU/cloud dependencies, runs on CPU.

---

## 3. GUI Module (`gui.py`)

### 3.1. Responsiveness and Controls

- **Test: Start/Stop Button Functionality**
  - Arrange: Launch GUI, click Start/Stop.
  - Act: Observe audio stream and denoising state.
  - Assert: Stream starts/stops, UI updates accordingly.

- **Test: Device Selection**
  - Arrange: Multiple audio devices present.
  - Act: Select different input/output devices.
  - Assert: Selection is reflected in audio routing.

- **Test: Status Display**
  - Arrange: Trigger various states (idle, running, error).
  - Act: Observe status label.
  - Assert: Status updates correctly and promptly.

- **Test: GUI Latency**
  - Arrange: Start/stop stream, change settings.
  - Act: Measure UI response time.
  - Assert: UI responds within 100ms.

- **Test: Error Handling**
  - Arrange: Simulate device disconnect, model load failure.
  - Act: Observe GUI.
  - Assert: User is notified, app remains stable.

- **Test: Cross-Platform GUI**
  - Arrange: Run on Windows and OSX.
  - Act: Launch GUI, interact with controls.
  - Assert: Layout and controls function as expected.

---

## 4. Integration & System Tests (`main.py` and full stack)

### 4.1. End-to-End Audio Denoising

- **Test: Real-Time Pipeline**
  - Arrange: Connect microphone to input, speakers to output.
  - Act: Speak, observe output.
  - Assert: Audio is denoised in real time, minimal latency.

- **Test: Edge Case Audio (Silence, High Noise)**
  - Arrange: Feed silence, high noise, and normal speech.
  - Act: Observe output.
  - Assert: System remains stable, output is as expected.

- **Test: Resource Usage**
  - Arrange: Run app for extended period.
  - Act: Monitor CPU/memory.
  - Assert: No leaks, usage remains within acceptable bounds.

- **Test: No Cloud/GPU Dependency**
  - Arrange: Run on offline, CPU-only system.
  - Act: Use all features.
  - Assert: No cloud/GPU calls, all features work.

- **Test: Cross-Platform End-to-End**
  - Arrange: Run on Windows and OSX.
  - Act: Use all features.
  - Assert: All features work identically.

---

## 5. Model Utilities (`model_utils.py`)

### 5.1. Model Selection, Quantization, Conversion

- **Test: Model Selection**
  - Arrange: Call `select_model()` with supported/unsupported names.
  - Act: Observe return value or error.
  - Assert: Correct model or error is returned.

- **Test: Quantization Utility**
  - Arrange: Call `quantize_model()` on supported/unsupported models.
  - Act: Observe result.
  - Assert: Quantized model is returned or error is handled.

- **Test: ONNX Conversion**
  - Arrange: Call `convert_to_onnx()` with valid/invalid models.
  - Act: Observe output file and errors.
  - Assert: ONNX file is created or error is handled.

---

## 6. Edge Cases

- Silence, high noise, buffer underrun/overrun, device disconnect, model load failure, unsupported model, cross-platform quirks.

---

## 7. Acceptance Criteria

- **Cross-Platform:** All features must work on Windows and OSX (test on both).
- **CPU-Only:** No GPU or cloud dependencies; must run on CPU-only systems.
- **No Cloud/GPU:** All computation is local; no network or GPU required.
- **Real-Time:** End-to-end latency < 40ms for 20ms buffers.
- **Robustness:** Handles edge cases (silence, noise, underrun/overrun, device errors) gracefully.
- **GUI:** Responsive (<100ms), clear status, error reporting.
- **Resource Usage:** No memory leaks, stable CPU usage.
- **Test Coverage:** >90% line and branch coverage for all modules.
- **CI Integration:** All tests runnable via CI on Windows and OSX runners, CPU-only.

---

## 8. Test Scaffolding and CI Integration

- Use `pytest` for unit and integration tests.
- Use `pytest-qt` for GUI tests.
- Mock audio devices and model files for automated tests.
- Provide test audio samples (silence, noise, speech).
- Use GitHub Actions or similar CI with Windows and OSX runners.
- Collect and report coverage metrics.
- Document test setup and expected results.

---

## 9. Documentation

- Each test must include:
  - Purpose
  - Setup/teardown
  - Expected result
  - Edge cases covered
- Maintain this document as requirements evolve.

---