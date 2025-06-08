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

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
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

5. **Run tests:**
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

---

## 🖥️ Usage

### GUI

- Launch with `python src/main.py`
- Intuitive interface for loading, denoising, and saving audio files
- Visualize waveforms and denoising results

### Command-Line

- Denoise audio:
  ```bash
  python src/denoiser.py --input noisy.wav --output clean.wav
  ```
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

- **Import errors:** Ensure your virtual environment is activated and dependencies are installed.
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

The Denoising Toolkit now supports a **Virtual Microphone** feature, allowing denoised audio to be routed to a system-level virtual audio input device. This enables you to use denoised audio in real-time with third-party applications (e.g., Zoom, Teams, Discord).

### Supported Platforms

- **Windows 10+** (user-mode virtual audio device, no manual driver install required)
- **macOS 12+** (CoreAudio virtual device, no manual third-party tools required)
- *Linux support coming soon*

### How It Works

- When you run the GUI or main application, a virtual microphone device is created and registered with your OS.
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

### Limitations

- The feature is in beta; some advanced audio routing scenarios may not be supported.
- Only one instance of the virtual microphone is supported at a time.

---