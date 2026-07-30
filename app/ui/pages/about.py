"""About page (spec §2.7)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QHBoxLayout, QLabel, QVBoxLayout, QWidget)

from PySide6.QtWidgets import QVBoxLayout as VBoxLayout
from app.i18n import t
from qfluentwidgets import FluentIcon as FIF, HyperlinkButton, StrongBodyLabel

# Public project links (no secrets). Edit to point at the new repo.
SITE_URL = "https://github.com/moshangjianjia/wallery"
GITHUB_URL = "https://github.com/moshangjianjia/wallery"
GITEE_URL = "https://gitee.com/moshangjianjia/wallery"


class AboutPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)
        root.addStretch(1)

        logo = QLabel("幕间")
        logo.setStyleSheet("font-size:42px;font-weight:bold;color:#5b9cf5;")
        logo.setAlignment(Qt.AlignmentFlag.AlignHCenter)  # AlignHCenter
        root.addWidget(logo)

        name = StrongBodyLabel("Wallery")
        name.setStyleSheet("font-size:18px;")
        name.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(name)

        ver = QLabel(t("app.version"))
        ver.setStyleSheet("color:#9aa0ab;")
        ver.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(ver)

        for key in ("story1", "story2", "story3", "story4"):
            s = QLabel(t(f"about.{key}"))
            s.setWordWrap(True)
            s.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            s.setStyleSheet("color:#cfd3da;max-width:560px;")
            root.addWidget(s)

        # data cards
        stats = [t("about.free"), t("about.open"), t("about.size"), t("about.mem")]
        stats_row = QHBoxLayout()
        for st in stats:
            b = QLabel(st)
            b.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            b.setStyleSheet(
                "background:rgba(91,156,245,0.15);color:#cfe0fb;"
                "border-radius:8px;padding:10px 14px;")
            stats_row.addWidget(b)
        root.addLayout(stats_row)

        # sponsor section (spec §2.7)
        self._build_sponsor(root)

        links = QHBoxLayout()
        links.addStretch(1)
        site = HyperlinkButton(SITE_URL, t("about.site"), self)
        gh = HyperlinkButton(GITHUB_URL, t("about.github"), self)
        ge = HyperlinkButton(GITEE_URL, t("about.gitee"), self)
        links.addWidget(site)
        links.addWidget(gh)
        links.addWidget(ge)
        links.addStretch(1)
        root.addLayout(links)

        root.addStretch(1)

    # -- sponsor -----------------------------------------------------------
    def _build_sponsor(self, root):
        from app.resources import resource_path
        title = StrongBodyLabel(t("about.sponsor"))
        title.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        root.addWidget(title)

        sponsor_img = resource_path("alipay.jpg")
        box = QLabel()
        box.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        if sponsor_img.exists():
            pm = QPixmap(str(sponsor_img))
            if not pm.isNull():
                pm = pm.scaled(170, 170, Qt.AspectRatioMode.KeepAspectRatio,
                               Qt.TransformationMode.SmoothTransformation)
                box.setPixmap(pm)
            else:
                box.setText("Alipay")
        else:
            box.setText("Alipay")
        box.setStyleSheet("background:rgba(255,255,255,0.06);border-radius:8px;"
                          "padding:8px;")
        root.addWidget(box)
