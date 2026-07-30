"""Primary screen resolution detection.

Combines QScreen (most accurate for the current main display) with a
ctypes ``GetSystemMetrics`` fallback, and ultimately (1920, 1080).
"""
from __future__ import annotations

import ctypes
import sys
from typing import Tuple

_FALLBACK = (1920, 1080)


def get_primary_resolution() -> Tuple[int, int]:
    """Return ``(width, height)`` of the primary screen."""
    # Preferred: Qt screen geometry (matches current main display)
    try:
        from PySide6.QtWidgets import QApplication
        app = QApplication.instance()
        if app is not None:
            screen = app.primaryScreen()
            if screen is not None:
                geo = screen.geometry()
                if geo.width() > 0 and geo.height() > 0:
                    return geo.width(), geo.height()
    except Exception:
        pass

    # Fallback: Win32 GetSystemMetrics
    if sys.platform == "win32":
        try:
            SM_CXSCREEN = 0
            SM_CYSCREEN = 1
            w = ctypes.windll.user32.GetSystemMetrics(SM_CXSCREEN)
            h = ctypes.windll.user32.GetSystemMetrics(SM_CYSCREEN)
            if w > 0 and h > 0:
                return w, h
        except Exception:
            pass

    return _FALLBACK
