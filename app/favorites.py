"""Local favorites persistence (spec §1.3, §5.3).

Stored in ``favorites.json``; capped at 100 entries; deduplicated by ``id``.
"""
from __future__ import annotations

import json
from datetime import datetime
from typing import Dict, List, Optional

from app.config import FAVORITES_FILE

MAX_FAVORITES = 100


def _load() -> List[Dict]:
    try:
        if FAVORITES_FILE.exists():
            with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
    except Exception:
        pass
    return []


def _save(items: List[Dict]) -> None:
    FAVORITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    tmp = FAVORITES_FILE.with_suffix(".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    tmp.replace(FAVORITES_FILE)


def get_all() -> List[Dict]:
    return _load()


def is_favorited(item_id: str) -> bool:
    return any(f.get("id") == item_id for f in _load())


def add(item: Dict) -> str:
    """Add a favorite. Returns '' on success, else an error code."""
    items = _load()
    item_id = item.get("id", "")
    if not item_id:
        return "no_id"
    if any(f.get("id") == item_id for f in items):
        return "duplicate"
    if len(items) >= MAX_FAVORITES:
        return "limit"
    fav = {
        "id": item_id,
        "url": item.get("url", ""),
        "thumbnail": item.get("thumbnail", ""),
        "source": item.get("source", ""),
        "display_name": item.get("display_name", ""),
        "attribution": item.get("attribution", ""),
        "source_page": item.get("source_page", ""),
        "created_at": item.get("created_at")
        or datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    items.append(fav)
    _save(items)
    return ""


def remove(item_id: str) -> None:
    items = [f for f in _load() if f.get("id") != item_id]
    _save(items)


def remove_by_item(item: Dict) -> None:
    remove(item.get("id", ""))
