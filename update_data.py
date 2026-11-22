import version_setting_lib as vslib
from semantic_version import Version
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QComboBox
from PySide6.QtCore import Qt, QSettings
from PySide6.QtGui import QColor, QPalette

settings = QSettings("3L", "3L Launcher")

version_filter = {
    "alpha": settings.value("version_alpha"),
    "beta": settings.value("version_beta"),
    "rc": settings.value("version_rc")
}

def get_filtered_sorted_versions() -> dict[str, bool]:
    # current_text = version_selector.currentText()

    version_list = {
        version: data["is_installed"]
        for version, data in vslib.read_versions().items()
    }

    result = {}

    for version, installed in version_list.items():
        prerelease_version = Version(version).prerelease
        if len(prerelease_version) == 0:
            if settings.value("version_release"):
                result[version] = installed
        else:
            for prerelease, setting in version_filter.items():
                if prerelease_version[0] == prerelease and setting:
                    result[version] = installed
                    break

    return dict(
        sorted(
            result.items(),
            key=lambda item: Version.coerce(item[0]),
            reverse=True
        )
    )

    # TODO: ПОСЛЕ 1.0.0
    # print("version_list:", version_list)
    # print("current_text:", current_text)
    # print("есть ли версия в списке версий:", any(item[0] == current_text for item in version_list))
    # if any(item[0] == current_text for item in version_list):
    #     version_selector.setCurrentText(current_text)
    #     print("ставим в version_selector:", current_text)

def populate_version_selector(version_selector: QComboBox, versions: dict[str, bool]):
    current_ver = version_selector.currentText()
    version_selector.clear()
    for version, is_installed in versions.items():
        version_selector.addItem(version)
        if is_installed: version_selector.setItemData(
            version_selector.count() - 1,
            QColor(version_selector.palette().color(QPalette.ColorRole.Base).darker(115)),
            Qt.ItemDataRole.BackgroundRole
            )
    if current_ver in versions.keys():
        version_selector.setCurrentText(current_ver)