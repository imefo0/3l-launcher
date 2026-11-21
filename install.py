import requests
from PySide6.QtCore import QSettings, QObject, Signal, Slot
from PySide6.QtWidgets import QMessageBox, QMainWindow, QComboBox
import version_setting_lib as vslib
from pathlib import Path
import zipfile
import shutil
import update_data as upd_data
import system_definition as sys_def
import hash_checker
import json

settings = QSettings("3L", "3L Launcher")
window = QMainWindow()

url = "https://api.github.com/repos/imefo0/3l-launcher-test/releases"

build_name = "last_light_leaving"

def check(version: str, version_selector: QComboBox) -> bool:
    if version_selector.currentText() == "":
        QMessageBox.information(
            window,
            "Справка",
            "Сначала выберете версию"
        )
        return False

    versions = vslib.read_versions()
    if versions[version].get("is_installed", False):
        QMessageBox.information(
            window,
            "Справка",
            f"Эта версия уже установлена"
        )
        return False

    if settings.value("game_path", "") == "":
        QMessageBox.critical(
            window,
            "Ошибка",
            f"Не удалось установить версию. Введите путь к папке игры"
        )
        return False

    return True

def update_registry(version_selector: QComboBox):
    upd_data.populate_version_selector(
        version_selector, 
        upd_data.get_filtered_sorted_versions()
        )

def install(version, 
            progress_callback=None,
            info_callback=None,
            is_waiting=None):
    if info_callback: info_callback.emit("Подготовка")
    if progress_callback and is_waiting is not None: is_waiting.emit(True)

    chunk_size = 8192
    
    temp_path = Path(settings.value("game_path", "")) / "templates"
    versions_path = Path(settings.value("game_path", "")) / "versions"

    versions = vslib.read_versions()

    versions_path.mkdir(parents=True, exist_ok=True)
    temp_path.mkdir(parents=True, exist_ok=True)

    os_name, arch = sys_def.get_system_info()

    executable_names = {
        # HACK
        "windows": f"{build_name}.exe",
        "linux": build_name,
        "macos": f"{build_name}.app"
    }

    if info_callback: info_callback.emit("Проверка на совместимость")
    if os_name not in executable_names:
        raise Exception("К сожалению, операционная система не поддерживается.")

    if arch is None:
        raise Exception("К сожалению, данная архитектура процессора не поддерживается.")

    # game-(windows/linux/macos)-(x86/x64/arm64).zip
    expected_name = f"3l-{os_name}-{arch}.zip"

    try:
        if info_callback: info_callback.emit("Установка данных о версий")
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
            raise Exception("Релиз не найден")
        print("установка: релиз есть")

        if info_callback: info_callback.emit("Поиск сборки под эту платформу")

        assets = release.get("assets", [])

        for asset in assets:
            print(f"{asset["name"]}: {asset["browser_download_url"]}")

        asset = next(
            (a for a in assets if a["name"] == expected_name),
            None
        )

        if asset is None:
            raise Exception(f"Сборка {expected_name} не найдена")
        print("установка: сборка найдена")

        if info_callback: info_callback.emit("Получение метаданных о сборке")
        download_url = asset["browser_download_url"]
        file_size = asset["size"]
        file_hash = str(asset["digest"]).removeprefix("sha256:")

        if file_size <= 0:
            raise Exception("Некорректный размер файла")

        response = requests.get(download_url, stream=True, timeout=30)
        response.raise_for_status()

        downloaded = 0

        if progress_callback and is_waiting is not None: is_waiting.emit(False)
        if info_callback: info_callback.emit("Установка версии")
        
        with open((temp_path / expected_name), "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    file.write(chunk)
                    downloaded += len(chunk)
                    print(f"{downloaded / file_size * 100:.0f}%\r", end="")
                    if progress_callback:
                        progress_callback.emit(int(downloaded / file_size * 100))

        if progress_callback: progress_callback.emit(0)

        if progress_callback and is_waiting is not None: is_waiting.emit(True)
        if info_callback: info_callback.emit("Проверка контрольных сумм")

        if not hash_checker.check_hash_2_files((temp_path / expected_name), file_hash):
            raise Exception("Контрольная сумма файла не совпадает с ожидаемым. Скачанный файл поврежден")
        else: print("установка: sha256 совпали")

        if progress_callback and is_waiting is not None: is_waiting.emit(False)
        if info_callback: info_callback.emit("Распаковка архива")

        with zipfile.ZipFile((temp_path / expected_name), "r") as archive:
            bad_file = archive.testzip()

            if bad_file is not None:
                raise Exception("Архив поврежден")

            members = archive.infolist()
            total_size = sum(member.file_size for member in members)
            extracted_size = 0

            for member in members:
                target = temp_path / version / member.filename

                if member.is_dir():
                    target.mkdir(parents=True, exist_ok=True)
                    continue

                target.parent.mkdir(parents=True, exist_ok=True)

                with archive.open(member) as source, open(target, "wb") as destination:
                    while True:
                        chunk = source.read(chunk_size)

                        if not chunk:
                            break

                        destination.write(chunk)
                        extracted_size += len(chunk)

                        if progress_callback and total_size > 0:
                            progress_callback.emit(
                                int(extracted_size / total_size * 100)
                            )

            executable = temp_path / version / executable_names[os_name]

            if not executable.exists():
                raise Exception("В архиве отсутствует исполняемый файл игры.")

            print("установка: есть исполняемый файл игры")

            if (versions_path / version).exists():
                raise Exception("Папка этой версии уже существует")

            shutil.move(
                temp_path / version,
                versions_path / version
            )

            print("установка: архив переместился")

        if progress_callback: progress_callback.emit(0)

        if info_callback: info_callback.emit("Запись версии в реестр")
        if progress_callback and is_waiting is not None: is_waiting.emit(True)
        versions[version]["is_installed"] = True
        vslib.write_versions(versions)

        # answer = QMessageBox.question(
        #     window,
        #     "Удаление временных файлов",
        #     "Хотите удалить временные файлы?",
        #     QMessageBox.StandardButton.Yes |
        #     QMessageBox.StandardButton.No
        # )
        # if answer == QMessageBox.StandardButton.Yes:
        #     shutil.rmtree(temp_path)

        if progress_callback and is_waiting is not None: is_waiting.emit(False)
        if info_callback: info_callback.emit("Установка завершена")
        print("установка завершена")

        # TODO: добавить потом защиту от zip slip
        # TODO: прям потом

    except requests.RequestException as e:
        raise Exception(f"Ошибка с сервером: {e}") from e

    # сделать кнопку отменить
    # показать прогресс
    # потом разархивировать
    # переместить файл
    # сказать готово
    # поставить кнопку "удалить"

class Installer(QObject):
    finished = Signal()
    error = Signal(str)
    success = Signal()
    final = Signal()
    progress = Signal(int)
    is_waiting = Signal(bool)
    info = Signal(str)

    def __init__(self, version):
        super().__init__()
        self.version = version

    @Slot()
    def run(self):
        try:
            install(self.version, self.progress, self.info, self.is_waiting)
            self.success.emit()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.final.emit()
            self.finished.emit()