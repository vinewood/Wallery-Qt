"""Sources page (spec §2.4)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QVBoxLayout, QWidget)

from app.config import SOURCE_META, SOURCE_ORDER, get_config
from app.i18n import t
from PySide6.QtWidgets import QVBoxLayout as VBoxLayout
from qfluentwidgets import (BodyLabel, CardWidget, FluentIcon as FIF,
                           PasswordLineEdit, StrongBodyLabel, SwitchButton)


class SourcesPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        from PySide6.QtWidgets import QScrollArea
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(12)

        title = StrongBodyLabel(t("sources.title"))
        title.setStyleSheet("font-size:20px;")
        root.addWidget(title)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        body = QWidget()
        vbox = VBoxLayout(body)
        vbox.setSpacing(12)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        self._key_inputs = {}
        for name in SOURCE_ORDER:
            vbox.addWidget(self._build_source_card(name))
        vbox.addStretch(1)

        self._build_api_key_section(root)

    # -- source card -------------------------------------------------------
    def _build_source_card(self, name: str) -> CardWidget:
        meta = SOURCE_META[name]
        card = CardWidget(self)
        h = QHBoxLayout(card)
        h.setContentsMargins(16, 16, 16, 16)
        h.setSpacing(14)

        badge = QLabel(meta["abbr"])
        badge.setFixedSize(56, 56)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setStyleSheet(
            f"background:{meta['brand']};color:#fff;border-radius:12px;"
            f"font-weight:bold;font-size:18px;")

        col = QVBoxLayout()
        col.setSpacing(2)
        row1 = QHBoxLayout()
        row1.addWidget(StrongBodyLabel(meta["display_name"]))
        if name in ("bing", "wallhaven", "nasa"):
            tag = QLabel(t("sources.default"))
            tag.setStyleSheet("color:#5b9cf5;font-size:12px;")
            row1.addWidget(tag)
        row1.addStretch(1)
        col.addLayout(row1)
        col.addWidget(BodyLabel(meta["desc"]))
        h.addLayout(col, 1)

        sw = SwitchButton()
        sw.setChecked(get_config().is_source_enabled(name))
        sw.checkedChanged.connect(
            lambda c, n=name: get_config().set_source_enabled(n, c))
        h.addWidget(sw)
        return card

    # -- api key section ---------------------------------------------------
    def _build_api_key_section(self, root: QVBoxLayout):
        section = CardWidget(self)
        v = VBoxLayout(section)
        v.setContentsMargins(16, 16, 16, 16)
        v.addWidget(StrongBodyLabel(t("sources.api_key")))
        for name in ("pexels", "unsplash", "nasa"):
            meta = SOURCE_META[name]
            label = BodyLabel(f"{meta['display_name']} API Key")
            inp = PasswordLineEdit()
            inp.setPlaceholderText(
                t("sources.api_key_placeholder", meta["display_name"]))
            saved = get_config().get_api_key(name)
            if saved:
                inp.setText("•" * min(len(saved), 12))
                inp.setPlaceholderText("•••••")
            inp.editingFinished.connect(
                lambda n=name, w=inp: self._save_key(n, w))
            v.addWidget(label)
            v.addWidget(inp)
            self._key_inputs[name] = inp
        root.addWidget(section)

    def _save_key(self, name: str, widget: PasswordLineEdit):
        # Only persist if the user typed something real (not the mask)
        text = widget.text().strip()
        if text and set(text) == {"•"}:
            return
        get_config().set_api_key(name, text)
        self.app.show_toast(t("sources.saved", SOURCE_META[name]["display_name"]),
                           success=True)
        if text:
            widget.setText("•" * min(len(text), 12))
            widget.setPlaceholderText("•••••")
