"""Browse page (spec §2.2)."""
from __future__ import annotations

from typing import Dict, List

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QIcon, QPixmap, QTransform
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QScrollArea,
                              QWidget)
from qfluentwidgets import ComboBox, FluentIcon as FIF, ToolButton

from app.config import SOURCE_META, SOURCE_ORDER, get_config
from app.favorites import is_favorited
from app.i18n import t
from app.ui.pages._base import PageBase
from app.ui.widgets.wallpaper_card import WallpaperCard

_LOADING_DOTS = ["", ".", "..", "..."]

# Expected items per page per source (used to decide if a "next" page exists).
_PAGE_SIZE = {
    "bing": 8,
    "wallhaven": 24,
    "nasa": 12,
    "pexels": 15,
    "unsplash": 20,
}


class BrowsePage(PageBase):
    def __init__(self, app, parent=None):
        super().__init__(app, parent)
        self.current_source = get_config().get_last_selected_source()
        self.current_category = "all"
        self.current_page = 1
        self._build_header()
        self._build_chips()
        self._build_loading()
        self._build_pagination()

        mgr = app.manager
        mgr.list_loaded.connect(self._on_list_loaded)
        mgr.list_error.connect(self._on_list_error)

        self._refresh_chips()
        self._load_cold_cache()
        self._fetch_current()

    # -- header ------------------------------------------------------------
    def _build_header(self):
        header = QWidget(self)
        h = QHBoxLayout(header)
        h.setContentsMargins(0, 0, 0, 0)

        self.srcCombo = ComboBox()
        for name in SOURCE_ORDER:
            self.srcCombo.addItem(SOURCE_META[name]["display_name"], name)
        # select current
        idx = self.srcCombo.findData(self.current_source)
        if idx >= 0:
            self.srcCombo.setCurrentIndex(idx)
        self.srcCombo.currentIndexChanged.connect(
            lambda i: self._on_source_changed(self.srcCombo.itemData(i)))

        self.countLabel = QLabel(t("browse.count", 0))
        self.countLabel.setStyleSheet("color:#9aa0ab;")

        self.refreshBtn = ToolButton(FIF.SYNC)
        self.refreshBtn.setToolTip(t("browse.refresh"))
        self.refreshBtn.clicked.connect(self._on_refresh)

        h.addWidget(QLabel("来源"))
        h.addWidget(self.srcCombo)
        h.addSpacing(12)
        h.addWidget(self.countLabel)
        h.addStretch(1)
        h.addWidget(self.refreshBtn)
        self._layout.insertWidget(0, header)

        self._spin_timer = QTimer(self)
        self._spin_angle = 0
        self._spin_timer.timeout.connect(self._spin)
        self._base_icon = self.refreshBtn.icon()

    def _spin(self):
        self._spin_angle = (self._spin_angle + 30) % 360
        pm = QPixmap(self._base_icon.pixmap(20, 20))
        if pm.isNull():
            return
        tr = QTransform().rotate(self._spin_angle)
        pm = pm.transformed(tr, Qt.SmoothTransformation)
        self.refreshBtn.setIcon(QIcon(pm))

    # -- chips -------------------------------------------------------------
    def _build_chips(self):
        self.chipsScroll = QScrollArea(self)
        self.chipsScroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.chipsScroll.setFixedHeight(40)
        self.chipsScroll.setWidgetResizable(True)
        self.chipsWidget = QWidget()
        self.chipsLayout = QHBoxLayout(self.chipsWidget)
        self.chipsLayout.setContentsMargins(0, 0, 0, 0)
        self.chipsLayout.setSpacing(8)
        self.chipsScroll.setWidget(self.chipsWidget)
        self._layout.insertWidget(1, self.chipsScroll)
        self._chip_buttons: List[QPushButton] = []

    def _refresh_chips(self):
        for b in self._chip_buttons:
            b.deleteLater()
        self._chip_buttons.clear()

        cats = SOURCE_META[self.current_source]["hot_categories"][:12]
        chips = [("all", t("common.all"))] + [(c, c) for c in cats]
        for key, label in chips:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setFixedHeight(30)
            btn.setStyleSheet(self._chip_style(key == self.current_category))
            btn.clicked.connect(lambda _=False, k=key: self._on_chip(k))
            self._chip_buttons.append(btn)
            self.chipsLayout.addWidget(btn)

    def _chip_style(self, selected: bool) -> str:
        if selected:
            return ("QPushButton{background:#5b9cf5;color:#fff;border:none;"
                    "border-radius:15px;padding:0 14px;}"
                    "QPushButton:hover{background:#4a8be0;}")
        return ("QPushButton{background:rgba(255,255,255,0.08);color:#cfd3da;"
                "border:none;border-radius:15px;padding:0 14px;}"
                "QPushButton:hover{background:rgba(255,255,255,0.16);}")

    # -- loading -----------------------------------------------------------
    def _build_loading(self):
        self.loadingLabel = QLabel("")
        self.loadingLabel.setStyleSheet("color:#9aa0ab;")
        self._layout.insertWidget(2, self.loadingLabel)
        self._dot_timer = QTimer(self)
        self._dot_idx = 0
        self._dot_timer.timeout.connect(self._pulse)
        self._loading_on = False

    def _pulse(self):
        self._dot_idx = (self._dot_idx + 1) % len(_LOADING_DOTS)
        dn = SOURCE_META[self.current_source]["display_name"]
        self.loadingLabel.setText(t("browse.loading", dn) + _LOADING_DOTS[self._dot_idx])

    def _set_loading(self, on: bool):
        self._loading_on = on
        if on:
            self._dot_idx = 0
            self._dot_timer.start(400)
            self._spin_timer.start(80)
            self.refreshBtn.setEnabled(False)
        else:
            self._dot_timer.stop()
            self._spin_timer.stop()
            self.loadingLabel.setText("")
            self.refreshBtn.setEnabled(True)
            self.refreshBtn.setIcon(self._base_icon)

    # -- actions -----------------------------------------------------------
    def _on_source_changed(self, name: str):
        if name == self.current_source:
            return
        self.current_source = name
        get_config().set_last_selected_source(name)
        self.current_category = "all"
        self.current_page = 1
        self._refresh_chips()
        self._fetch_current()

    def _on_chip(self, key: str):
        self.current_category = key
        self.current_page = 1
        for b in self._chip_buttons:
            b.setStyleSheet(self._chip_style(False))
        # highlight active
        for b in self._chip_buttons:
            if b.text() == (t("common.all") if key == "all" else key):
                b.setStyleSheet(self._chip_style(True))
                break
        self._fetch_current()

    def _on_refresh(self):
        self._fetch_current()

    # -- pagination (spec §2.2) -------------------------------------------
    def _build_pagination(self):
        self.paginationWidget = QWidget(self)
        h = QHBoxLayout(self.paginationWidget)
        h.setContentsMargins(0, 6, 0, 6)

        self.prevBtn = QPushButton(t("browse.prev"))
        self.prevBtn.clicked.connect(self._on_prev)
        self.nextBtn = QPushButton(t("browse.next"))
        self.nextBtn.clicked.connect(self._on_next)

        self.pageBtnWidget = QWidget()
        self.pageBtnLayout = QHBoxLayout(self.pageBtnWidget)
        self.pageBtnLayout.setContentsMargins(0, 0, 0, 0)
        self.pageBtnLayout.setSpacing(6)

        h.addStretch(1)
        h.addWidget(self.prevBtn)
        h.addWidget(self.pageBtnWidget)
        h.addWidget(self.nextBtn)
        h.addStretch(1)
        self._layout.addWidget(self.paginationWidget)

    def _refresh_pagination(self, items_len: int):
        has_prev = self.current_page > 1
        has_next = items_len >= _PAGE_SIZE.get(self.current_source, 15)
        self.prevBtn.setEnabled(has_prev)
        self.nextBtn.setEnabled(has_next)
        self._rebuild_page_buttons(has_next)

    def _rebuild_page_buttons(self, has_next: bool):
        while self.pageBtnLayout.count():
            item = self.pageBtnLayout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        start = max(1, self.current_page - 2)
        buttons = []
        if start > 1:
            buttons.append(("1", 1))
            buttons.append(("…", None))
        for p in range(start, start + 5):
            buttons.append((str(p), p))
        if has_next:
            buttons.append(("…", None))
        for label, pnum in buttons:
            if pnum is None:
                lbl = QLabel(label)
                lbl.setStyleSheet("color:#9aa0ab;padding:0 4px;")
                self.pageBtnLayout.addWidget(lbl)
            else:
                b = QPushButton(label)
                b.setFixedSize(34, 30)
                b.setStyleSheet(self._page_btn_style(pnum == self.current_page))
                if pnum != self.current_page:
                    b.clicked.connect(lambda _=False, n=pnum: self._on_page(n))
                self.pageBtnLayout.addWidget(b)

    def _page_btn_style(self, selected: bool) -> str:
        if selected:
            return ("QPushButton{background:#5b9cf5;color:#fff;border:none;"
                    "border-radius:6px;}")
        return ("QPushButton{background:rgba(255,255,255,0.08);color:#cfd3da;"
                "border:none;border-radius:6px;}"
                "QPushButton:hover{background:rgba(255,255,255,0.16);}")

    def _on_prev(self):
        if self.current_page > 1:
            self.current_page -= 1
            self._fetch_current()

    def _on_next(self):
        self.current_page += 1
        self._fetch_current()

    def _on_page(self, n: int):
        self.current_page = n
        self._fetch_current()

    # -- data --------------------------------------------------------------
    def _load_cold_cache(self):
        items = get_config().load_cache()
        if items:
            self._populate(items)
            self.countLabel.setText(t("browse.count", len(items)))

    def _fetch_current(self):
        self._set_loading(True)
        self.app.manager.fetch_list_async(
            self.current_source, self.current_category, self.current_page)

    def _on_list_loaded(self, name, category, page, items):
        if name != self.current_source or category != self.current_category \
           or page != self.current_page:
            return
        self._set_loading(False)
        if not items:
            self._populate_placeholder()
            self.countLabel.setText(t("browse.count", 0))
            self._refresh_pagination(0)
            return
        get_config().save_cache(items)
        self._populate(items)
        self.countLabel.setText(t("browse.count", len(items)))
        self._refresh_pagination(len(items))

    def _on_list_error(self, name, err):
        if name != self.current_source:
            return
        self._set_loading(False)
        # fall back to placeholder cards so the page is never empty
        self._populate_placeholder()
        self._refresh_pagination(0)

    def _populate(self, items: List[Dict]):
        self.clear_grid()
        for it in items:
            meta = SOURCE_META.get(it.get("source", ""), {})
            card = WallpaperCard(
                it, meta.get("brand", "#5b9cf5"), meta.get("abbr", "?"),
                self._card_callbacks(), self.grid)
            self.add_widget(card)

    def _populate_placeholder(self, n: int = 21):
        self.clear_grid()
        for _ in range(n):
            meta = SOURCE_META[self.current_source]
            card = WallpaperCard(
                {"id": f"ph-{_}", "url": "", "source": self.current_source,
                 "display_name": meta["display_name"]},
                meta["brand"], meta["abbr"], self._card_callbacks(), self.grid)
            self.add_widget(card)

    def _card_callbacks(self) -> Dict:
        return {
            "on_set": self.app.set_wallpaper_from_item,
            "on_download": self.app.download_item,
            "on_toggle_favorite": self.app.toggle_favorite,
            "is_favorited": is_favorited,
        }
