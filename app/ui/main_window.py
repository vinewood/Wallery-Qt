"""Main window: frameless FluentWindow with 6 navigation pages (spec §2)."""
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout

from app.i18n import t
from app.ui.pages.about import AboutPage
from app.ui.pages.browse import BrowsePage
from app.ui.pages.categories import CategoriesPage
from app.ui.pages.favorites import FavoritesPage
from app.ui.pages.settings import SettingsPage
from app.ui.pages.sources_page import SourcesPage
from pathlib import Path
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QWidget
from qfluentwidgets import (FluentIcon as FIF, FluentWindow,
                           NavigationItemPosition)


class MainWindow(FluentWindow):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        self.setWindowTitle(t("app.title"))
        self.resize(1200, 800)
        self.setMinimumSize(800, 600)

        # Custom title bar: brand icon + title + language badge (spec §2.0)
        try:
            tb = self.titleBar
            tb.setTitle("幕间 · Wallery")
            from app.resources import resource_path
            icon_path = resource_path("cube_icon.png")
            if icon_path.exists():
                try:
                    tb.setIcon(QIcon(str(icon_path)))
                except Exception:
                    pass
            try:
                if hasattr(tb, "addWidget"):
                    badge = QLabel("zh-CN")
                    badge.setStyleSheet(
                        "color:#9aa0ab;font-size:11px;padding:2px 8px;"
                        "background:rgba(255,255,255,0.08);border-radius:8px;")
                    tb.addWidget(badge)
            except Exception:
                pass
        except Exception:
            pass

        # Background gradient (spec §10.1)
        self.setStyleSheet(
            "QWidget#browseInterface, QWidget#favoritesInterface, "
            "QWidget#sourcesInterface, QWidget#categoriesInterface, "
            "QWidget#settingsInterface, QWidget#aboutInterface {"
            "background: qlineargradient(x1:0, y1:0, x2:1, y2:1, "
            "stop:0 #3a3f47, stop:0.5 #2d343c, stop:1 #1e2730);}")

        self._init_pages()
        self._add_nav()

    def _init_pages(self):
        self.browsePage = BrowsePage(self.app, self)
        self.favoritesPage = FavoritesPage(self.app, self)
        self.sourcesPage = SourcesPage(self.app, self)
        self.categoriesPage = CategoriesPage(self.app, self)
        self.settingsPage = SettingsPage(self.app, self)
        self.aboutPage = AboutPage(self.app, self)

        self.browseInterface = self._wrap(self.browsePage, "browse")
        self.favoritesInterface = self._wrap(self.favoritesPage, "favorites")
        self.sourcesInterface = self._wrap(self.sourcesPage, "sources")
        self.categoriesInterface = self._wrap(self.categoriesPage, "categories")
        self.settingsInterface = self._wrap(self.settingsPage, "settings")
        self.aboutInterface = self._wrap(self.aboutPage, "about")

    def _wrap(self, widget, name: str) -> QWidget:
        interface = QWidget(self)
        interface.setObjectName(f"{name}Interface")
        layout = QVBoxLayout(interface)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(widget)
        return interface

    def _add_nav(self):
        self.addSubInterface(self.browseInterface, FIF.HOME, t("tabs.browse"),
                            NavigationItemPosition.TOP)
        self.addSubInterface(self.favoritesInterface, FIF.HEART, t("tabs.favorites"),
                            NavigationItemPosition.TOP)
        self.addSubInterface(self.sourcesInterface, FIF.GLOBE, t("tabs.sources"),
                            NavigationItemPosition.SCROLL)
        self.addSubInterface(self.categoriesInterface, FIF.TAG, t("tabs.categories"),
                            NavigationItemPosition.SCROLL)
        self.addSubInterface(self.settingsInterface, FIF.SETTING, t("tabs.settings"),
                            NavigationItemPosition.SCROLL)
        self.addSubInterface(self.aboutInterface, FIF.INFO, t("tabs.about"),
                            NavigationItemPosition.BOTTOM)

    # -- window behaviour (close -> tray) ---------------------------------
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.app.show_toast(t("app.title"), success=True)
