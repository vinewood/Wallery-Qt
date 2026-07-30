"""Unsplash source (spec §3.5)."""
from __future__ import annotations

import random
from typing import Dict, List, Optional

from app.core.http import get_json
from app.sources.base import BaseSource, WallpaperItem, SourceError

_SEARCH = "https://api.unsplash.com/search/photos"
_RANDOM = "https://api.unsplash.com/photos/random"


class UnsplashSource(BaseSource):
    name = "unsplash"
    display_name = "Unsplash"

    def __init__(self, api_key: str = ""):
        self.api_key = api_key or ""

    def _require_key(self):
        if not self.api_key:
            raise SourceError("missing_api_key")

    def _headers(self) -> Dict[str, str]:
        return {"Authorization": f"Client-ID {self.api_key}"}

    def fetch_list(self, category: str = "all", page: int = 1) -> List[WallpaperItem]:
        self._require_key()
        query = category if (category and category.lower() != "all") else "nature"
        data = get_json(_SEARCH, params={
            "query": query, "page": page, "per_page": 20,
            "orientation": "landscape",
        }, headers=self._headers())
        results = data.get("results", [])
        return [self._parse_one(p) for p in results]

    def fetch_random(self, categories: Optional[List[str]] = None) -> Optional[WallpaperItem]:
        self._require_key()
        params = {"orientation": "landscape", "count": 1}
        if categories:
            q = ",".join(c for c in categories if c and c.lower() != "all")
            if q:
                params["query"] = q
        data = get_json(_RANDOM, params=params, headers=self._headers())
        if isinstance(data, list):
            items = data
        else:
            items = [data]
        if not items:
            return None
        return self._parse_one(items[0])

    @staticmethod
    def _parse_one(p: Dict) -> WallpaperItem:
        pid = p.get("id", "")
        urls = p.get("urls", {})
        url = urls.get("full") or urls.get("raw") or ""
        thumb = urls.get("small") or urls.get("thumb") or url
        user = p.get("user", {})
        name = user.get("name", "Unsplash")
        return WallpaperItem(
            id=f"unsplash-{pid}",
            url=url,
            source="unsplash",
            display_name="Unsplash",
            thumbnail=thumb,
            attribution=f"📸 {name} · Unsplash",
            source_page=p.get("links", {}).get("html", "https://unsplash.com"),
        )
