from __future__ import annotations

from unittest.mock import patch, MagicMock
from semanticfs.config import Config, UIConfig
from semanticfs.daemon import DaemonContext


def test_ui_config_defaults():
    ui_cfg = UIConfig()
    assert ui_cfg.enabled is False


def test_config_loads_ui_section(tmp_path):
    cfg_file = tmp_path / "test_config.yaml"
    cfg_file.write_text("ui:\n  enabled: true\n", encoding="utf-8")
    loaded = Config._load(cfg_file)
    assert loaded.ui.enabled is True

    cfg_file_disabled = tmp_path / "test_config_disabled.yaml"
    cfg_file_disabled.write_text("ui:\n  enabled: false\n", encoding="utf-8")
    loaded_disabled = Config._load(cfg_file_disabled)
    assert loaded_disabled.ui.enabled is False


def test_default_config_yaml_ui_disabled():
    from semanticfs.config import DEFAULT_CONFIG_PATH
    loaded = Config._load(DEFAULT_CONFIG_PATH)
    assert loaded.ui.enabled is False


def test_daemon_ui_server_opt_in():
    # Test when ui.enabled is False
    config = Config()
    config.ui.enabled = False

    with patch("semanticfs.daemon.Embedder"), \
         patch("semanticfs.daemon.VectorStore"), \
         patch("semanticfs.daemon.FileLinker"), \
         patch("semanticfs.daemon.FileWatcher"), \
         patch("semanticfs.daemon.get_or_create_auth_token", return_value="token"), \
         patch("semanticfs.ui_server.start_ui_server") as mock_start_ui:

        daemon_ctx = DaemonContext(config)
        daemon_ctx.start_ipc_server = MagicMock()
        daemon_ctx.initial_scan = MagicMock()

        # Stop loop immediately
        daemon_ctx._running = False
        daemon_ctx.run()

        mock_start_ui.assert_not_called()

    # Test when ui.enabled is True
    config.ui.enabled = True
    with patch("semanticfs.daemon.Embedder"), \
         patch("semanticfs.daemon.VectorStore"), \
         patch("semanticfs.daemon.FileLinker"), \
         patch("semanticfs.daemon.FileWatcher"), \
         patch("semanticfs.daemon.get_or_create_auth_token", return_value="token"), \
         patch("semanticfs.ui_server.start_ui_server") as mock_start_ui:

        daemon_ctx = DaemonContext(config)
        daemon_ctx.start_ipc_server = MagicMock()
        daemon_ctx.initial_scan = MagicMock()

        daemon_ctx._running = False
        daemon_ctx.run()

        mock_start_ui.assert_called_once_with(port=9877)
