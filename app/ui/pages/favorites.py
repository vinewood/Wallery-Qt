"""Favorites page (spec §2.3)."""
from __future__ import annotations

from typing import Dict, List

from PySide6.QtWidgets import QLabel

from app.config import SOURCE_META
from app.favorites import get_all, is_favorited
from app.i18n import t
from app.ui.pages._base import PageBase
from app.ui.widgets.wallpaper_card import WallpaperCard


class FavoritesPage(PageBase):
    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        self.titleLabel = QLabel()
        self.titleLabel.setStyleSheet("font-size:20px;font-weight:bold;color:#e8eaed;")
        self._layout.insertWidget(0, self.titleLabel)

        self.emptyLabel = QLabel(t("favorites.empty"))
        self.emptyLabel.setStyleSheet("color:#9aa0ab;")
        self._layout.insertWidget(1, self.emptyLabel)

        app.favorites_changed.connect(self.refresh)
        self.refresh()

    def refresh(self):
        items = get_all()
        self.titleLabel.setText(t("favorites.title", len(items)))
        self.emptyLabel.setVisible(len(items) == 0)
        self.clear_grid()
        for it in items:
            meta = SOURCE_META.get(it.get("source", ""), {})
            card = WallpaperCard(
                it, meta.get("brand", "#5b9cf5"), meta.get("abbr", "?"),
                self._card_callbacks(), self.grid)
            self.add_widget(card)

    def _card_callbacks(self) -> Dict:
        return {
            "on_set": self.app.set_wallpaper_from_item,
            "on_download": self.app.download_item,
            "on_toggle_favorite": self.app.toggle_favorite,
            "is_favorited": is_favorited,
        }
