"""
Test suite for main.py

Covers:
- Canonical entry point (no duplicates)
- Application startup and shutdown (mocked)
- Error handling during startup (mocked)
- Integration with AudioIO, DenoisingInference, and DenoisingApp (mocked)

TDD: All tests initially fail to drive implementation.
"""

import pytest
import importlib

def test_single_main_function():
    """Test that only one main() function exists and is importable."""
    import src.main as main
    assert hasattr(main, "main")
    assert callable(main.main)

def test_entrypoint_runs(monkeypatch):
    """Test application startup and shutdown (mocked)."""
    import src.main as main
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
    import src.main as main
    monkeypatch.setattr(main, "AudioIO", lambda: (_ for _ in ()).throw(RuntimeError("AudioIO error")))
    with pytest.raises(RuntimeError):
        main.main()

def test_integration_with_modules(monkeypatch):
    """Test integration with AudioIO, DenoisingInference, and DenoisingApp (mocked)."""
    import src.main as main
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