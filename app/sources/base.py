"""Base class & shared types for wallpaper sources (spec §3)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class WallpaperItem:
    id: str
    url: str
    source: str
    display_name: str = ""
    thumbnail: str = ""
    attribution: str = ""
    source_page: str = ""

    def to_dict(self) -> Dict[str, str]:
        return {
            "id": self.id,
            "url": self.url,
            "source": self.source,
            "display_name": self.display_name,
            "thumbnail": self.thumbnail,
            "attribution": self.attribution,
            "source_page": self.source_page,
        }


class SourceError(Exception):
    """Raised when a source fails (e.g. missing API key, network error)."""


class BaseSource:
    """Interface every source adapter implements."""

    name: str = ""
    display_name: str = ""

    def fetch_list(self, category: str = "all", page: int = 1) -> List[WallpaperItem]:
        raise NotImplementedError

    def fetch_random(self, categories: Optional[List[str]] = None) -> Optional[WallpaperItem]:
        raise NotImplementedError

    # Helpers --------------------------------------------------------------
    @staticmethod
    def _join(items: List[WallpaperItem]) -> List[Dict[str, str]]:
        return [it.to_dict() for it in items]
