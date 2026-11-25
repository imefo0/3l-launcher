from PySide6.QtWidgets import (
    QLabel,
    QHBoxLayout,
    QCheckBox
    )
from PySide6.QtCore import QSettings
from typing import Any

settings = QSettings("3L", "3L Launcher")

def ensure_defaults() -> None:
    # переместить в конфиг
    defaults = {
        "check_game_upd_on_start": False,
        "check_launcher_upd_on_start": True,
        "minimize_on_start_game": True,
        "double_check": True,
        "version_alpha": True,
        "version_beta": True,
        "version_rc": True,
        "version_release": True,
        "game_path": "",
    }
    
    changed = False
    for key, default in defaults.items():
        if not settings.contains(key):
            settings.setValue(key, default)
            changed = True
    if changed:
        settings.sync()

def add_setting(*, layout: QHBoxLayout,
                text: str,
                settings: QSettings,
                value: str, default_value, type: Any,
                add_stretch=True):
    layout.addWidget(QLabel(text))
    if add_stretch: layout.addStretch()

    checkbox = QCheckBox()
    checkbox.setChecked(settings.value(value, default_value, type))
    checkbox.stateChanged.connect(
        lambda: settings.setValue(value, checkbox.isChecked())
    )
    
    layout.addWidget(checkbox)
