"""Wallhaven source (spec §3.2)."""
from __future__ import annotations

import random
import time
from typing import Dict, List, Optional

from app.core.http import get_json
from app.sources.base import BaseSource, WallpaperItem

_API = "https://wallhaven.cc/api/v1/search"

_CATEGORY_MAP = {
    "自然风景": "nature", "自然": "nature",
    "极简": "minimal", "极简主义": "minimal",
    "星空": "space", "宇宙": "space", "天文": "space",
    "城市夜景": "cityscape", "城市": "cityscape",
    "动漫": "anime", "二次元": "anime",
    "抽象": "abstract",
    "海洋": "ocean", "大海": "ocean",
    "山脉": "mountain", "山": "mountain",
    "森林": "forest", "树林": "forest",
    "建筑": "architecture",
    "赛博朋克": "cyberpunk",
    "暗色": "dark", "深色": "dark",
    "幻想": "fantasy", "奇幻": "fantasy",
    "复古": "retro", "怀旧": "retro",
    "科幻": "sci-fi",
}


def map_category_to_wallhaven(category: str) -> str:
    cat = (category or "").strip()
    if not cat or cat.lower() == "all":
        return "nature"
    if cat in _CATEGORY_MAP:
        return _CATEGORY_MAP[cat]
    # already english or unknown -> lowercase
    return cat.lower()


def _build_query(categories: Optional[List[str]]) -> str:
    if not categories:
        return "nature"
    mapped = [map_category_to_wallhaven(c) for c in categories if c and c.lower() != "all"]
    if not mapped:
        return "nature"
    return "+".join(mapped)


class WallhavenSource(BaseSource):
    name = "wallhaven"
    display_name = "Wallhaven"

    def fetch_list(self, category: str = "all", page: int = 1) -> List[WallpaperItem]:
        query = _build_query([category])
        data = get_json(_API, params={
            "q": query, "page": page,
            "sorting": "toplist", "atleast": "1920x1080",
        })
        return self._parse(data)

    def fetch_random(self, categories: Optional[List[str]] = None) -> Optional[WallpaperItem]:
        query = _build_query(categories)
        data = get_json(_API, params={
            "q": query, "sorting": "random",
            "atleast": "1920x1080", "seed": int(time.time()),
        })
        items = self._parse(data)
        return random.choice(items) if items else None

    @staticmethod
    def _parse(data: Dict) -> List[WallpaperItem]:
        items: List[WallpaperItem] = []
        for entry in data.get("data", []):
            pid = entry.get("id", "")
            path = entry.get("path") or entry.get("url") or ""
            if not path:
                continue
            thumbs = entry.get("thumbs", {})
            thumb = thumbs.get("small") or thumbs.get("original") or ""
            resolution = entry.get("resolution", "")
            items.append(WallpaperItem(
                id=f"wallhaven-{pid}",
                url=path,
                source="wallhaven",
                display_name="Wallhaven",
                thumbnail=thumb,
                attribution=f"Wallhaven · {resolution}",
                source_page=entry.get("url", "https://wallhaven.cc"),
            ))
        return items
