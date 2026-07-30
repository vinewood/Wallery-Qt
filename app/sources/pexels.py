"""Pexels source (spec §3.4)."""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from app.core.http import get_json
from app.sources.base import BaseSource, WallpaperItem, SourceError

_API = "https://api.pexels.com/v1/search"


class PexelsSource(BaseSource):
    name = "pexels"
    display_name = "Pexels"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or ""

    def _require_key(self):
        if not self.api_key:
            raise SourceError("missing_api_key")

    def _query(self, categories: Optional[List[str]]) -> str:
        if categories:
            joined = " ".join(c for c in categories if c and c.lower() != "all")
            if joined:
                return joined + " wallpaper"
        return "nature wallpaper"

    def fetch_list(self, category: str = "all", page: int = 1) -> List[WallpaperItem]:
        self._require_key()
        query = self._query([category])
        data = get_json(_API, params={
            "query": query, "page": page, "per_page": 15,
            "orientation": "landscape",
        }, headers={"Authorization": self.api_key})
        return self._parse(data)

    def fetch_random(self, categories: Optional[List[str]] = None) -> Optional[WallpaperItem]:
        self._require_key()
        query = self._query(categories)
        data = get_json(_API, params={
            "query": query, "per_page": 1,
            "orientation": "landscape", "size": "large",
        }, headers={"Authorization": self.api_key})
        photos = data.get("photos", [])
        if not photos:
            return None
        return self._parse_one(photos[0])

    @staticmethod
    def _parse_one(p: Dict) -> WallpaperItem:
        pid = p.get("id", "")
        src = p.get("src", {})
        url = src.get("original") or src.get("large") or src.get("large2x") or ""
        thumb = src.get("medium") or url
        return WallpaperItem(
            id=f"pexels-{pid}",
            url=url,
            source="pexels",
            display_name="Pexels",
            thumbnail=thumb,
            attribution=f"📷 {p.get('photographer', 'Pexels')} · Pexels",
            source_page=p.get("url", "https://www.pexels.com"),
        )

    def _parse(self, data: Dict) -> List[WallpaperItem]:
        return [self._parse_one(p) for p in data.get("photos", [])]
