from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import psutil
import pygetwindow as gw

logger = logging.getLogger(__name__)

@dataclass
class ContextSnapshot:
    active_window: str
    active_process: str
    running_processes: list[str]
    timestamp: datetime
    time_bucket: str
    day_of_week: str

    def to_text(self) -> str:
        """Human-readable summary for embedding."""
        return (f"Time: {self.time_bucket} on {self.day_of_week}. "
                f"Active Window: {self.active_window}. "
                f"Active Process: {self.active_process}. "
                f"Running: {', '.join(self.running_processes)}.")

class ContextCapture:
    """Captures ambient system context."""
    def __init__(self):
        self.notable_apps = {"Code", "chrome", "firefox", "Spotify", "Teams", "slack", "obsidian"}

    def capture(self) -> ContextSnapshot:
        """Capture current system state."""
        active_window = ""
        active_process = ""
        try:
            active_win = gw.getActiveWindow()
            if active_win:
                active_window = active_win.title
                active_process = "unknown"
        except Exception as e:
            logger.debug(f"Could not get active window: {e}")

        running = []
        try:
            for proc in psutil.process_iter(['name']):
                name = proc.info['name']
                if name:
                    for app in self.notable_apps:
                        if app.lower() in name.lower():
                            if name not in running:
                                running.append(name)
        except Exception as e:
            logger.debug(f"Could not get process list: {e}")

        now = datetime.now()
        day = now.strftime("%A")
        hour = now.hour
        if 5 <= hour < 12:
            bucket = "morning"
        elif 12 <= hour < 17:
            bucket = "afternoon"
        elif 17 <= hour < 21:
            bucket = "evening"
        else:
            bucket = "night"

        return ContextSnapshot(
            active_window=active_window,
            active_process=active_process,
            running_processes=running,
            timestamp=now,
            time_bucket=bucket,
            day_of_week=day
        )
