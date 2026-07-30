"""Resource path helper compatible with PyInstaller (sys._MEIPASS).

When frozen (--onefile), bundled files live under ``sys._MEIPASS/resources``.
In dev they live under ``<project_root>/resources``.
"""
from __future__ import annotations

import sys
from pathlib import Path


def resource_path(name: str) -> Path:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return Path(base) / "resources" / name
    # __file__ is <project_root>/app/resources.py -> parent.parent == project root
    return Path(__file__).resolve().parent.parent / "resources" / name
