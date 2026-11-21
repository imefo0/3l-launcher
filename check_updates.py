import requests
import version_setting_lib as vslib
from pathlib import Path
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMainWindow
import platform
import os
import shutil
import system_definition as sys_def

url = "https://api.github.com/repos/imefo0/3l-launcher-test/releases"

settings = QSettings("3L", "3L Launcher")
window = QMainWindow()

build_name = "last_light_leaving"

local_path = Path(settings.value("game_path", "")) / "versions"

def update_versions():
    versions = synchronize_versions()

    vslib.write_versions(versions)

    print(versions)
    print("список версий обновлен")

def get_remote_versions() -> dict[str, dict[str, str | bool]]:
    response = requests.get(url, params={"per_page": 100}, timeout=15)
    releases = response.json()

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

def get_local_versions() -> dict[str, bool]:
    result = {} # TODO: сделать формат вывода

    format_start_game = {
        "windows": ".exe",
        "macos": "", # HACK: тут спорный момент
        "linux": ""
    }
    os_name = sys_def.get_system_info()[0]

    if not local_path.exists():
        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        return result
    
    versions_names = [version.name for version in local_path.iterdir() if version.is_dir()]

    for version_name in versions_names:
        start_game_file = local_path / version_name / f"{build_name}{format_start_game.get(os_name, "")}"
        if start_game_file.exists() and start_game_file.is_file():
            result[version_name] = True
            print("get_local_versions:", "версия ЕСТЬ")
        else:
            result[version_name] = False
            print("get_local_versions:", "версии НЕТ")
            # shutil.rmtree(local_path / version_name)

    return result

def synchronize_versions() -> dict[str, dict[str, str | bool]]:
    remote_versions = get_remote_versions()
    local_versions = get_local_versions()

    for version in remote_versions:
        remote_versions[version]["is_installed"] = local_versions.get(version, False)

    for local_version, is_installed in local_versions.items():
        if local_version not in remote_versions:
            remote_versions[local_version] = {
                "is_installed": is_installed
            }

    return remote_versions