"""
Test suite for main.py

Covers:
- Canonical entry point (no duplicates)
- Application startup and shutdown (mocked)
- Error handling during startup (mocked)
- Integration with AudioIO, DenoisingInference, and DenoisingApp (mocked)

TDD: All tests initially fail to drive implementation.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

import pytest
import importlib

def test_single_main_function():
    """Test that only one main() function exists and is importable."""
    import main
    assert hasattr(main, "main")
    assert callable(main.main)

def test_entrypoint_runs(monkeypatch):
    """Test application startup and shutdown (mocked)."""
    import main
    # Mock dependencies
    monkeypatch.setattr(main, "AudioIO", lambda: "audio")
    monkeypatch.setattr(main, "DenoisingInference", lambda model_path, backend: "denoiser")
    class DummyApp:
        def __init__(self, audio, denoiser):
            self.audio = audio
            self.denoiser = denoiser
            self.shown = False
        def show(self):
            self.shown = True
            return True
    monkeypatch.setattr(main, "DenoisingApp", DummyApp)
    class DummyQApp:
        def __init__(self, argv):
            self.argv = argv
            self.exec_called = False
        def exec_(self):
            self.exec_called = True
            return 0
    monkeypatch.setattr(main, "QtWidgets", type("QtWidgets", (), {"QApplication": DummyQApp}))
    monkeypatch.setattr(main, "sys", type("sys", (), {"argv": []}))
    # Should not raise
    main.main()

def test_error_handling_on_startup(monkeypatch):
    """Test error handling during startup (mocked)."""
    import main
    monkeypatch.setattr(main, "AudioIO", lambda: (_ for _ in ()).throw(RuntimeError("AudioIO error")))
    with pytest.raises(RuntimeError):
        main.main()

def test_integration_with_modules(monkeypatch):
    """Test integration with AudioIO, DenoisingInference, and DenoisingApp (mocked)."""
    import main
    monkeypatch.setattr(main, "AudioIO", lambda: "audio")
    monkeypatch.setattr(main, "DenoisingInference", lambda model_path, backend: "denoiser")
    class DummyApp:
        def __init__(self, audio, denoiser): self.audio = audio; self.denoiser = denoiser
        def show(self): return True
    monkeypatch.setattr(main, "DenoisingApp", DummyApp)
    class DummyQApp:
        def __init__(self, argv):
            self.argv = argv
            self.exec_called = False
        def exec_(self):
            self.exec_called = True
            return 0
    monkeypatch.setattr(main, "QtWidgets", type("QtWidgets", (), {"QApplication": DummyQApp}))
    monkeypatch.setattr(main, "sys", type("sys", (), {"argv": []}))
    main.main()
@pytest.mark.usefixtures("monkeypatch")
def test_onnxruntime_install_attempt_and_logging(monkeypatch, caplog):
    """
    Test that the application attempts to install ONNX Runtime if missing and logs the outcome.
    """
    import main
    # Simulate ImportError for onnxruntime
    monkeypatch.setattr(main, "import_onnxruntime", lambda: (_ for _ in ()).throw(ImportError("No module named 'onnxruntime'")))
    install_attempted = []
    def fake_install_onnxruntime():
        install_attempted.append(True)
        return True
    monkeypatch.setattr(main, "install_onnxruntime", fake_install_onnxruntime)
    with caplog.at_level("INFO"):
        main.main()
    assert any("Attempting to install ONNX Runtime" in m for m in caplog.messages)
    assert install_attempted, "ONNX Runtime install was not attempted"
    assert any("ONNX Runtime installed successfully" in m or "Failed to install ONNX Runtime" in m for m in caplog.messages)

@pytest.mark.usefixtures("monkeypatch")
def test_virtual_microphone_dependency_resolution_and_logging(monkeypatch, caplog):
    """
    Test that the application attempts to resolve missing dependencies for VirtualMicrophoneService and logs all actions.
    """
    import main
    # Simulate ImportError for VirtualMicrophoneService dependency
    monkeypatch.setattr(main, "import_virtual_microphone", lambda: (_ for _ in ()).throw(ImportError("Missing dependency")))
    resolve_attempted = []
    def fake_resolve_dependencies():
        resolve_attempted.append(True)
        return True
    monkeypatch.setattr(main, "resolve_virtual_microphone_dependencies", fake_resolve_dependencies)
    with caplog.at_level("INFO"):
        main.main()
    assert any("Attempting to resolve VirtualMicrophoneService dependencies" in m for m in caplog.messages)
    assert resolve_attempted, "Dependency resolution was not attempted"
    assert any("Dependencies resolved" in m or "Failed to resolve dependencies" in m for m in caplog.messages)

@pytest.mark.usefixtures("monkeypatch")
def test_logs_actionable_errors_and_exits_on_unrecoverable_env_issue(monkeypatch, caplog):
    """
    Test that the application logs actionable errors and exits gracefully if unrecoverable environment issues occur.
    """
    import main
    # Simulate unrecoverable environment error
    def fake_check_env():
        raise RuntimeError("Unrecoverable environment error")
    monkeypatch.setattr(main, "check_environment", fake_check_env)
    with caplog.at_level("ERROR"), pytest.raises(SystemExit):
        main.main()
    assert any("Unrecoverable environment error" in m for m in caplog.messages)
    assert any("Exiting" in m for m in caplog.messages)

@pytest.mark.usefixtures("monkeypatch")
def test_startup_continues_if_env_issues_resolved(monkeypatch, caplog):
    """
    Test that the application continues to start if environment issues are resolved automatically.
    """
    import main
    # Simulate environment issue that is resolved on retry
    call_count = {"check": 0}
    def fake_check_env():
        if call_count["check"] == 0:
            call_count["check"] += 1
            raise RuntimeError("Temporary environment issue")
        return True
    monkeypatch.setattr(main, "check_environment", fake_check_env)
    # Mock rest of startup to prevent side effects
    monkeypatch.setattr(main, "AudioIO", lambda: "audio")
    monkeypatch.setattr(main, "DenoisingInference", lambda model_path, backend: "denoiser")
    class DummyApp:
        def __init__(self, audio, denoiser): self.audio = audio; self.denoiser = denoiser
        def show(self): return True
    monkeypatch.setattr(main, "DenoisingApp", DummyApp)
    class DummyQApp:
        def __init__(self, argv): self.argv = argv
        def exec_(self): return 0
    monkeypatch.setattr(main, "QtWidgets", type("QtWidgets", (), {"QApplication": DummyQApp}))
    monkeypatch.setattr(main, "sys", type("sys", (), {"argv": []}))
    with caplog.at_level("WARNING"):
        main.main()
    assert any("Temporary environment issue" in m for m in caplog.messages)
    assert any("Environment issue resolved" in m or "Continuing startup" in m for m in caplog.messages)