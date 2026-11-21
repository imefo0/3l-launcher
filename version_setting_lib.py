import tomllib
import tomli_w
from pathlib import Path
from datetime import datetime
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMessageBox, QMainWindow
import os
import platform
import shutil

settings = QSettings("3L", "3L Launcher")
window = QMainWindow()

versions_path = Path(settings.value("game_path", "")) / "config" / "versions.toml"
installed_path = Path(settings.value("game_path", "")) / "config" / "installed.toml"
local_versions_path = Path(settings.value("game_path", "")) / "versions"

def check_file(file_path, massage=True) -> bool:
    if file_path == "":
        if massage:
            QMessageBox.critical(
                window,
                "Ошибка",
                f"Введите путь к папке игры"
            )
        return False
    return True

def write_versions(versions: dict):
    if check_file(versions_path):
        os.makedirs(os.path.dirname(versions_path), exist_ok=True)

        with open(versions_path, "wb") as f:
            tomli_w.dump(versions, f)

# def write_installed(installed: dict):
#     if check_file(installed_path):
#         os.makedirs(os.path.dirname(installed_path), exist_ok=True)

#         with open(installed_path, "wb") as f:
#             tomli_w.dump(installed, f)

def read_versions():
    os.makedirs(os.path.dirname(versions_path), exist_ok=True)

    with open(versions_path, "a+b") as f:
        f.seek(0)
        return tomllib.load(f) 

# def read_installed():
#     os.makedirs(os.path.dirname(installed_path), exist_ok=True)

#     with open(installed_path, "a+b") as f:
#         f.seek(0)
#         return tomllib.load(f)

# def read_local_versions():
#     result = {} # TODO: сделать формат вывода

#     os_name = platform.system().lower()
#     os_name = os_name if os_name != "darwin" else "macos"

#     format_start_game = {
#         "windows": ".exe",
#         "macos": "", # HACK: тут спорный момент
#         "linux": ""
#     }

#     if not local_versions_path.exists():
#         os.makedirs(os.path.dirname(local_versions_path), exist_ok=True)
#         return result
    
#     versions_names = [version.name for version in local_versions_path.iterdir() if version.is_dir()]

#     for version_name in versions_names:
#         start_game_file = local_versions_path / version_name / f"last_light_leaving{format_start_game.get(os_name, "")}"
#         if start_game_file.exists() and start_game_file.is_file():
#             result[version_name] = True
#         else:
#             result[version_name] = False
#             shutil.rmtree(local_versions_path / version_name)

# def add_installed(versions: dict):
#     if check_file(versions_path):
#         os.makedirs(os.path.dirname(installed_path), exist_ok=True)

#         installed_versions = {}

#         if os.path.exists(installed_path):
#             with open(installed_path, "rb") as f:
#                 installed_versions = tomllib.load(f)

#         for version in list(versions["versions"].keys()):
#             installed_versions.setdefault(version, False)

#         with open(installed_path, "wb") as f:
#             tomli_w.dump(installed_versions, f)

#         print(installed_versions)

#     # TODO: потом проверять еще файлы локальные

def format_date(date):
    df = datetime.fromisoformat(date.replace("Z", "+00:00")).astimezone()

    return df.strftime("%d.%m.%Y %H:%M")