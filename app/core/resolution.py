"""Resolution-aware URL resolution (spec §4).

Before setting / downloading a wallpaper, adjust the URL to the version
that best matches the target screen resolution.
"""
from __future__ import annotations

import re
from typing import Tuple


def resolve_best_url(url: str, source: str, target_w: int, target_h: int) -> str:
    """Return the URL variant best matching ``(target_w, target_h)``.

    Source-specific rules follow the requirements spec §4.
    """
    if not url:
        return url

    src = (source or "").lower()

    if src == "bing":
        return _resolve_bing(url, target_w, target_h)
    if src == "unsplash":
        return _resolve_unsplash(url, target_w, target_h)
    # pexels / wallhaven / nasa / others: pass through
    return url


def _resolve_bing(url: str, target_w: int, target_h: int) -> str:
    max_dim = max(target_w, target_h)
    if max_dim > 2500:
        suffix = "_UHD.jpg"
    elif max_dim > 1200:
        suffix = "_1920x1080.jpg"
    else:
        suffix = "_1366x768.jpg"

    if url.endswith(suffix):
        return url

    # Known bing patterns to strip (with leading underscore, before .jpg)
    patterns = ["_UHD", "_1920x1080", "_1366x768", "_640x360"]
    base = url
    if base.endswith(".jpg"):
        base = base[:-4]
    for p in patterns:
        if base.endswith(p):
            base = base[: -len(p)]
            break
    return base + suffix


def _resolve_unsplash(url: str, target_w: int, target_h: int) -> str:
    # Already a sized (regular/small) image -> leave as-is
    if "&w=" in url or "?w=" in url:
        return url
    w = min(target_w, 1920)
    h = min(target_h, 1080)
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}w={w}&h={h}&q=85&fm=jpg&fit=crop"
