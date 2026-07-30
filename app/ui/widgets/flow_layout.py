"""A self-contained flow layout (responsive grid) — avoids depending on a
specific QFluentWidgets layout export.
"""
from __future__ import annotations

from PySide6.QtCore import QPoint, QRect, QSize, Qt
from PySide6.QtWidgets import QLayout, QSizePolicy, QWidget


class FlowLayout(QLayout):
    def __init__(self, parent: QWidget = None, margin: int = 8, hspacing: int = 10,
                 vspacing: int = 10):
        super().__init__(parent)
        self._margin = margin
        self._hspacing = hspacing
        self._vspacing = vspacing
        self._items = []

    def addItem(self, item):
        self._items.append(item)

    def count(self):
        return len(self._items)

    def itemAt(self, index):
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self._items):
            return self._items.pop(index)
        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width: int) -> int:
        return self._do_layout(QRect(0, 0, width, 0), False)

    def setGeometry(self, rect: QRect):
        super().setGeometry(rect)
        self._do_layout(rect, True)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self._items:
            size = size.expandedTo(item.minimumSize())
        left, top, right, bottom = self._get_margins()
        size += QSize(left + right, top + bottom)
        return size

    def _get_margins(self):
        if self.parent() is not None:
            return (self._margin, self._margin, self._margin, self._margin)
        return (0, 0, 0, 0)

    def _do_layout(self, rect: QRect, apply: bool):
        left, top, right, bottom = self._get_margins()
        x = rect.x() + left
        y = rect.y() + top
        line_height = 0
        for item in self._items:
            w = item.sizeHint().width()
            h = item.sizeHint().height()
            next_x = x + w + self._hspacing
            if next_x - self._hspacing > rect.right() - right and line_height > 0:
                x = rect.x() + left
                y = y + line_height + self._vspacing
                next_x = x + w + self._hspacing
                line_height = 0
            if apply:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            x = next_x
            line_height = max(line_height, h)

        if not self._items:
            return rect.height()
        return y + line_height + bottom - rect.y()
