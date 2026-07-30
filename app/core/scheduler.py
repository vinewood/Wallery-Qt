"""Scheduled wallpaper rotation (spec §5.6).

A QTimer polls every 60s and, depending on the schedule config & frequency,
triggers the injected ``do_next`` callback (the real fetch+apply logic).
"""
from __future__ import annotations

from datetime import datetime
from typing import Callable, Optional

from PySide6.QtCore import QObject, QTimer

from app.config import get_config


class Scheduler(QObject):
    def __init__(self, do_next: Callable[[], bool], parent: Optional[QObject] = None):
        super().__init__(parent)
        self._do_next = do_next
        self._timer = QTimer(self)
        self._timer.setInterval(60 * 1000)  # 60s poll
        self._timer.timeout.connect(self._on_tick)

    # -- control -----------------------------------------------------------
    def start(self) -> None:
        self._timer.start()
        # immediate first run
        self._run_once()

    def stop(self) -> None:
        self._timer.stop()

    # -- logic -------------------------------------------------------------
    def _run_once(self) -> None:
        cfg = get_config()
        sched = cfg.get_schedule()
        if not sched.get("enabled", True):
            return
        if self._should_run(sched):
            ok = False
            try:
                ok = bool(self._do_next())
            except Exception:
                ok = False
            if ok:
                today = datetime.now().strftime("%Y-%m-%d")
                cfg.set_schedule(last_run_date=today)

    def _on_tick(self) -> None:
        self._run_once()

    @staticmethod
    def _should_run(sched: dict) -> bool:
        now = datetime.now()
        sched_min = int(sched.get("hour", 10)) * 60 + int(sched.get("minute", 0))
        cur_min = now.hour * 60 + now.minute
        freq = sched.get("frequency", "daily")
        today = now.strftime("%Y-%m-%d")

        if freq == "daily":
            in_window = sched_min <= cur_min < sched_min + 5
            ran_today = sched.get("last_run_date") == today
            return in_window and not ran_today
        if freq == "12h":
            return (cur_min - sched_min) % (12 * 60) < 5
        if freq == "6h":
            return (cur_min - sched_min) % (6 * 60) < 5
        if freq == "1h":
            return cur_min % 60 < 5
        return False
