"""Source registry — builds a source adapter instance by name (spec §3)."""
from __future__ import annotations

from app.sources.base import BaseSource
from app.sources.bing import BingSource
from app.sources.nasa import NasaSource
from app.sources.pexels import PexelsSource
from app.sources.unsplash import UnsplashSource
from app.sources.wallhaven import WallhavenSource


def build_source(name: str, api_key: str = "") -> BaseSource:
    """Return a source adapter instance for ``name`` with its API key."""
    name = (name or "").lower()
    if name == "bing":
        return BingSource()
    if name == "wallhaven":
        return WallhavenSource()
    if name == "nasa":
        return NasaSource(api_key)
    if name == "pexels":
        return PexelsSource(api_key)
    if name == "unsplash":
        return UnsplashSource(api_key)
    raise ValueError(f"Unknown source: {name}")
