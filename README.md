# Denoising Toolkit

A modular, research-driven Python toolkit for audio denoising, featuring a cross-platform GUI, robust model utilities, and comprehensive test coverage. Designed for rapid experimentation, reproducibility, and extensibility in speech and audio enhancement tasks.

---

## 🚀 Quickstart

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/denoising.git
   cd denoising
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install all dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    > **Note:** PyTorch (`torch`) is required for model inference.
    > Only PyTorch models (`.pth`, `.jit`, `.ckpt`) are supported. ONNX and ONNX Runtime are **not** supported.

4. **Select and download a pre-trained model:**
    - By default, the application will use the **Silero Denoiser** model and auto-download it if missing.
    - You can select an alternative model using the `--model-name` argument (see below).
    - To use a custom model file, provide the `--model` argument with the path to your model.

---

## 🎤 Supported Pre-trained Models

| Model Name         | CLI Value           | Download Link                                                                 | Default Path                   | Notes                                      |
|--------------------|--------------------|-------------------------------------------------------------------------------|--------------------------------|--------------------------------------------|
| Silero Denoiser    | `silero`           | [Silero Denoiser (.jit)](https://github.com/snakers4/silero-models/releases/download/v0.4.0/denoiser.jit) | `models/silero-denoiser.jit`   | Fast, robust, widely used                  |
| Facebook Denoiser  | `facebook-denoiser`| [Facebook Denoiser (.pth)](https://dl.fbaipublicfiles.com/denoiser/denoiser.pth) | `models/facebook-denoiser.pth` | Official Facebook Denoiser                 |
| DCUNet (SpeechBrain)| `dcunet`          | [DCUNet 16kHz (.ckpt)](https://github.com/speechbrain/speechbrain/releases/download/v0.5.12/dc_unet_16kHz_pretrained.ckpt) | `models/dcunet-16khz.ckpt`     | From SpeechBrain, for speech enhancement   |

- The model will be auto-downloaded to the default path on first run if not present.
- To use a different model, specify `--model-name` (see below).
- To use a custom model file, specify `--model /path/to/model`.

---

## 🛠️ Model Selection & Usage

- **Default (Silero):**
  ```bash
  python -m src.main
  ```
- **Select Facebook Denoiser:**
  ```bash
  python -m src.main --model-name facebook-denoiser
  ```
- **Select DCUNet:**
  ```bash
  python -m src.main --model-name dcunet
  ```
- **Use a custom model file:**
  ```bash
  python -m src.main --model /path/to/your_model.pth
  ```

- The application will attempt to auto-download the selected model if it is missing.
- If the automatic download fails (e.g., due to network/firewall issues), manually download the model from the link above and place it at the default path (or your custom path).

  Example for Silero:
  ```bash
  mkdir -p models
  wget https://github.com/snakers4/silero-models/releases/download/v0.4.0/denoiser.jit -O models/silero-denoiser.jit
  ```

---

- **Platform-specific requirements for Virtual Microphone:**
  - The Virtual Microphone feature is only supported on **Windows 10+** and **macOS 12+**.
  - On first use, you may be prompted for admin/system permissions to install a virtual audio device or system extension.
  - No manual installation of third-party tools is required; all components are bundled or installed programmatically.
  - **Linux is not currently supported for the virtual microphone.**

5. **Run the application:**
   - **GUI:**
     You can run the GUI application in either of the following ways:
     - As a module (recommended, ensures correct imports):
       ```bash
       python -m src.main
       ```
     - Or, by setting the `PYTHONPATH` so Python treats `src/` as a package:
       ```bash
       PYTHONPATH=. python src/main.py
       ```
     > **Note:** Directly running `python src/main.py` without setting `PYTHONPATH` will result in an import error due to Python's package import rules. Using the `-m` flag or setting `PYTHONPATH` ensures absolute imports work correctly.
   - **Command-line (example):**
     ```bash
     python src/denoiser.py --input noisy.wav --output clean.wav
     ```

6. **Run tests:**
   ```bash
   pytest tests/
   ```

---

## 📦 Installation

- **Python 3.8+ required**
- Recommended: Use a virtual environment (`.venv`)
- Install dependencies with `pip install -r requirements.txt`
- For development, install test and linting tools:
  ```bash
  pip install pytest coverage mypy flake8
  ```
- **PyTorch is required for all model inference. Only `.pth` models are supported.**
- **No manual model download is required for the default configuration. The Silero Denoiser model will be auto-downloaded to `models/silero-denoiser.pth` on first run if not present.**

---

## 🖥️ Usage

### GUI

- Launch with `python -m src.main` (recommended) or set `PYTHONPATH=. python src/main.py`
- Intuitive interface for loading, denoising, and saving audio files
- Visualize waveforms and denoising results
- **On first run, the Silero Denoiser model will be auto-downloaded to `models/silero-denoiser.pth` if not already present.**

### Command-Line

- Denoise audio:
  ```bash
  python src/denoiser.py --input noisy.wav --output clean.wav
  ```
  - The model will be auto-downloaded if missing.
- See all options:
  ```bash
  python src/denoiser.py --help
  ```

---

## 🛠️ Development Workflow

- **Test-Driven Development (TDD):** All modules are covered by unit tests. Write tests before implementing new features.
- **Modular Design:** Each module has a single responsibility. Extend functionality by adding new modules and tests.
- **Continuous Integration:** Use `pytest` and `coverage` to ensure code quality.
- **Documentation:** Update `README.md` and module docstrings for all changes.

### Running Tests

```bash
pytest tests/
coverage run -m pytest tests/
coverage report
```

### Linting & Type Checking

```bash
flake8 src/ tests/
mypy src/
```

---

## 🧩 Project Structure

- `src/main.py` — Application entry point (GUI)
- `src/denoiser.py` — Core denoising logic
- `src/audio_io.py` — Audio file I/O utilities
- `src/model_utils.py` — Model loading and utility functions
- `src/gui.py` — GUI components
- `src/virtual_microphone.py` — Virtual Microphone feature
- `tests/` — Unit tests for each module (e.g., `tests/test_denoiser.py`)
- `research/` — Reference papers and supporting materials
- `docs/` — Specifications, prompts, and documentation

---

## 🧪 Troubleshooting

- **Import errors:** Ensure your virtual environment is activated and all dependencies are installed.
- **Model not found:** If you see errors about a missing model file, ensure you have internet access on first run so the Silero Denoiser model can be auto-downloaded. The model will be saved to `models/silero-denoiser.pth` by default.
- **PyTorch not installed:** If you see `ModuleNotFoundError: No module named 'torch'`, install PyTorch with `pip install torch`.
- **"VirtualMicrophoneService is not defined" or NotImplementedError:**
  - This error occurs if you attempt to use the Virtual Microphone feature on an unsupported platform (e.g., Linux) or if the backend is not yet implemented for your OS.
  - The Virtual Microphone is only available on Windows 10+ and macOS 12+.
  - If you see `NotImplementedError: Virtual microphone is only supported on Windows and macOS.` or `NotImplementedError: <platform> virtual microphone backend not yet implemented.`, this is expected on unsupported platforms or while the feature is in beta.

- **Audio file issues:** Supported formats are WAV/PCM. For others, convert using `ffmpeg`.
- **GUI not launching:** Check for missing GUI dependencies (e.g., PyQt5, Tkinter).
- **Test failures:** Run `pytest -v` for detailed output. Check for missing test dependencies.
- **Permission errors:** Avoid running as root. Ensure you have read/write access to audio files.

---

## 🤝 Contributing

- Fork the repo and create a feature branch.
- Write tests for new features or bugfixes.
- Ensure all tests pass and code is linted.
- Submit a pull request with a clear description.

---

## 📚 Research & References

See the `research/` directory for foundational papers and inspiration. Contributions of new research or implementation of novel denoising methods are welcome!

---

## 📝 License

[MIT License](LICENSE)
---

## 🎤 Virtual Microphone Feature (Beta)

The Denoising Toolkit includes a **Virtual Microphone** feature, allowing denoised audio to be routed to a system-level virtual audio input device. This enables you to use denoised audio in real-time with third-party applications (e.g., Zoom, Teams, Discord).

### Supported Platforms

- **Windows 10+** (user-mode virtual audio device, no manual driver install required)
- **macOS 12+** (CoreAudio virtual device, no manual third-party tools required)
- **Linux is not supported** (feature will raise `NotImplementedError`)

### How It Works

- When you run the GUI or main application, a virtual microphone device is created and registered with your OS (if supported).
- Denoised audio is streamed to this device in real time.
- In your communication app, select "Denoising Virtual Microphone" (or similar) as your input device.

### Usage

1. **Run the application as usual:**
   ```bash
   python src/main.py
   ```
2. **Select the virtual microphone in your target app's audio settings.**
3. **Denoised audio will be routed automatically.**

### Permissions & Security

- On first use, you may be prompted for admin/system permissions to install a virtual audio device or system extension.
- No manual installation of third-party tools is required; all components are bundled or installed programmatically.

### Troubleshooting

- If the virtual microphone does not appear:
  - Ensure you have granted all required permissions.
  - Restart your system if prompted after installation.
  - Check the application logs for errors related to the virtual microphone.
- If you encounter issues, disable the feature by running with the `--no-virtual-mic` flag (if available).
- If you see `NotImplementedError` related to the virtual microphone, check your OS support (see above).

### Limitations

- The feature is in beta; some advanced audio routing scenarios may not be supported.
- Only one instance of the virtual microphone is supported at a time.
- The backend implementation for Windows and macOS is in progress; you may see `NotImplementedError` until full support is released.

---
---

## 🔊 Virtual Microphone: Troubleshooting "Failed to initialize VirtualMicrophoneService"

If you encounter the error message:

```
Failed to initialize VirtualMicrophoneService
```

in the application logs or console output, it means the virtual microphone feature could not be started. This feature is currently **beta** and only supported on **Windows 10+** and **macOS 12+**. Linux is not supported.

### Common Causes

- **Missing dependencies**: Required system libraries or drivers are not installed.
- **Insufficient permissions**: The application lacks admin or system-level permissions to install or access virtual audio devices.
- **Platform limitations**: The feature is not available on your OS version or hardware.
- **Incomplete installation**: The virtual audio driver or system extension was not installed correctly, or the installation was interrupted.
- **Antivirus or security software**: Security tools may block driver installation or access.

### How to Resolve

#### Windows

1. **Run as Administrator**  
   Right-click the application or your terminal and select "Run as administrator" to grant necessary permissions.

2. **Check for Driver Prompts**  
   On first use, Windows may prompt you to allow installation of a virtual audio device. Accept all prompts.

3. **Verify Driver Installation**  
   - Open Device Manager and look for a "Virtual Audio Device" under "Sound, video and game controllers".
   - If missing, restart the application as administrator.

4. **Temporarily Disable Antivirus/Security Software**  
   Some security tools may block driver installation. Temporarily disable them and try again.

5. **Check Windows Version**  
   Ensure you are running Windows 10 or newer.

6. **Review Log Output**  
   Check the application logs for lines containing `VirtualMicrophoneService` for more details.

#### macOS

1. **Grant Microphone and System Extension Permissions**  
   - On first use, macOS may prompt for microphone access and to allow a system extension.
   - Go to **System Settings > Privacy & Security** and approve any pending requests for the app or virtual audio device.

2. **Restart After Granting Permissions**  
   After approving permissions or system extensions, restart your Mac and the application.

3. **Check macOS Version**  
   Ensure you are running macOS 12 (Monterey) or newer.

4. **Review Log Output**  
   Look for lines containing `VirtualMicrophoneService` in the application logs for more details.

5. **Check for Third-Party Conflicts**  
   Audio routing tools (e.g., Loopback, BlackHole) may interfere. Try disabling them temporarily.

### Beta Status and Limitations

- The virtual microphone feature is **beta** and may not work on all systems.
- Only one virtual microphone instance can be active at a time.
- Some hardware configurations or enterprise-managed devices may block virtual audio drivers.
- If you continue to experience issues, please report them with your OS version and relevant log output.