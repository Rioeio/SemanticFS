from __future__ import annotations

import socket
import threading

from semanticfs.doctor import (
    get_cargo_path,
    get_tesseract_path,
    is_daemon_reachable,
    is_startup_daemon_installed,
    run_environment_doctor,
)


def test_daemon_reachable_offline():
    assert is_daemon_reachable(port=59999, host="127.0.0.1", timeout=0.2) is False


def test_daemon_reachable_online():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind(("127.0.0.1", 0))
    srv.listen(1)
    assigned_port = srv.getsockname()[1]

    running = True

    def _accept():
        while running:
            try:
                conn, _ = srv.accept()
                conn.close()
            except Exception:
                break

    t = threading.Thread(target=_accept, daemon=True)
    t.start()

    try:
        assert is_daemon_reachable(port=assigned_port, host="127.0.0.1", timeout=1.0) is True
    finally:
        running = False
        srv.close()


def test_is_startup_daemon_installed(tmp_path, monkeypatch):
    monkeypatch.setenv("APPDATA", str(tmp_path))
    startup_dir = tmp_path / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
    startup_dir.mkdir(parents=True, exist_ok=True)
    vbs_file = startup_dir / "SemanticFS_Daemon.vbs"

    assert is_startup_daemon_installed() is False

    vbs_file.write_text("' dummy vbs script")
    assert is_startup_daemon_installed() is True


def test_run_environment_doctor():
    result = run_environment_doctor()
    assert isinstance(result, bool)


def test_binary_helpers():
    tess = get_tesseract_path()
    assert tess is None or isinstance(tess, str)

    cargo = get_cargo_path()
    assert cargo is None or isinstance(cargo, str)
