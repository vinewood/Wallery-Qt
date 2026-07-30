"""Wallery-Qt entry point.

PySide6 + QFluentWidgets rebuild of Wallery. See app/app.py for the
coordinator and app/config.py / app/sources / app/core for logic.
"""
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication

from app.app import WalleryApp
from app.i18n import reload_language


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Wallery")
    app.setApplicationDisplayName("Wallery 幕间")

    try:
        from qfluentwidgets import setThemeColor
        setThemeColor("#5b9cf5")
    except Exception:
        pass

    reload_language()
    wallery = WalleryApp(app)
    wallery.start()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
