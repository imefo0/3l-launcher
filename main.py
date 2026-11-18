import sys
from PySide6.QtWidgets import (
    QApplication, 
    QMainWindow,
    QWidget,
    QLabel,
    QPushButton,
    QVBoxLayout, QHBoxLayout, QGridLayout, QStackedWidget,
    QCheckBox, QLineEdit,
    QMessageBox,
    QComboBox,
    QFrame,
    QFileDialog,
    QDialog, QProgressBar
    )
from PySide6.QtCore import Qt, QSettings, QTimer
from PySide6.QtGui import QColor, QPalette, QFont
from winotify import Notification
from semantic_version import Version

app = QApplication()

import install
import version_setting_lib as vslib
import check_updates
import update_data as upd_data
import settings_lib

def notification():
    Notification(
        app_id="3L Launcher",
        title="3L Launcher",
        msg="Установка пошла",
        duration="short"
    ).show()

def question():
    answer = QMessageBox.question(
        window,
        "Удаление игры",
        "Ты действительно хочешь удалить 3l?",
        QMessageBox.StandardButton.Yes |
        QMessageBox.StandardButton.No
    )

    if answer == QMessageBox.StandardButton.Yes:
        print("удаление")
    else: 
        print("отмена")

def test():
    dialog = QDialog(window)
    dialog.setWindowTitle("тест")
    dialog.setFixedSize(300, 70)

    layout = QVBoxLayout(dialog)
    label = QLabel("тест 2")
    progress = QProgressBar()

    progress.setRange(0, 100)
    progress.setValue(45)

    layout.addWidget(label)
    layout.addWidget(progress)

    dialog.show()

def check_updates_versions(progress_bar: QProgressBar, info: QLabel):
    progress_bar.setRange(0, 0)
    info.setText("Идет проверка на обновления")
    check_updates.update_versions()
    progress_bar.setRange(0, 100)
    info.setText("Выполнена проверка на обновления версий")
    QTimer.singleShot(3000, lambda: info.setText(""))

version_launcher_value = "v1.0.0"

settings = QSettings("3L", "3L Launcher")

window = QMainWindow()
window.setWindowTitle("3L Launcher")
window.setFixedSize(300, 400)

pages = QStackedWidget()

main_page = QWidget()
settings_page = QWidget()

pages.addWidget(main_page)
pages.addWidget(settings_page)

main_layout = QVBoxLayout(main_page)
settings_layout = QVBoxLayout(settings_page)

window.setCentralWidget(pages)

# ========== переменные которые нужны раньше ==========

version_selector = QComboBox()

# ========== главное меню ==========

main_menu_header_layout = QHBoxLayout()

settings_button = QPushButton("⛭")
settings_button.setFixedSize(30, 30)
settings_button.setFont(QFont("Arial", 13))
settings_button.clicked.connect(lambda: pages.setCurrentWidget(settings_page))

main_menu_header_layout.addWidget(QLabel("<b>Главное меню</b>"))
main_menu_header_layout.addStretch()
main_menu_header_layout.addWidget(settings_button)

# ========== настройки ==========

# шапка
settings_header_layout = QHBoxLayout()

back_button = QPushButton("⮜")
back_button.setFixedSize(30, 30)
back_button.setFont(QFont("Arial", 13))
back_button.clicked.connect(lambda: (pages.setCurrentWidget(main_page), upd_data.post_upd(version_selector, upd_data.update(version_selector))))

settings_header_layout.addWidget(QLabel("<b>Настройки лаунчера</b>"))
settings_header_layout.addStretch()
settings_header_layout.addWidget(back_button)

# настройки

check_game_upd_on_start = QHBoxLayout()
settings_lib.add_setting(layout=check_game_upd_on_start,
                         text="Проверять обновления игры при запуске",
                         settings=settings,
                         value="check_game_upd_on_start", default_value=False, type=bool,
                         add_stretch=True)

check_launcher_upd_on_start = QHBoxLayout()
settings_lib.add_setting(layout=check_launcher_upd_on_start,
                         text="Проверять обновления лаунчера при запуске",
                         settings=settings,
                         value="check_launcher_upd_on_start", default_value=True, type=bool,
                         add_stretch=True)

minimize_on_start_game = QHBoxLayout()
settings_lib.add_setting(layout=minimize_on_start_game,
                         text="Сворачивать лаунчер при запуске игры",
                         settings=settings,
                         value="minimize_on_start_game", default_value=True, type=bool,
                         add_stretch=True)

path_layout = QHBoxLayout()
path_input = QLineEdit()
path_input.setText(settings.value("game_path", ""))
path_input.textChanged.connect(
    lambda: settings.setValue("game_path", path_input.text())
)
path_input.setPlaceholderText("Путь к папке игры")
open_button = QPushButton("Выбрать папку")
open_button.clicked.connect(
    lambda: path_input.setText(
        QFileDialog.getExistingDirectory(window, "Выбрать папку игры")
    )
)
path_layout.addWidget(path_input)
path_layout.addWidget(open_button)

version_layout = QVBoxLayout()
version_layout.addWidget(QLabel("Показывать версии в списке версий:"))

for version in ["alpha", "beta", "rc", "release"]:
    row = QHBoxLayout()
    row.addWidget(QLabel(f"\t- {version}"))
    checkbox = QCheckBox()
    checkbox.setChecked(settings.value(f"version_{version}", True, type=bool))
    checkbox.stateChanged.connect(
        lambda checked, v=version: settings.setValue(f"version_{v}", checked)
    )
    row.addWidget(checkbox)
    version_layout.addLayout(row)

update_launcher = QPushButton("Проверить на наличие обновлений лаунчера")

version_launcher = QLabel(version_launcher_value)

version_launcher.setFont(QFont("Arial", 8))
version_launcher.setAlignment(Qt.AlignmentFlag.AlignCenter)

settings_layout.setSpacing(3)

settings_layout.addLayout(settings_header_layout)
settings_layout.addLayout(check_game_upd_on_start)
settings_layout.addLayout(check_launcher_upd_on_start)
settings_layout.addLayout(minimize_on_start_game)
settings_layout.addLayout(path_layout)
settings_layout.addLayout(version_layout)
settings_layout.addStretch()
settings_layout.addWidget(update_launcher)
settings_layout.addWidget(version_launcher)

# ========== описание ==========

top_layout = QVBoxLayout()

desc_versions = QLabel("Описание версии")
desc_versions.setAlignment(
    Qt.AlignmentFlag.AlignTop
)

print("read_versions:", vslib.read_versions())
description = QLabel()
def set_desc_version(description: QLabel):
    current_text_version_selector = version_selector.currentText()
    print("set_desc_version получил", current_text_version_selector)
    if current_text_version_selector == "":
        description.setText("Сначала выберете версию")
    else:
        description.setText(
            vslib.read_versions()["versions"]
            .get(current_text_version_selector, {"body": "Я не знаю что делать, такой версии нет"})
            .get("body", "Нет описания у версии")
        )
    return description

description = set_desc_version(description)
description.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)
version_selector.currentTextChanged.connect(lambda: set_desc_version(description))

top_layout.addWidget(desc_versions)
top_layout.addWidget(description, 1)

# ========== разделитель ==========

line = QFrame()
line.setFrameShape(QFrame.Shape.HLine)
line.setFrameShadow(QFrame.Shadow.Sunken)

# ========== нижняя часть =========

bottom_layout = QGridLayout()
bottom_layout.setSpacing(5)

progress_bar = QProgressBar()
progress_bar.setFixedWidth(315)
progress_bar.setFixedHeight(9)

info = QLabel()
info.setFont(QFont("Arial", 8))
info.setAlignment(
    Qt.AlignmentFlag.AlignCenter
)

install_delete_button = QPushButton("Установить")
install_delete_button.clicked.connect(lambda: (
    install_delete_button.setText("Отмена"),
    install.install(version_selector.currentText(), version_selector),
    install_delete_button.setText("Установить")))
play_button = QPushButton("Запустить")

update_button = QPushButton("Проверить на наличие новых версий")
update_button.clicked.connect(lambda: (check_updates_versions(progress_bar, info),
                                       upd_data.post_upd(version_selector, upd_data.update(version_selector))))

version_list_raw = list(vslib.read_installed().items())
version_list = []

for version, installed in version_list_raw:
    prerelease_version = Version(version).prerelease
    if len(prerelease_version) == 0:
        if settings.value("version_release"):
            version_list.append((version, installed))
    else:
        if prerelease_version[0] == "alpha" and settings.value("version_alpha"):
            version_list.append((version, installed))
        if prerelease_version[0] == "beta" and settings.value("version_beta"):
            version_list.append((version, installed))
        if prerelease_version[0] == "rc" and settings.value("version_rc"):
            version_list.append((version, installed))

version_list.sort(key=lambda item: Version.coerce(item[0]), reverse=True)
# print("version_list:", version_list)
# print([settings.value(f"version_{x}") for x in ["alpha", "beta", "rc", "release"]])

version_selector.setPlaceholderText("Выберете версию")
version_selector.setCurrentIndex(-1)
for version, is_installed in version_list:
    # print(number)
    version_selector.addItem(version)
    if is_installed: version_selector.setItemData(
        version_selector.count() - 1,
        QColor(version_selector.palette().color(QPalette.ColorRole.Base).darker(115)),
        Qt.ItemDataRole.BackgroundRole
        )
if len(version_list) > 0: version_selector.setCurrentIndex(0)

bottom_layout.addWidget(install_delete_button, 1, 0)
bottom_layout.addWidget(play_button, 1, 1)
bottom_layout.addWidget(update_button, 2, 0, 1, 2)
bottom_layout.addWidget(version_selector, 0, 0, 1, 2)
bottom_layout.addWidget(progress_bar, 3, 0, 1, 2)
bottom_layout.addWidget(info, 4, 0, 1, 2)

# ========== сборка ==========

if settings.value("check_game_upd_on_start") == "true":
    check_updates_versions(progress_bar=progress_bar, info=info)

main_layout.addLayout(main_menu_header_layout)

main_layout.addLayout(top_layout, 2)
main_layout.addWidget(line)
main_layout.addLayout(bottom_layout, 1)

window.show()

sys.exit(app.exec())