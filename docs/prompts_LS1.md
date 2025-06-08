## Prompt LS1_1

### Context
You are to architect a cross-platform (Windows/OSX) desktop application for real-time speech denoising on microphone input. The application must use efficient, open-source, CPU-only AI models (no GPU or cloud). Prioritize Tiny Recurrent U-Net (TRU-Net), SpeechDenoiser, and other quantized/causal models for real-time CPU inference. Model deployment should use ONNX or PyTorch, ensuring compatibility with both C++ and Python. The GUI and real-time audio I/O should use JUCE (C++), Qt (C++/Python), or PyQt (Python). PortAudio (or PyAudio) is recommended for low-latency, cross-platform audio input/output. The app must process audio in small buffers (10–20 ms) for minimal latency. Enforce modularity, file size limits (<500 lines/module), no hard-coded secrets, and TDD for all features.

### Task
Design a high-level architecture diagram and module breakdown for the application, clearly separating audio I/O, denoising inference, and GUI components. Specify the responsibilities and interfaces for each module.

### Requirements
- Modular separation: audio I/O, denoising inference, GUI
- Cross-platform (Windows/OSX) compatibility
- Use of efficient, open-source, CPU-only AI models (TRU-Net, SpeechDenoiser, etc.)
- Model deployment via ONNX or PyTorch
- GUI and audio I/O via JUCE, Qt, or PyQt; audio via PortAudio/PyAudio
- Audio processed in 10–20 ms buffers
- File size limit: <500 lines/module
- No hard-coded secrets
- TDD for all features

### Previous Issues
None (first layer).

### Expected Output
A high-level architecture diagram (text or mermaid), a list of modules with responsibilities, and a description of module interfaces.

---

## Prompt LS1_2

### Context
The application must perform real-time speech denoising using efficient, open-source, CPU-only AI models. Prioritize Tiny Recurrent U-Net (TRU-Net), SpeechDenoiser, and other quantized/causal models. Model deployment should use ONNX or PyTorch, and the solution must be compatible with both C++ and Python.

### Task
Propose a strategy for selecting, quantizing, and integrating AI models for real-time CPU inference. Detail how to convert models to ONNX or quantized PyTorch, and how to ensure compatibility with both C++ and Python runtimes.

### Requirements
- Prioritize TRU-Net, SpeechDenoiser, and similar models
- Quantize models for CPU efficiency
- Convert models to ONNX or quantized PyTorch
- Ensure C++ and Python compatibility for inference
- Document model selection, conversion, and integration steps
- No GPU or cloud dependencies

### Previous Issues
None (first layer).

### Expected Output
A step-by-step strategy for model selection, quantization, conversion, and integration, including code snippets or commands for each step.

---

## Prompt LS1_3

### Context
The application requires low-latency, cross-platform audio input/output for real-time processing. PortAudio (C++/Python) or PyAudio (Python) are recommended for this purpose. The system must process audio in small buffers (10–20 ms) to minimize latency.

### Task
Design the audio I/O module, specifying how to capture microphone input, process audio in small buffers, and output denoised audio in real time. Define the API for this module and describe how it will interface with the denoising inference module.

### Requirements
- Use PortAudio (C++/Python) or PyAudio (Python) for audio I/O
- Support 10–20 ms buffer sizes for minimal latency
- Cross-platform (Windows/OSX) support
- Clean API for integration with denoising inference
- Modular design, <500 lines/module
- TDD for all features

### Previous Issues
None (first layer).

### Expected Output
A detailed module design, including API signatures, buffer management strategy, and integration points with the inference module.

---

## Prompt LS1_4

### Context
The application must provide a responsive, cross-platform desktop GUI for controlling real-time speech denoising. Frameworks to consider include JUCE (C++), Qt (C++/Python), and PyQt (Python). The GUI should allow users to select input/output devices, adjust denoising parameters, and monitor audio levels in real time.

### Task
Design the GUI module, specifying the framework, main UI components, and event handling strategy. Define how the GUI will communicate with the audio I/O and denoising inference modules.

### Requirements
- Use JUCE, Qt, or PyQt for GUI
- Cross-platform (Windows/OSX) support
- Real-time device selection, parameter adjustment, and audio monitoring
- Modular design, <500 lines/module
- No hard-coded secrets
- TDD for all features

### Previous Issues
None (first layer).

### Expected Output
A detailed GUI module design, including framework choice, UI component breakdown, event flow, and integration points with other modules.

---

## Prompt LS1_5

### Context
The project enforces strict modularity, file size limits (<500 lines/module), no hard-coded secrets, and test-driven development (TDD) for all features. The application must be easy to test, maintain, and extend.

### Task
Define a TDD and CI strategy for the project. Specify how to scaffold tests for each module, enforce file size and code quality limits, and set up continuous integration for cross-platform builds and tests.

### Requirements
- TDD for all modules (audio I/O, inference, GUI)
- Test scaffolding for C++ and/or Python
- Enforce <500 lines/module and code quality checks
- CI setup for Windows/OSX builds and tests
- No hard-coded secrets in code or tests

### Previous Issues
None (first layer).

### Expected Output
A TDD and CI plan, including test scaffolding examples, code quality enforcement strategy, and CI configuration outline.

---

## Prompt LS1_6

### Context
The application must be packaged for easy installation and use on both Windows and OSX. The packaging process should include all dependencies, ensure cross-platform compatibility, and avoid reliance on GPU or cloud services.

### Task
Propose a cross-platform packaging and distribution strategy for the application. Specify tools and steps for packaging C++ and/or Python applications with all dependencies, and describe how to automate the process in CI.

### Requirements
- Cross-platform packaging (Windows/OSX)
- Include all dependencies (audio, GUI, model inference)
- No GPU or cloud dependencies
- Automate packaging in CI
- Clear installation instructions for end users

### Previous Issues
None (first layer).

### Expected Output
A packaging and distribution plan, including tool recommendations, automation steps, and sample installation instructions.