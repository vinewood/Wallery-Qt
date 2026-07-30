"""Wallpaper card widget: thumbnail + hover actions + favorite badge."""
from __future__ import annotations

from typing import Callable, Dict

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QVBoxLayout,
                              QWidget)
from qfluentwidgets import CardWidget, FluentIcon as FIF, ToolButton

from app.ui.widgets.thumbnail_loader import load_thumbnail


def _fi(name):
    """Safely resolve a FluentIcon attribute (fallback to APPLICATION)."""
    return getattr(FIF, name, FIF.APPLICATION)


THUMB_W, THUMB_H = 320, 213  # 3:2


class WallpaperCard(CardWidget):
    def __init__(self, item: Dict, brand: str, abbr: str,
                 callbacks: Dict[str, Callable], parent=None):
        super().__init__(parent)
        self.item = item
        self.brand = brand
        self.abbr = abbr
        self.callbacks = callbacks
        self._thumb_signals = None
        self.setFixedWidth(THUMB_W + 24)
        self._build_ui()
        self._load_thumb()

    # -- UI ----------------------------------------------------------------
    def _build_ui(self):
        self.imageLabel = QLabel(self)
        self.imageLabel.setFixedSize(THUMB_W, THUMB_H)
        self.imageLabel.setPixmap(self._placeholder())
        self.imageLabel.setScaledContents(True)

        self.overlay = QWidget(self.imageLabel)
        self.overlay.setFixedSize(THUMB_W, THUMB_H)
        self.overlay.setStyleSheet("background: rgba(0,0,0,120);")
        self.overlay.hide()

        o_layout = QHBoxLayout(self.overlay)
        o_layout.setContentsMargins(0, 0, 0, 0)
        o_layout.setSpacing(6)
        o_layout.addStretch(1)

        self.setBtn = ToolButton(_fi("DESKTOP"), self.overlay)
        self.favBtn = ToolButton(_fi("HEART"), self.overlay)
        self.dlBtn = ToolButton(_fi("DOWNLOAD"), self.overlay)
        for b in (self.setBtn, self.favBtn, self.dlBtn):
            b.setFixedSize(34, 34)
            b.setToolTip("")
        self.setBtn.setToolTip("设为壁纸")
        self.dlBtn.setToolTip("下载")
        o_layout.addWidget(self.setBtn)
        o_layout.addWidget(self.favBtn)
        o_layout.addWidget(self.dlBtn)

        # source tag (bottom-left of overlay)
        self.srcTag = QLabel(self.overlay)
        self.srcTag.setText(self.item.get("source", "").upper())
        self.srcTag.setStyleSheet(
            "color:#fff;background:rgba(0,0,0,120);padding:2px 6px;border-radius:4px;")
        self.srcTag.move(8, THUMB_H - 26)

        self.setBtn.clicked.connect(lambda: self.callbacks["on_set"](self.item))
        self.dlBtn.clicked.connect(lambda: self.callbacks["on_download"](self.item))
        self.favBtn.clicked.connect(self._toggle_fav)

        # favorite star badge (top-right, always visible when favorited)
        self.star = QLabel(self.imageLabel)
        self.star.setText("★")
        self.star.setStyleSheet("color:#ff4d4f;font-size:18px;")
        self.star.move(THUMB_W - 24, 4)
        self._refresh_star()

        # caption
        caption = QLabel(self.item.get("attribution", "") or self.item.get("display_name", ""))
        caption.setMaximumWidth(THUMB_W)
        caption.setWordWrap(True)
        caption.setStyleSheet("color:#9aa0ab;font-size:12px;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(6)
        layout.addWidget(self.imageLabel)
        layout.addWidget(caption)

    def _refresh_star(self):
        fav = self.callbacks.get("is_favorited", lambda i: False)(self.item)
        self.star.setVisible(bool(fav))

    def _toggle_fav(self):
        now_fav = self.callbacks["on_toggle_favorite"](self.item)
        self._refresh_star()

    # -- thumbnail ---------------------------------------------------------
    def _placeholder(self) -> QPixmap:
        pm = QPixmap(THUMB_W, THUMB_H)
        pm.fill(Qt.GlobalColor.transparent)
        p = QPainter(pm)
        base = QColor(self.brand)
        grad = QLinearGradient(0, 0, THUMB_W, THUMB_H)
        grad.setColorAt(0, base)
        grad.setColorAt(1, base.darker(150))
        p.fillRect(0, 0, THUMB_W, THUMB_H, grad)
        p.setPen(Qt.GlobalColor.white)
        f = QFont()
        f.setBold(True)
        f.setPointSize(30)
        p.setFont(f)
        p.drawText(pm.rect(), Qt.AlignmentFlag.AlignCenter, self.abbr)
        p.end()
        return pm

    def _load_thumb(self):
        url = self.item.get("thumbnail") or self.item.get("url") or ""
        if not url:
            return
        self._thumb_signals = load_thumbnail(
            url, THUMB_W, THUMB_H, self._on_thumb)

    def _on_thumb(self, pix: QPixmap):
        if not pix.isNull():
            self.imageLabel.setPixmap(pix)

    # -- hover -------------------------------------------------------------
    def enterEvent(self, event):
        self.overlay.show()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.overlay.hide()
        super().leaveEvent(event)
