"""Application configuration & persistence layer.

All user-configurable values live in ``config.json`` under the OS config
directory (``%APPDATA%/wallery`` on Windows, via QStandardPaths). No real
API keys are ever hardcoded — they are read from this config at runtime.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QStandardPaths

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
CONFIG_DIR = Path(
    QStandardPaths.standardLocations(QStandardPaths.ConfigLocation)[0]
) / "wallery"
CONFIG_FILE = CONFIG_DIR / "config.json"
FAVORITES_FILE = CONFIG_DIR / "favorites.json"
CACHE_FILE = CONFIG_DIR / "wallpaper_cache.json"

CACHE_DIR = Path(
    QStandardPaths.standardLocations(QStandardPaths.CacheLocation)[0]
) / "wallery"
PICTURES_DIR = Path(
    QStandardPaths.standardLocations(QStandardPaths.PicturesLocation)[0]
)
DEFAULT_DOWNLOAD_DIR = PICTURES_DIR / "Wallery"

# Source order is fixed (used for "next random" rotation & default list)
SOURCE_ORDER = ["bing", "wallhaven", "nasa", "pexels", "unsplash"]

# Per-source metadata (display names, brand colour, abbreviation, descriptions,
# hot categories) — all static & public, no secrets.
SOURCE_META: Dict[str, Dict[str, Any]] = {
    "bing": {
        "name": "bing",
        "display_name": "Bing Daily",
        "brand": "#008373",
        "abbr": "B",
        "desc": "微软 Bing 每日美图，自动匹配所在地区",
        "needs_api_key": False,
        "hot_categories": ["Nature", "Landscape", "City", "Animal", "Travel",
                           "Aerial", "Underwater", "Night", "Sunrise", "Snow"],
    },
    "wallhaven": {
        "name": "wallhaven",
        "display_name": "Wallhaven",
        "brand": "#4d7cff",
        "abbr": "WH",
        "desc": "高质量社区壁纸，无需 API Key",
        "needs_api_key": False,
        "hot_categories": ["Nature", "Minimal", "Abstract", "Anime", "City",
                           "Space", "Ocean", "Mountain", "Forest", "Architecture",
                           "Cyberpunk", "Dark", "Fantasy", "Retro", "Sci-Fi",
                           "Night", "Sunset", "Waterfall", "Vintage", "Technology"],
    },
    "nasa": {
        "name": "nasa",
        "display_name": "NASA APOD",
        "brand": "#0b3d91",
        "abbr": "N",
        "desc": "天文图片每日一图，探索宇宙之美",
        "needs_api_key": False,  # uses DEMO_KEY fallback
        "hot_categories": ["Nebula", "Galaxy", "Planet", "Earth", "Moon", "Sun",
                           "ISS", "Aurora", "Comet", "Deep Space", "Mars",
                           "Jupiter", "Saturn", "Solar Flare", "Milky Way",
                           "Constellation"],
    },
    "pexels": {
        "name": "pexels",
        "display_name": "Pexels",
        "brand": "#05a081",
        "abbr": "Px",
        "desc": "免费高清摄影图库，需 API Key",
        "needs_api_key": True,
        "hot_categories": ["Landscape", "Nature", "Sunset", "Flowers", "Beach",
                           "Autumn", "Winter", "Wildlife", "Mountains", "Waterfall",
                           "Stars", "Forest", "Ocean", "City", "Architecture",
                           "Travel", "Night", "Minimal", "Abstract", "Food"],
    },
    "unsplash": {
        "name": "unsplash",
        "display_name": "Unsplash",
        "brand": "#000000",
        "abbr": "Un",
        "desc": "摄影师社区精选，需 API Key",
        "needs_api_key": True,
        "hot_categories": ["Travel", "Nature", "Textures", "Film", "Interior",
                           "Street Photography", "Minimalism", "Food", "Architecture",
                           "Business", "Technology", "Fashion", "Animals", "Health",
                           "Sports", "Night", "Water", "Mountains"],
    },
}

DEFAULT_CATEGORIES = ["自然风景", "极简", "星空", "城市夜景"]


def _default_config() -> Dict[str, Any]:
    return {
        "sources": {
            name: {"enabled": True, "api_key": ""} for name in SOURCE_ORDER
        },
        "categories": list(DEFAULT_CATEGORIES),
        "schedule": {
            "enabled": True,
            "hour": 10,
            "minute": 0,
            "set_desktop": True,
            "set_lock_screen": True,  # refined per-platform at load time
            "frequency": "daily",
        },
        "auto_start": True,
        "language": "auto",
        "current_wallpaper_url": "",
        "current_wallpaper_path": "",
        "current_source": "",
        "last_update": "",
        "download_path": "",
        "open_folder_after_download": True,
        "last_selected_source": "unsplash",
    }


class Config:
    """Singleton-style configuration holder backed by ``config.json``."""

    _instance: Optional["Config"] = None

    def __new__(cls) -> "Config":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if getattr(self, "_initialized", False):
            return
        self._initialized = True
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self._data: Dict[str, Any] = _default_config()
        self._load()

    # -- persistence -------------------------------------------------------
    def _load(self) -> None:
        try:
            if CONFIG_FILE.exists():
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                self._merge(loaded)
        except Exception:
            # Corrupt config — fall back to defaults
            self._data = _default_config()
        self._normalize_platform_defaults()

    def _merge(self, loaded: Dict[str, Any]) -> None:
        """Shallow/structured merge of loaded data over defaults."""
        defaults = _default_config()
        for k, v in loaded.items():
            if k == "sources":
                for name, sv in (v or {}).items():
                    if name in self._data["sources"]:
                        self._data["sources"][name].update(sv or {})
            elif k == "schedule":
                self._data["schedule"].update(v or {})
            else:
                self._data[k] = v
        # ensure every known source exists
        for name in SOURCE_ORDER:
            if name not in self._data["sources"]:
                self._data["sources"][name] = {"enabled": True, "api_key": ""}

    def _normalize_platform_defaults(self) -> None:
        import sys
        if sys.platform != "win32":
            # Lock screen is Windows-only
            if self._data["schedule"].get("set_lock_screen") is True and \
               "set_lock_screen" not in self._raw_keys():
                self._data["schedule"]["set_lock_screen"] = False

    def _raw_keys(self):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f).get("schedule", {}).keys())
        except Exception:
            return set()

    def save(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        tmp = CONFIG_FILE.with_suffix(".tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
        tmp.replace(CONFIG_FILE)

    # -- generic access ----------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()

    # -- sources -----------------------------------------------------------
    def is_source_enabled(self, name: str) -> bool:
        return bool(self._data["sources"].get(name, {}).get("enabled", False))

    def set_source_enabled(self, name: str, enabled: bool) -> None:
        self._data["sources"].setdefault(name, {})["enabled"] = bool(enabled)
        self.save()

    def get_api_key(self, name: str) -> str:
        return self._data["sources"].get(name, {}).get("api_key", "") or ""

    def set_api_key(self, name: str, key: str) -> None:
        self._data["sources"].setdefault(name, {})["api_key"] = key or ""
        self.save()

    def enabled_sources(self) -> List[str]:
        return [n for n in SOURCE_ORDER if self.is_source_enabled(n)]

    # -- schedule ----------------------------------------------------------
    def get_schedule(self) -> Dict[str, Any]:
        return dict(self._data["schedule"])

    def set_schedule(self, **kwargs: Any) -> None:
        self._data["schedule"].update(kwargs)
        self.save()

    # -- categories --------------------------------------------------------
    def get_categories(self) -> List[str]:
        return list(self._data.get("categories", []))

    def add_category(self, cat: str) -> bool:
        cat = (cat or "").strip()
        if not cat:
            return False
        cats = self._data.setdefault("categories", [])
        if cat in cats:
            return False
        cats.append(cat)
        self.save()
        return True

    def remove_category(self, cat: str) -> None:
        cats = self._data.get("categories", [])
        if cat in cats:
            cats.remove(cat)
            self.save()

    # -- download dir ------------------------------------------------------
    def get_download_path(self) -> Path:
        p = self._data.get("download_path") or ""
        if p:
            return Path(p)
        return DEFAULT_DOWNLOAD_DIR

    def set_download_path(self, path: str) -> None:
        self._data["download_path"] = path or ""
        self.save()

    # -- current wallpaper ------------------------------------------------
    def set_current_wallpaper(self, url: str, path: str, source: str) -> None:
        self._data["current_wallpaper_url"] = url
        self._data["current_wallpaper_path"] = path
        self._data["current_source"] = source
        from datetime import datetime
        self._data["last_update"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.save()

    def get_current_wallpaper(self) -> Dict[str, str]:
        return {
            "url": self._data.get("current_wallpaper_url", ""),
            "path": self._data.get("current_wallpaper_path", ""),
            "source": self._data.get("current_source", ""),
            "last_update": self._data.get("last_update", ""),
        }

    # -- misc --------------------------------------------------------------
    def get_language(self) -> str:
        return self._data.get("language", "auto")

    def set_language(self, lang: str) -> None:
        self._data["language"] = lang
        self.save()

    def get_last_selected_source(self) -> str:
        src = self._data.get("last_selected_source", "unsplash")
        return src if src in SOURCE_ORDER else "unsplash"

    def set_last_selected_source(self, src: str) -> None:
        if src in SOURCE_ORDER:
            self._data["last_selected_source"] = src
            self.save()

    def get_auto_start(self) -> bool:
        return bool(self._data.get("auto_start", True))

    def set_auto_start(self, enabled: bool) -> None:
        self._data["auto_start"] = bool(enabled)
        self.save()

    # -- cache -------------------------------------------------------------
    def save_cache(self, items: List[Dict[str, Any]]) -> None:
        try:
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False)
        except Exception:
            pass

    def load_cache(self) -> List[Dict[str, Any]]:
        try:
            if CACHE_FILE.exists():
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception:
            pass
        return []


# Convenience singleton accessor
def get_config() -> Config:
    return Config()
