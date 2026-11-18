import version_setting_lib as vslib
from semantic_version import Version
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QPalette

settings = QSettings("3L", "3L Launcher")

def update(version_selector: QComboBox):
    # current_text = version_selector.currentText()

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

    # TODO: ПОСЛЕ 1.0.0
    # print("version_list:", version_list)
    # print("current_text:", current_text)
    # print("есть ли версия в списке версий:", any(item[0] == current_text for item in version_list))
    # if any(item[0] == current_text for item in version_list):
    #     version_selector.setCurrentText(current_text)
    #     print("ставим в version_selector:", current_text)

    return version_list

def post_upd(version_selector: QComboBox, version_list: list):
    version_selector.clear()
    for version, is_installed in version_list:
        version_selector.addItem(version)
        if is_installed: version_selector.setItemData(
            version_selector.count() - 1,
            QColor(version_selector.palette().color(QPalette.ColorRole.Base).darker(115)),
            Qt.ItemDataRole.BackgroundRole
            )