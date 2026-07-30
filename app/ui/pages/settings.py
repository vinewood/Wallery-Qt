"""Settings page (spec §2.6, §7, §10.2)."""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QFileDialog, QHBoxLayout, QLabel, QSlider,
                              QVBoxLayout, QWidget)

from app.config import get_config
from app.i18n import t
from PySide6.QtWidgets import QVBoxLayout as VBoxLayout
from qfluentwidgets import (BodyLabel, CardWidget, ComboBox, FluentIcon as FIF,
                           PrimaryPushButton, PushButton, StrongBodyLabel,
                           SwitchButton)


class SettingsPage(QWidget):
    def __init__(self, app, parent=None):
        super().__init__(parent)
        self.app = app
        root = QVBoxLayout(self)
        root.setContentsMargins(20, 16, 20, 16)
        root.setSpacing(14)

        root.addWidget(StrongBodyLabel(t("settings.title")))

        scroll = WidgetScroll(self)
        body = QWidget()
        vbox = VBoxLayout(body)
        vbox.setSpacing(14)
        scroll.setWidget(body)
        root.addWidget(scroll, 1)

        vbox.addWidget(self._build_schedule_card())
        vbox.addWidget(self._build_download_card())
        vbox.addWidget(self._build_appearance_card())
        vbox.addWidget(self._build_update_card())
        vbox.addStretch(1)

    # -- schedule ----------------------------------------------------------
    def _build_schedule_card(self) -> CardWidget:
        cfg = get_config()
        sched = cfg.get_schedule()
        card = CardWidget(self)
        v = VBoxLayout(card)
        v.setContentsMargins(16, 16, 16, 16)
        v.addWidget(StrongBodyLabel(t("settings.schedule")))

        # time slider
        time_row = QHBoxLayout()
        self.timeSlider = QSlider()
        self.timeSlider.setOrientation(Qt.Orientation.Horizontal)
        self.timeSlider.setRange(0, 1440)
        self.timeSlider.setValue(sched.get("hour", 10) * 60 + sched.get("minute", 0))
        self.timeLabel = QLabel()
        self.timeLabel.setFixedWidth(90)
        self.timeLabel.setStyleSheet("color:#e8eaed;")
        self._update_time_label(self.timeSlider.value())
        self.timeSlider.valueChanged.connect(self._on_time)
        time_row.addWidget(self.timeSlider, 1)
        time_row.addWidget(self.timeLabel)
        v.addLayout(time_row)

        # desktop / lock / autostart switches
        self.swDesktop = _switch_row(v, t("settings.set_desktop"),
                                     sched.get("set_desktop", True),
                                     lambda c: cfg.set_schedule(set_desktop=c))
        if cfg.get("set_lock_screen") is not None or _is_win():
            self.swLock = _switch_row(
                v, t("settings.set_lock_screen"),
                sched.get("set_lock_screen", _is_win()),
                lambda c: cfg.set_schedule(set_lock_screen=c))
        self.swAuto = _switch_row(v, t("settings.auto_start"),
                                  cfg.get_auto_start(),
                                  lambda c: self.app.set_autostart(c))

        # frequency combo
        freq_row = QHBoxLayout()
        freq_row.addWidget(BodyLabel(t("settings.frequency")))
        self.freqCombo = ComboBox()
        freq_map = [("daily", t("settings.freq_daily")),
                    ("12h", t("settings.freq_12h")),
                    ("6h", t("settings.freq_6h")),
                    ("1h", t("settings.freq_1h"))]
        for key, label in freq_map:
            self.freqCombo.addItem(label, key)
        idx = self.freqCombo.findData(sched.get("frequency", "daily"))
        if idx >= 0:
            self.freqCombo.setCurrentIndex(idx)
        self.freqCombo.currentIndexChanged.connect(
            lambda i: cfg.set_schedule(frequency=self.freqCombo.itemData(i)))
        freq_row.addWidget(self.freqCombo, 1)
        v.addLayout(freq_row)

        # update now
        now_btn = PrimaryPushButton(t("settings.update_now"))
        now_btn.clicked.connect(self.app.request_next)
        v.addWidget(now_btn)
        return card

    def _on_time(self, minutes: int):
        self._update_time_label(minutes)
        h = minutes // 60
        m = minutes % 60
        get_config().set_schedule(hour=h, minute=m)

    def _update_time_label(self, minutes: int):
        h24 = minutes // 60
        m = minutes % 60
        ampm = "AM" if h24 < 12 else "PM"
        h12 = h24 % 12
        if h12 == 0:
            h12 = 12
        self.timeLabel.setText(f"{h12}:{m:02d} {ampm}")

    # -- download ----------------------------------------------------------
    def _build_download_card(self) -> CardWidget:
        cfg = get_config()
        card = CardWidget(self)
        v = VBoxLayout(card)
        v.setContentsMargins(16, 16, 16, 16)
        v.addWidget(StrongBodyLabel(t("settings.download")))

        path_row = QHBoxLayout()
        path_row.addWidget(BodyLabel(t("settings.download_path")))
        self.pathLabel = QLabel()
        self.pathLabel.setStyleSheet("color:#9aa0ab;")
        self._refresh_path_label()
        change = PushButton(t("settings.change"))
        change.clicked.connect(self._change_path)
        path_row.addWidget(self.pathLabel, 1)
        path_row.addWidget(change)
        v.addLayout(path_row)

        _switch_row(v, t("settings.open_after"),
                    cfg.get("open_folder_after_download", True),
                    lambda c: cfg.set("open_folder_after_download", c))
        return card

    def _refresh_path_label(self):
        p = get_config().get_download_path()
        self.pathLabel.setText(str(p))

    def _change_path(self):
        d = QFileDialog.getExistingDirectory(self, t("settings.change"),
                                             str(get_config().get_download_path()))
        if d:
            get_config().set_download_path(d)
            self._refresh_path_label()

    # -- appearance (language + theme) ------------------------------------
    def _build_appearance_card(self) -> CardWidget:
        cfg = get_config()
        card = CardWidget(self)
        v = VBoxLayout(card)
        v.setContentsMargins(16, 16, 16, 16)
        v.addWidget(StrongBodyLabel(t("settings.theme")))

        lang_row = QHBoxLayout()
        lang_row.addWidget(BodyLabel(t("settings.language")))
        self.langCombo = ComboBox()
        for key, label in (("auto", t("settings.theme_auto")),
                           ("zh", "中文"), ("en", "English")):
            self.langCombo.addItem(label, key)
        idx = self.langCombo.findData(cfg.get_language())
        if idx >= 0:
            self.langCombo.setCurrentIndex(idx)
        self.langCombo.currentIndexChanged.connect(self._on_language)
        lang_row.addWidget(self.langCombo, 1)
        v.addLayout(lang_row)

        theme_row = QHBoxLayout()
        theme_row.addWidget(BodyLabel(t("settings.theme")))
        self.themeCombo = ComboBox()
        for key, label in (("dark", t("settings.theme_dark")),
                           ("light", t("settings.theme_light")),
                           ("auto", t("settings.theme_auto"))):
            self.themeCombo.addItem(label, key)
        idx = self.themeCombo.findData(cfg.get("theme", "dark"))
        if idx >= 0:
            self.themeCombo.setCurrentIndex(idx)
        self.themeCombo.currentIndexChanged.connect(self._on_theme)
        theme_row.addWidget(self.themeCombo, 1)
        v.addLayout(theme_row)
        return card

    def _on_language(self, i):
        get_config().set_language(self.langCombo.itemData(i))
        from app.i18n import reload_language
        reload_language()
        self.app.show_toast(t("common.need_restart"), success=False)

    def _on_theme(self, i):
        theme = self.themeCombo.itemData(i)
        get_config().set("theme", theme)
        self.app.apply_theme(theme)

    # -- update ------------------------------------------------------------
    def _build_update_card(self) -> CardWidget:
        card = CardWidget(self)
        v = VBoxLayout(card)
        v.setContentsMargins(16, 16, 16, 16)
        v.addWidget(StrongBodyLabel(t("settings.update")))
        info = self.app.check_update()
        label = QLabel(info)
        label.setStyleSheet("color:#9aa0ab;")
        v.addWidget(label)
        return card


def _switch_row(layout, title: str, checked: bool, on_change) -> SwitchButton:
    row = QHBoxLayout()
    row.addWidget(BodyLabel(title))
    sw = SwitchButton()
    sw.setChecked(bool(checked))
    sw.checkedChanged.connect(on_change)
    row.addStretch(1)
    row.addWidget(sw)
    layout.addLayout(row)
    return sw


def _is_win() -> bool:
    import sys
    return sys.platform == "win32"


class WidgetScroll(QWidget):
    """Thin wrapper so the same pattern works; real scroll handled by QScrollArea."""
    def __init__(self, parent=None):
        super().__init__(parent)
        from PySide6.QtWidgets import QScrollArea
        self._sa = QScrollArea(self)
        self._sa.setWidgetResizable(True)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._sa)

    def setWidget(self, w):
        self._sa.setWidget(w)
