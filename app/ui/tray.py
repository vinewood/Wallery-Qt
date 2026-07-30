"""System tray (spec §6)."""
from __future__ import annotations

import webbrowser

from PySide6.QtGui import QAction, QIcon, QPixmap, QColor, QPainter, Qt
from PySide6.QtWidgets import QMenu, QSystemTrayIcon

from app.config import get_config
from app.i18n import t

_SOURCE_HOMEPAGE = {
    "bing": "https://www.bing.com",
    "wallhaven": "https://wallhaven.cc",
    "nasa": "https://apod.nasa.gov/apod/",
    "pexels": "https://www.pexels.com",
    "unsplash": "https://unsplash.com",
}


def _make_icon() -> QIcon:
    pm = QPixmap(32, 32)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setBrush(QColor("#5b9cf5"))
    p.setPen(Qt.NoPen)
    p.drawRoundedRect(0, 0, 32, 32, 7, 7)
    p.setPen(Qt.GlobalColor.white)
    f = p.font()
    f.setBold(True)
    f.setPointSize(16)
    p.setFont(f)
    p.drawText(pm.rect(), Qt.AlignCenter, "W")
    p.end()
    return QIcon(pm)


class TrayIcon(QSystemTrayIcon):
    def __init__(self, app, parent=None):
        super().__init__(_make_icon(), parent)
        self.app = app
        self.setToolTip(t("tray.tooltip"))
        self._build_menu()
        self.activated.connect(self._on_activate)

    def _build_menu(self):
        menu = QMenu()

        a_next = QAction(t("tray.next"), menu)
        a_next.triggered.connect(lambda: self.app.request_next())
        menu.addAction(a_next)

        a_skip = QAction(t("tray.skip"), menu)
        a_skip.triggered.connect(self._skip)
        menu.addAction(a_skip)

        menu.addSeparator()

        a_copy = QAction(t("tray.copy_url"), menu)
        a_copy.triggered.connect(self._copy_url)
        menu.addAction(a_copy)

        a_save = QAction(t("tray.save"), menu)
        a_save.triggered.connect(self._save)
        menu.addAction(a_save)

        a_src = QAction(t("tray.open_src"), menu)
        a_src.triggered.connect(self._open_src)
        menu.addAction(a_src)

        menu.addSeparator()

        a_open = QAction(t("tray.open_wnd"), menu)
        a_open.triggered.connect(self.app.show_main_window)
        menu.addAction(a_open)

        a_settings = QAction(t("tray.settings"), menu)
        a_settings.triggered.connect(self.app.show_main_window)
        menu.addAction(a_settings)

        menu.addSeparator()

        a_quit = QAction(t("tray.quit"), menu)
        a_quit.triggered.connect(self.app.quit)
        menu.addAction(a_quit)

        self.setContextMenu(menu)

    def _on_activate(self, reason):
        # Single click on some platforms also opens the window
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.app.show_main_window()

    # -- tray actions ------------------------------------------------------
    def _skip(self):
        # Original had no real behaviour; keep as logged no-op
        pass

    def _copy_url(self):
        url = get_config().get_current_wallpaper().get("url", "")
        if url:
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(url)
            self.app.show_toast(t("common.copied"), success=True)

    def _save(self):
        path = self.app.save_current_wallpaper_action()
        if path:
            self.app.show_toast(t("common.saved_current"), success=True)
        else:
            self.app.show_toast(t("common.download_fail", "no current"), success=False)

    def _open_src(self):
        src = get_config().get_current_wallpaper().get("source", "")
        url = _SOURCE_HOMEPAGE.get(src, "https://www.bing.com")
        webbrowser.open(url)
        self.app.show_toast(t("common.open_src"), success=True)
