"""Application coordinator: wires config, sources, scheduler, tray, window."""
from __future__ import annotations

import os
import sys
from typing import Dict, Optional

from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication

from app.config import get_config
from app.core.download import download_wallpaper_url, save_current_wallpaper
from app.core.scheduler import Scheduler
from app.core.wallpaper import set_wallpaper
from app.favorites import add as fav_add
from app.favorites import remove as fav_remove
from app.i18n import reload_language, t
from app.sources.manager import SourceManager
from app.ui.main_window import MainWindow
from app.ui.tray import TrayIcon


class WalleryApp(QObject):
    favorites_changed = Signal()

    def __init__(self, qapp: QApplication):
        super().__init__()
        self.qapp = qapp
        self._really_quit = False
        get_config()
        reload_language()

        self.manager = SourceManager(self)
        self.scheduler = Scheduler(do_next=self.manager.do_next_wallpaper, parent=self)
        self.window = MainWindow(self)
        self.tray = TrayIcon(self)

        self.manager.wallpaper_changed.connect(self._on_wallpaper_changed)
        self.manager.error_occurred.connect(self._on_error)

    # -- lifecycle ---------------------------------------------------------
    def start(self):
        self.apply_theme(get_config().get("theme", "dark"))
        self._sync_autostart()
        self.tray.show()
        self.scheduler.start()
        if "--minimized" not in sys.argv:
            self.window.show()

    def quit(self):
        self._really_quit = True
        self.qapp.quit()

    # -- window control ----------------------------------------------------
    def show_main_window(self):
        self.window.showNormal()
        self.window.raise_()
        self.window.activateWindow()

    # -- toasts ------------------------------------------------------------
    def show_toast(self, content: str, success: bool = True, title: str = ""):
        try:
            from qfluentwidgets import InfoBar, InfoBarPosition
            if success:
                InfoBar.success(title=title, content=content, parent=self.window,
                               duration=5000, position=InfoBarPosition.BOTTOM_RIGHT)
            else:
                InfoBar.error(title=title, content=content, parent=self.window,
                              duration=5000, position=InfoBarPosition.BOTTOM_RIGHT)
        except Exception:
            pass

    # -- wallpaper actions -------------------------------------------------
    def set_wallpaper_from_item(self, item: Dict) -> bool:
        try:
            url = item.get("url")
            if not url:
                # placeholder card -> go random
                return self.manager.do_next_wallpaper()
            from app.core.download import download_to_cache
            local = download_to_cache(url, item.get("source", ""))
            sched = get_config().get_schedule()
            set_wallpaper(local,
                         set_desktop=sched.get("set_desktop", True),
                         set_lock_screen=sched.get("set_lock_screen", False))
            get_config().set_current_wallpaper(url, local, item.get("source", ""))
            self.show_toast(t("common.set_ok"), success=True)
            return True
        except Exception as e:
            self.show_toast(t("common.download_fail", str(e)), success=False)
            return False

    def download_item(self, item: Dict) -> Optional[str]:
        try:
            url = item.get("url")
            if not url:
                return None
            path = download_wallpaper_url(url, item.get("source", ""))
            self.show_toast(t("common.download_ok", path), success=True)
            return path
        except Exception as e:
            self.show_toast(t("common.download_fail", str(e)), success=False)
            return None

    def toggle_favorite(self, item: Dict) -> bool:
        from app.favorites import is_favorited
        if is_favorited(item.get("id", "")):
            fav_remove(item.get("id", ""))
            self.favorites_changed.emit()
            self.show_toast(t("common.fav_del"), success=True)
            return False
        err = fav_add(item)
        if err == "duplicate":
            self.show_toast(t("common.fav_dup"), success=False)
            return True
        if err == "limit":
            self.show_toast(t("common.fav_limit"), success=False)
            return False
        if err == "no_id":
            return False
        self.favorites_changed.emit()
        self.show_toast(t("common.fav_ok"), success=True)
        return True

    def request_next(self):
        self.manager.request_next()

    # -- tray/scheduler callbacks -----------------------------------------
    def _on_wallpaper_changed(self, item: Dict, path: str):
        self.show_toast(t("common.set_ok"), success=True)

    def _on_error(self, msg: str):
        if msg == "missing_api_key" or "missing_api_key" in msg:
            self.show_toast(t("common.no_key", "Pexels/Unsplash"), success=False)
        elif msg in ("all_failed", "no_enabled_source"):
            self.show_toast(t("common.all_failed"), success=False)
        else:
            self.show_toast(t("common.download_fail", msg), success=False)

    # -- misc --------------------------------------------------------------
    def save_current_wallpaper_action(self) -> Optional[str]:
        return save_current_wallpaper()

    def check_update(self) -> str:
        # Update server not configured for the new repo; placeholder UI (spec §9)
        return t("settings.latest")

    def apply_theme(self, theme: str):
        try:
            from qfluentwidgets import Theme, setTheme
            if theme == "light":
                setTheme(Theme.LIGHT)
            elif theme == "auto":
                scheme = (QApplication.styleHints().colorScheme()
                          if hasattr(QApplication, "styleHints") else None)
                from PySide6.QtCore import Qt
                if scheme == Qt.ColorScheme.Dark:
                    setTheme(Theme.DARK)
                else:
                    setTheme(Theme.LIGHT)
            else:
                setTheme(Theme.DARK)
        except Exception:
            pass

    def set_autostart(self, enabled: bool):
        get_config().set_auto_start(enabled)
        self._write_autostart(enabled)

    def _sync_autostart(self):
        self._write_autostart(get_config().get_auto_start())

    def _write_autostart(self, enabled: bool):
        if sys.platform != "win32":
            return
        try:
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            if enabled:
                exe = sys.executable
                script = os.path.abspath(sys.argv[0])
                value = f'"{exe}" "{script}" --minimized'
                winreg.SetValueEx(key, "Wallery", 0, winreg.REG_SZ, value)
            else:
                try:
                    winreg.DeleteValue(key, "Wallery")
                except OSError:
                    pass
        except Exception:
            pass
