"""Shared HTTP helpers.

All requests send ``User-Agent: Wallery/1.0`` per spec §3.
"""
from __future__ import annotations

import requests

USER_AGENT = "Wallery/1.0"
_TIMEOUT = 15


def _headers(extra=None):
    h = {"User-Agent": USER_AGENT}
    if extra:
        h.update(extra)
    return h


def get_text(url: str, params=None, headers=None, timeout=_TIMEOUT) -> str:
    r = requests.get(url, params=params, headers=_headers(headers),
                     timeout=timeout)
    r.raise_for_status()
    return r.text


def get_json(url: str, params=None, headers=None, timeout=_TIMEOUT):
    r = requests.get(url, params=params, headers=_headers(headers),
                     timeout=timeout)
    r.raise_for_status()
    return r.json()


def get_bytes(url: str, headers=None, timeout=_TIMEOUT) -> bytes:
    r = requests.get(url, headers=_headers(headers), timeout=timeout)
    r.raise_for_status()
    return r.content


def ext_from_url(url: str, default: str = "jpg") -> str:
    """Best-effort file extension from a URL."""
    if not url:
        return default
    path = url.split("?")[0].split("#")[0]
    if "." in path:
        ext = path.rsplit(".", 1)[-1].lower()
        if 1 <= len(ext) <= 5 and ext.isalnum():
            return ext
    return default
