"""
Test suite for main.py

Covers:
- Canonical entry point (no duplicates)
- Application startup and shutdown (mocked)
- Error handling during startup (mocked)
- Integration with AudioIO, DenoisingInference, and DenoisingApp (mocked)

TDD: All tests initially fail to drive implementation.
"""
def test_main_entrypoint_no_syntax_error(monkeypatch):
    """
    Smoke test: Import and run main.main() to ensure no syntax errors or immediate exceptions.
    Mocks dependencies to avoid side effects.
    """
    import main
    # Mock dependencies to prevent actual execution
    monkeypatch.setattr(main, "AudioIO", lambda *args, **kwargs: "audio")
    monkeypatch.setattr(main, "DenoisingInference", lambda model_path: "denoiser")
    class DummyApp:
        def __init__(self, audio, denoiser):
            self.audio = audio
            self.denoiser = denoiser
        def show(self):
            return True
    monkeypatch.setattr(main, "DenoisingApp", DummyApp)
    class DummyQApp:
        def __init__(self, *args, **kwargs): pass
        def exec_(self): return 0
    monkeypatch.setattr(main, "QApplication", DummyQApp)
    # Patch sys.argv to minimal valid args
    monkeypatch.setattr(main.sys, "argv", ["main.py", "--model", "dummy_model.pth"])
    # Patch ensure_model_exists to no-op
    monkeypatch.setattr(main, "ensure_model_exists", lambda model, url: None)
    # Patch parse_args to return a dummy args object
    class DummyArgs:
        model = "dummy_model.pth"
        sample_rate = 16000
    monkeypatch.setattr(main, "parse_args", lambda argv: DummyArgs())
    # Should not raise any exceptions
    main.main()
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
    monkeypatch.setattr(main, "AudioIO", lambda *args, **kwargs: "audio")
    monkeypatch.setattr(main, "DenoisingInference", lambda model_path: "denoiser")
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
    monkeypatch.setattr(main, "AudioIO", lambda *args, **kwargs: "audio")
    monkeypatch.setattr(main, "DenoisingInference", lambda model_path: "denoiser")
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
# (Removed obsolete ONNX Runtime and dependency resolution tests)
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