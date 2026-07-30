"""Categories page (spec §2.5)."""
from __future__ import annotations

from PySide6.QtWidgets import (QHBoxLayout, QLabel, QPushButton, QScrollArea,
                              QVBoxLayout, QWidget)

from app.config import SOURCE_META, get_config
from app.i18n import t
from PySide6.QtWidgets import QVBoxLayout as VBoxLayout
from qfluentwidgets import BodyLabel, LineEdit, PrimaryPushButton, PushButton, StrongBodyLabel


class CategoriesPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        root.addWidget(StrongBodyLabel(t("categories.title")))

        # add row
        add_row = QHBoxLayout()
        self.input = LineEdit()
        self.input.setPlaceholderText(t("categories.placeholder"))
        self.input.returnPressed.connect(self._add)
        add_btn = PrimaryPushButton(t("categories.add"))
        add_btn.clicked.connect(self._add)
        add_row.addWidget(self.input, 1)
        add_row.addWidget(add_btn)
        root.addLayout(add_row)

        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        body = QWidget()
        self.vbox = VBoxLayout(body)
        self.vbox.setSpacing(14)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        self._build_mine()
        self._build_suggestions("wallhaven", t("categories.wallhaven"), 12)
        self._build_suggestions("pexels", t("categories.pexels"), 10)
        self._build_suggestions("unsplash", t("categories.unsplash"), 8)

    # -- my categories -----------------------------------------------------
    def _build_mine(self):
        self.mineLabel = BodyLabel(t("categories.mine"))
        self.mineLabel.setStyleSheet("color:#9aa0ab;")
        self.vbox.addWidget(self.mineLabel)
        self.mineWidget = QWidget()
        self.mineLayout = FlowLite(self.mineWidget)
        self.vbox.addWidget(self.mineWidget)
        self._refresh_mine()

    def _refresh_mine(self):
        while self.mineLayout.count():
            w = self.mineLayout.takeAt(0).widget()
            if w:
                w.deleteLater()
        for cat in get_config().get_categories():
            btn = QPushButton(cat)
            btn.setFixedHeight(30)
            btn.setStyleSheet(
                "QPushButton{background:rgba(91,156,245,0.18);color:#cfe0fb;"
                "border:none;border-radius:15px;padding:0 8px 0 14px;}")
            remove = QPushButton("×")
            remove.setFixedSize(20, 20)
            remove.setStyleSheet(
                "QPushButton{background:transparent;color:#ff8a8a;border:none;"
                "font-size:14px;}")
            remove.clicked.connect(lambda _=False, c=cat: self._remove(c))
            row = QWidget()
            rl = QHBoxLayout(row)
            rl.setContentsMargins(0, 0, 4, 0)
            rl.setSpacing(2)
            rl.addWidget(btn)
            rl.addWidget(remove)
            self.mineLayout.addWidget(row)

    # -- suggestions -------------------------------------------------------
    def _build_suggestions(self, source: str, title: str, limit: int):
        self.vbox.addWidget(BodyLabel(f"{t('categories.suggestions')} · {title}"))
        box = QWidget()
        fl = FlowLite(box)
        for cat in SOURCE_META[source]["hot_categories"][:limit]:
            btn = QPushButton(cat)
            btn.setFixedHeight(30)
            btn.setStyleSheet(
                "QPushButton{background:rgba(255,255,255,0.08);color:#cfd3da;"
                "border:none;border-radius:15px;padding:0 14px;}"
                "QPushButton:hover{background:rgba(255,255,255,0.16);}")
            btn.clicked.connect(lambda _=False, c=cat: self._add_cat(c))
            fl.addWidget(btn)
        self.vbox.addWidget(box)

    # -- actions -----------------------------------------------------------
    def _add(self):
        self._add_cat(self.input.text())
        self.input.clear()

    def _add_cat(self, cat: str):
        if get_config().add_category(cat):
            self._refresh_mine()
            self.app.show_toast(t("categories.added"), success=True)
        else:
            self.app.show_toast(t("categories.exists"), success=False)

    def _remove(self, cat: str):
        get_config().remove_category(cat)
        self._refresh_mine()
        self.app.show_toast(t("categories.removed"), success=True)


class FlowLite(QHBoxLayout):
    """Simple horizontal wrapping-ish layout (chips row, scrolls if long)."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setSpacing(8)
