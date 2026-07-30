"""Asynchronous thumbnail loading via QThreadPool (spec §2.2, §10.3)."""
from __future__ import annotations

from PySide6.QtCore import QObject, QRunnable, QThreadPool, Qt, Signal
from PySide6.QtGui import QImage, QPixmap

from app.core.http import USER_AGENT, get_bytes

_THUMB_POOL = QThreadPool()
_THUMB_POOL.setMaxThreadCount(8)


class ThumbLoadSignals(QObject):
    loaded = Signal(QPixmap)


class ThumbnailTask(QRunnable):
    def __init__(self, url: str, width: int, height: int, signals: ThumbLoadSignals):
        super().__init__()
        self.url = url
        self.width = width
        self.height = height
        self.signals = signals

    def run(self):
        try:
            data = get_bytes(self.url)
            img = QImage()
            if img.loadFromData(data):
                pix = QPixmap.fromImage(img)
                if not pix.isNull():
                    pix = pix.scaled(
                        self.width, self.height,
                        Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                        Qt.TransformationMode.SmoothTransformation,
                    )
                    self.signals.loaded.emit(pix)
        except Exception:
            pass


def load_thumbnail(url: str, width: int, height: int,
                   on_loaded) -> ThumbLoadSignals:
    """Kick off a thumbnail download; ``on_loaded(pixmap)`` runs on UI thread."""
    signals = ThumbLoadSignals()
    signals.loaded.connect(on_loaded)
    task = ThumbnailTask(url, width, height, signals)
    _THUMB_POOL.start(task)
    return signals
