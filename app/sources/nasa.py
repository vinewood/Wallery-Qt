"""NASA APOD source (spec §3.3).

NASA uses a public demo key ``DEMO_KEY`` as the allowed fallback when the
user has not supplied their own key (per security convention in the spec).
"""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from app.core.http import get_json
from app.sources.base import BaseSource, WallpaperItem

_API = "https://api.nasa.gov/planetary/apod"
DEMO_KEY = "DEMO_KEY"  # public demo constant, non-secret, allowed as fallback


class NasaSource(BaseSource):
    name = "nasa"
    display_name = "NASA APOD"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or DEMO_KEY

    def _fetch(self, count: int) -> List[Dict]:
        data = get_json(_API, params={
            "api_key": self.api_key, "count": count, "thumbs": "true",
        })
        # count request returns a list; single returns a dict
        if isinstance(data, dict):
            return [data]
        return data

    @staticmethod
    def _parse_item(item: Dict) -> Optional[WallpaperItem]:
        media_type = item.get("media_type", "image")
        # For video APODs, fall back to the thumbnail
        if media_type == "video":
            url = item.get("thumbnail_url") or item.get("url") or ""
        else:
            url = item.get("hdurl") or item.get("url") or ""
        if not url:
            return None
        date = item.get("date", "")
        ymd = date.replace("-", "")
        thumb = item.get("thumbnail_url") or item.get("url") or url
        title = item.get("title", "NASA APOD")
        return WallpaperItem(
            id=f"nasa-apod-{date}",
            url=url,
            source="nasa",
            display_name="NASA APOD",
            thumbnail=thumb,
            attribution=f"NASA APOD · {title} · {date}",
            source_page=f"https://apod.nasa.gov/apod/ap{ymd}.html",
        )

    def fetch_list(self, category: str = "all", page: int = 1) -> List[WallpaperItem]:
        raw = self._fetch(12)
        items: List[WallpaperItem] = []
        for it in raw:
            parsed = self._parse_item(it)
            if parsed:
                items.append(parsed)
        return items

    def fetch_random(self, categories: Optional[List[str]] = None) -> Optional[WallpaperItem]:
        raw = self._fetch(1)
        if not raw:
            return None
        return self._parse_item(raw[0])
