"""Download & filesystem caching helpers.

Wallpaper images are first fetched into the app cache dir, then (for an
explicit user download) copied into the configured download directory.
"""
from __future__ import annotations

import os
import shutil
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

from app.config import CACHE_DIR, get_config
from app.core.http import ext_from_url, get_bytes
from app.core.resolution import resolve_best_url
from app.core.screen import get_primary_resolution


def _unique_cache_path(source: str, ext: str) -> Path:
    ts = int(time.time() * 1000)
    return CACHE_DIR / f"{source}_{ts}.{ext}"


def download_to_cache(url: str, source: str, ext: Optional[str] = None) -> str:
    """Download ``url`` into the cache dir, return local path.

    Performs resolution-aware URL resolution before download.
    """
    w, h = get_primary_resolution()
    final_url = resolve_best_url(url, source, w, h)
    data = get_bytes(final_url)
    if ext is None:
        ext = ext_from_url(final_url)
    path = _unique_cache_path(source, ext)
    with open(path, "wb") as f:
        f.write(data)
    return str(path)


def download_wallpaper_url(url: str, source: str, open_folder: bool = None) -> str:
    """Download a specific wallpaper to the user download directory.

    Returns the destination path. Filename:
    ``wallery_{source}_{YYYYMMDD_HHMMSS}.jpg``.
    """
    if open_folder is None:
        open_folder = get_config().get("open_folder_after_download", True)

    local = download_to_cache(url, source)

    dest_dir = get_config().get_download_path()
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = ext_from_url(local)
    dest = dest_dir / f"wallery_{source}_{stamp}.{ext}"
    shutil.copyfile(local, dest)

    if open_folder:
        open_in_explorer(dest_dir)
    return str(dest)


def save_current_wallpaper() -> Optional[str]:
    """Copy the currently-set wallpaper file into the download dir."""
    cur = get_config().get_current_wallpaper()
    path = cur.get("path") or ""
    if not path or not os.path.exists(path):
        return None
    dest_dir = get_config().get_download_path()
    dest_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    ext = ext_from_url(path)
    source = cur.get("source") or "current"
    dest = dest_dir / f"wallery_{source}_{stamp}.{ext}"
    shutil.copyfile(path, dest)
    if get_config().get("open_folder_after_download", True):
        open_in_explorer(dest_dir)
    return str(dest)


def open_in_explorer(path: Path) -> None:
    """Open ``path`` in Windows Explorer (or the OS file manager)."""
    import subprocess
    p = str(path)
    if os.name == "nt":
        subprocess.Popen(["explorer", "/select,", p])
    else:
        subprocess.Popen(["xdg-open", p])
