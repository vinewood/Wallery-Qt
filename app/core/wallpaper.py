"""Set desktop / lock-screen wallpaper on Windows via ctypes & registry.

``set_desktop_wallpaper`` is the primary, required behaviour (equivalent to
the original Rust ``wallpaper`` crate). Lock-screen writing is best-effort
and never fatal.
"""
from __future__ import annotations

import ctypes
import sys
from typing import Tuple


def set_desktop_wallpaper(path: str) -> bool:
    """Set the desktop wallpaper using ``SystemParametersInfoW``.

    Returns True on success. Windows only; on other platforms returns False.
    """
    if sys.platform != "win32":
        return False
    SPI_SETDESKWALLPAPER = 20
    SPIF_UPDATEINIFILE = 0x01
    SPIF_SENDCHANGE = 0x02
    try:
        ok = ctypes.windll.user32.SystemParametersInfoW(
            SPI_SETDESKWALLPAPER, 0, path, SPIF_UPDATEINIFILE | SPIF_SENDCHANGE
        )
        return bool(ok)
    except Exception:
        return False


def set_lock_screen_wallpaper(path: str) -> bool:
    """Best-effort lock-screen wallpaper via registry (Windows only)."""
    if sys.platform != "win32":
        return False
    try:
        import winreg
        # Control Panel desktop key (used by some Windows versions)
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Control Panel\Desktop",
            0,
            winreg.KEY_SET_VALUE,
        ) as key:
            winreg.SetValueEx(key, "LockScreenImage", 0, winreg.REG_SZ, path)
        # Personalization overlay path
        with winreg.CreateKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Personalization\LockScreenOverlays",
        ) as key:
            winreg.SetValueEx(key, "LockScreenImagePath", 0, winreg.REG_SZ, path)
        return True
    except Exception:
        return False


def set_wallpaper(path: str, set_desktop: bool = True,
                  set_lock_screen: bool = False) -> Tuple[bool, bool]:
    """Apply a local image as wallpaper.

    Returns ``(desktop_ok, lockscreen_ok)``.
    """
    desk = set_desktop_wallpaper(path) if set_desktop else True
    lock = set_lock_screen_wallpaper(path) if set_lock_screen else True
    return desk, lock
