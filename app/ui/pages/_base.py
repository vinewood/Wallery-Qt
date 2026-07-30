"""Shared helpers for pages: a scrollable grid area with FlowLayout."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QScrollArea, QVBoxLayout, QWidget

from app.ui.widgets.flow_layout import FlowLayout


class PageBase(QWidget):
    """Base for content pages that show a responsive wallpaper grid."""

    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 16, 20, 16)
        self._layout.setSpacing(12)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.grid = QWidget()
        self.flow = FlowLayout(self.grid, margin=6, hspacing=12, vspacing=12)
        self.grid.setLayout(self.flow)
        self.scroll.setWidget(self.grid)
        self._layout.addWidget(self.scroll, 1)

    # -- grid management ---------------------------------------------------
    def clear_grid(self):
        while self.flow.count():
            item = self.flow.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

    def add_widget(self, widget: QWidget):
        self.flow.addWidget(widget)

    def set_title(self, widget: QWidget):
        self._layout.insertWidget(0, widget)
