"""Bing Daily source (spec §3.1)."""
from __future__ import annotations

import os
import random
from typing import Dict, List, Optional

from app.core.http import get_json
from app.sources.base import BaseSource, WallpaperItem, SourceError

_BING_API = "https://www.bing.com/HPImageArchive.aspx"
_MARKET_MAP = {
    "zh_cn": "zh-CN", "zh_sg": "zh-CN",
    "zh_tw": "zh-TW", "zh_hk": "zh-TW",
    "ja_jp": "ja-JP", "ko_kr": "ko-KR",
    "en_us": "en-US", "en_gb": "en-GB",
    "de_de": "de-DE", "fr_fr": "fr-FR",
}


def _detect_market() -> str:
    loc = (os.environ.get("LANG") or os.environ.get("LC_ALL") or "").lower()
    if not loc:
        try:
            import locale
            loc = (locale.getdefaultlocale()[0] or "").lower()
        except Exception:
            loc = ""
    key = loc.replace("-", "_")
    return _MARKET_MAP.get(key, "en-US")


class BingSource(BaseSource):
    name = "bing"
    display_name = "Bing Daily"

    def _fetch_raw(self, n: int) -> List[Dict]:
        market = _detect_market()
        data = get_json(_BING_API, params={
            "format": "js", "idx": 0, "n": n, "mkt": market,
        })
        return data.get("images", [])

    def fetch_list(self, category: str = "all", page: int = 1) -> List[WallpaperItem]:
        images = self._fetch_raw(8)
        items: List[WallpaperItem] = []
        for i, img in enumerate(images):
            base = img.get("urlbase") or ""
            if not base:
                continue
            url = "https://www.bing.com" + base + "_1920x1080.jpg"
            thumb = "https://www.bing.com" + base + "_640x360.jpg"
            enddate = img.get("enddate", "")
            items.append(WallpaperItem(
                id=f"bing-{enddate}-{i}",
                url=url,
                source=self.name,
                display_name=self.display_name,
                thumbnail=thumb,
                attribution=img.get("copyright", "Bing"),
                source_page=img.get("copyrightlink", "https://www.bing.com"),
            ))
        return items

    def fetch_random(self, categories: Optional[List[str]] = None) -> Optional[WallpaperItem]:
        images = self._fetch_raw(8)
        if not images:
            return None
        img = random.choice(images)
        base = img.get("urlbase") or ""
        if not base:
            return None
        url = "https://www.bing.com" + base + "_1920x1080.jpg"
        thumb = "https://www.bing.com" + base + "_640x360.jpg"
        enddate = img.get("enddate", "")
        return WallpaperItem(
            id=f"bing-{enddate}-r{random.randint(0, 9999)}",
            url=url,
            source=self.name,
            display_name=self.display_name,
            thumbnail=thumb,
            attribution=img.get("copyright", "Bing"),
            source_page=img.get("copyrightlink", "https://www.bing.com"),
        )
