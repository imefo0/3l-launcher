import requests
from PySide6.QtCore import QSettings
from PySide6.QtWidgets import QMessageBox, QMainWindow, QComboBox
import version_setting_lib as vslib
import platform
from pathlib import Path
import hashlib
import zipfile
import shutil
import update_data as upd_data

settings = QSettings("3L", "3L Launcher")
window = QMainWindow()

url = "https://api.github.com/repos/imefo0/3l-launcher-test/releases"

temp_path = Path(settings.value("game_path", "")) / "templates"

versions_path = Path(settings.value("game_path", "")) / "versions"


def install(version, version_selector: QComboBox):
    if version_selector.currentText() == "":
        QMessageBox.information(
            window,
            "Справка",
            "Сначала выберете версию"
        )
        return

    installed_versions = vslib.read_installed()

    if installed_versions.get(version, False):
        QMessageBox.information(
            window,
            "Справка",
            f"Эта версия уже установлена"
        )
        return
    
    if settings.value("game_path", "") == "":
        QMessageBox.critical(
            window,
            "Ошибка",
            f"Не удалось установить версию. Введите путь к папке игры"
        )
        return

    versions_path.mkdir(parents=True, exist_ok=True)
    temp_path.mkdir(parents=True, exist_ok=True)

    # windows, linux, darwin (macos)
    os_name = platform.system().lower()

    # windows: x86_64, amd64 (чаще amd64 чем x86_64), x86, i386, i686
    # linux: x86_64, arm64, x86, i386, i686
    # macos: x86_64, arm64, aarch64 (M1, M2...)
    arch = platform.machine().lower()

    # для названий сборок: game-(windows/linux/macos)-(x86/x64/arm64).zip

    if os_name == "darwin":
        os_name = "macos"

    arch_aliases = {
        "amd64": "x64",
        "x86_64": "x64",
        "x86": "x86",
        "i386": "x86",
        "i686": "x86",
        "arm64": "arm64",
        "aarch64": "arm64"
    }

    arch = arch_aliases.get(arch)

    if arch is None:
        QMessageBox.critical(
            window,
            "Ошибка",
            "К сожалению данная операционная система не поддерживается."
        )

    # game-(windows/linux/macos)-(x86/x64/arm64).zip
    excepted_name = f"3l-{os_name}-{arch}.zip"

    try:
        response = requests.get(
            url,
            timeout=15
        )
        response.raise_for_status()
        releases = response.json()

        release = next(
            (r for r in releases if r["tag_name"] == version),
            None
        )

        if release is None:
            QMessageBox.critical(window, "Ошибка", "Релиз не найден")
            return
        print("установка: релиз есть")

        assets = release.get("assets", [])

        for asset in assets:
            print(asset["name"])
            print(asset["browser_download_url"])

        asset = next(
            (a for a in assets if a["name"] == excepted_name),
            None
        )

        if asset is None:
            QMessageBox.critical(
                window,
                "Ошибка",
                f"Сборка {excepted_name} не найдена"
            )
            return
        print("установка: сборка найдена")

        download_url = asset["browser_download_url"]
        file_size = asset["size"]
        file_hash = str(asset["digest"]).removeprefix("sha256:")

        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()

        downloaded = 0
        
        with open((temp_path / excepted_name), "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    print(f"{downloaded}\r" if downloaded % 10000 == 0 else "", end="")

        hasher = hashlib.sha256()

        with open((temp_path / excepted_name), "rb") as file:
            while chunk := file.read(8192):
                hasher.update(chunk)

        actual_hash = hasher.hexdigest()

        if actual_hash != file_hash:
            QMessageBox.critical(
                window,
                "Ошибка",
                "Контрольная сумма файла не совпадает. Файл повреждён."
            )
            return
        else: print("sha256 совпали")

        with zipfile.ZipFile((temp_path / excepted_name), "r") as archive:
            bad_file = archive.testzip()

            if bad_file is not None:
                QMessageBox.critical(
                    window,
                    "Ошибка",
                    "Архив поврежден"
                )
                return

            archive.extractall(temp_path / version)

            executable_names = {
                # HACK
                "windows": "Новый игровой проект.exe",
                "linux": "last_light_leaving",
                "macos": "last_light_leaving.app"
            }

            executable = temp_path / version / executable_names[os_name]

            if not executable.exists():
                QMessageBox.critical(
                    window,
                    "Ошибка",
                    "В архиве отсутствует исполняемый файл игры."
                )
                return
            print("установка: есть исполняемый файл игры")

            if (versions_path / version).exists():
                QMessageBox.critical(
                    window,
                    "Ошибка",
                    "Папка этой версии уже существует."
                )
                return

            shutil.move(
                temp_path / version,
                versions_path / version
                )
            print("установка: архив переместился")

            installed = vslib.read_installed()
            installed[version] = True
            vslib.write_installed(installed)
            print(installed)
            print(f"{version} = True")

            upd_data.post_upd(version_selector, upd_data.update(version_selector))

            # answer = QMessageBox.question(
            #     window,
            #     "Удаление временных файлов",
            #     "Хотите удалить временные файлы?",
            #     QMessageBox.StandardButton.Yes |
            #     QMessageBox.StandardButton.No
            # )
            # if answer == QMessageBox.StandardButton.Yes:
            #     shutil.rmtree(temp_path)

            print("установка завершена")

            # TODO: добавить потом защиту от zip slip
            # TODO: прям потом

    except requests.RequestException:
        print("Status:", response.status_code)
        print("URL:", response.url)
        print("Response:", response.text[:1000])
        QMessageBox.critical(window, "Ошибка", "Ошибка с сервером.")

        return

    # сделать кнопку отменить
    # показать прогресс
    # потом разархивировать
    # переместить файл
    # сказать готово
    # поставить кнопку "удалить"