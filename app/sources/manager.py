"""Source manager: orchestrates fetching, "next random", and caching.

Exposes Qt signals so the UI / tray can react without blocking.
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal

from app.config import SOURCE_META, SOURCE_ORDER, get_config
from app.core.download import download_to_cache
from app.core.wallpaper import set_wallpaper
from app.sources.base import WallpaperItem
from app.sources.registry import build_source


class _NextWorker(QRunnable):
    def __init__(self, manager: "SourceManager"):
        super().__init__()
        self._mgr = manager

    def run(self):
        try:
            self._mgr._do_next_blocking()
        except Exception as e:  # surface to UI
            self._mgr.error_occurred.emit(f"next_failed: {e}")


class _ListWorker(QRunnable):
    def __init__(self, manager: "SourceManager", name: str,
                 category: str, page: int):
        super().__init__()
        self._mgr = manager
        self._name = name
        self._category = category
        self._page = page

    def run(self):
        try:
            items = self._mgr._fetch_list_blocking(
                self._name, self._category, self._page)
            self._mgr.list_loaded.emit(self._name, self._category, self._page, items)
        except Exception as e:
            self._mgr.list_error.emit(self._name, str(e))


class SourceManager(QObject):
    """Coordinates all wallpaper sources."""

    wallpaper_changed = Signal(dict, str)  # item dict, local path
    error_occurred = Signal(str)
    list_loaded = Signal(str, str, int, list)  # name, category, page, items
    list_error = Signal(str, str)  # name, error

    def __init__(self, parent: Optional[QObject] = None):
        super().__init__(parent)
        self._pool = QThreadPool(self)
        self._pool.setMaxThreadCount(6)

    # -- source access -----------------------------------------------------
    def get_source(self, name: str):
        cfg = get_config()
        api_key = cfg.get_api_key(name) if name in ("pexels", "unsplash", "nasa") else ""
        return build_source(name, api_key)

    # -- status ------------------------------------------------------------
    def get_sources_status(self) -> List[Dict]:
        cfg = get_config()
        out = []
        for name in SOURCE_ORDER:
            meta = SOURCE_META[name]
            enabled = cfg.is_source_enabled(name)
            has_key = bool(cfg.get_api_key(name))
            out.append({
                "name": name,
                "display_name": meta["display_name"],
                "brand": meta["brand"],
                "abbr": meta["abbr"],
                "desc": meta["desc"],
                "enabled": enabled,
                "needs_api_key": meta["needs_api_key"],
                "has_api_key": has_key,
                "hot_categories": meta["hot_categories"],
            })
        return out

    def get_source_hot_categories(self, name: str) -> List[str]:
        return list(SOURCE_META.get(name, {}).get("hot_categories", []))

    # -- list (async) ------------------------------------------------------
    def fetch_list_async(self, name: str, category: str = "all", page: int = 1):
        self._pool.start(_ListWorker(self, name, category, page))

    def _fetch_list_blocking(self, name: str, category: str, page: int) -> List[Dict]:
        src = self.get_source(name)
        items = src.fetch_list(category, page)
        return [it.to_dict() for it in items]

    # -- next random (async) ----------------------------------------------
    def request_next(self):
        """Trigger do_next_wallpaper in a background thread."""
        self._pool.start(_NextWorker(self))

    def do_next_wallpaper(self) -> bool:
        """Blocking variant (also callable directly)."""
        return self._do_next_blocking()

    def _do_next_blocking(self) -> bool:
        cfg = get_config()
        enabled = cfg.enabled_sources()
        if not enabled:
            self.error_occurred.emit("no_enabled_source")
            return False

        pool = list(enabled)
        random.shuffle(pool)
        categories = cfg.get_categories()

        last_err = ""
        for name in pool:
            try:
                src = self.get_source(name)
                item = src.fetch_random(categories)
                if item is None:
                    continue
                local = download_to_cache(item.url, item.source)
                sched = cfg.get_schedule()
                set_wallpaper(
                    local,
                    set_desktop=sched.get("set_desktop", True),
                    set_lock_screen=sched.get("set_lock_screen", False),
                )
                cfg.set_current_wallpaper(item.url, local, item.source)
                self.wallpaper_changed.emit(item.to_dict(), local)
                return True
            except Exception as e:
                last_err = str(e)
                continue

        self.error_occurred.emit(last_err or "all_failed")
        return False

    # -- synchronous single fetch (used by set-wallpaper-from-url) ---------
    def fetch_one(self, name: str, category: str = "all") -> Optional[Dict]:
        src = self.get_source(name)
        items = src.fetch_list(category, 1)
        if items:
            return items[0].to_dict()
        return None
