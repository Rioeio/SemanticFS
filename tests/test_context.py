from __future__ import annotations

from semanticfs.context import ContextCapture

def test_capture():
    # Because of CI/headless environments, this might fail or return mock data.
    # We just ensure it runs and returns a valid object structure.
    capture = ContextCapture()
    snapshot = capture.capture()
    
    assert hasattr(snapshot, "active_window")
    assert hasattr(snapshot, "time_bucket")
    assert isinstance(snapshot.running_processes, list)
    
    text = snapshot.to_text()
    assert isinstance(text, str)
    assert "Time:" in text
