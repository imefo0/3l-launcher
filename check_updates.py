import requests
import version_setting_lib as vslib
from pathlib import Path
from PySide6.QtCore import QSettings, Signal, Slot, QObject
from PySide6.QtWidgets import QMainWindow
import platform
import os
import shutil
import system_definition as sys_def
import github_api as gh_api

url = "https://api.github.com/repos/imefo0/3l-launcher-test/releases"

settings = QSettings("3L", "3L Launcher")
window = QMainWindow()

build_name = "last_light_leaving"

local_path = Path(settings.value("game_path", "")) / "versions"

def update_versions(info_callback=None, is_waiting=None):
    if is_waiting is not None: 
        is_waiting.emit(True)
    versions = synchronize_versions(info_callback)

    if info_callback: info_callback.emit("Запись версий в реестр")
    vslib.write_versions(versions)

    print(versions)
    if info_callback: info_callback.emit("Список версий обновлен")
    print("[CHECK UPD]: список версий обновлен")

    if is_waiting is not None: is_waiting.emit(False)

def get_remote_versions(info_callback=None) -> dict[str, dict[str, str | bool]]:
    if info_callback: info_callback.emit("Получение списка установленных версий")
    print("[CHECK UPD]: получение списка установленных версий")

    response = gh_api.github_get(url, params={"per_page": 100})
    response.raise_for_status()
    releases = response.json()
    print(f"[CHECK UPD]: всего релизов: {len(releases)}")

    versions = { }

    for release in releases:
        tag = release["tag_name"]

        published_at = release.get("published_at")
        is_prerelease = release.get("prerelease", False)

        versions[tag] = {
            "body": release.get("body", "У этой версии нет описания"),
            "published_at": published_at,
            "user_published_at": vslib.format_date(published_at) if published_at else "Время неизвестно",
            "prerelease": is_prerelease,
            "user_prerelease": "prerelease" if is_prerelease else "release"
        }

    print("версии:", versions)
    return versions

def get_local_versions(info_callback=None) -> dict[str, bool]:
    result = {} # TODO: сделать формат вывода

    if info_callback: info_callback.emit("Получение данные об операционной системе")
    print("[CHECK UPD]: проверка ОС")
    format_start_game = {
        "windows": ".exe",
        "macos": "", # HACK: тут спорный момент
        "linux": ""
    }
    os_name = sys_def.get_system_info()[0]

    if not local_path.exists():
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        return result

    if info_callback: info_callback.emit("Получение локального списка версий")
    print("[CHECK UPD]: получаем локальный список версий")

    versions_names = [version.name for version in local_path.iterdir() if version.is_dir()]

    if info_callback: info_callback.emit("Проверка на существование исполняемого файла")
    print("[CHECK UPD]: проверяем на исполняемый файл")
    for version_name in versions_names:
        start_game_file = local_path / version_name / f"{build_name}{format_start_game.get(os_name, "")}"
        if start_game_file.exists() and start_game_file.is_file():
            result[version_name] = True
            print("[CHECK UPD]: get_local_versions:", "версия ЕСТЬ")
        else:
            result[version_name] = False
            print("[CHECK UPD]: get_local_versions:", "версии НЕТ")
            # shutil.rmtree(local_path / version_name)

    return result

def synchronize_versions(info_callback=None) -> dict[str, dict[str, str | bool]]:
    remote_versions = get_remote_versions(info_callback)
    local_versions = get_local_versions(info_callback)

    print("[CHECK UPD]: синхронизация remote и local")
    if info_callback: info_callback.emit("Синхронизация локальных и скачанных данных")

    for version in remote_versions:
        remote_versions[version]["is_installed"] = local_versions.get(version, False)

    for local_version, is_installed in local_versions.items():
        if local_version not in remote_versions:
            remote_versions[local_version] = {
                "is_installed": is_installed
            }

    return remote_versions

class Updater(QObject):
    error = Signal(str)
    success = Signal()
    final = Signal()
    is_waiting = Signal(bool)
    info = Signal(str)

    def __init__(self, version):
        super().__init__()
        self.version = version

    @Slot()
    def run(self):
        try:
            update_versions(self.info, self.is_waiting)
            self.success.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.final.emit()
