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
import github_api as gh_api

settings = QSettings("3L", "3L Launcher")
window = QMainWindow()

def check(version: str, version_selector: QComboBox) -> bool:
    if version_selector.currentText() == "":
        QMessageBox.information(
            window,
            "Справка",
            "Сначала выберете версию"
        )
        return False

    versions = vslib.read_versions()
    # если версия установлена то удалить
    # иначе сказать что нельзя удалить
    if not versions[version].get("is_installed", False):
        QMessageBox.information(
            window,
            "Справка",
            f"Невозможно удалить эту версию: она не установлена или не найдена."
        )
        return False

    if settings.value("game_path", "") == "":
        QMessageBox.critical(
            window,
            "Ошибка",
            f"Не удалось удалить версию. Введите путь к папке игры"
        )
        return False

    return True

def update_registry(version_selector: QComboBox):
    upd_data.populate_version_selector(
        version_selector, 
        upd_data.get_filtered_sorted_versions()
        )

def delete(
        version, 
        info_callback=None,
        is_waiting=None,
        cancel_event=None
        ):
    def check_cancel():
        if cancel_event and cancel_event.is_set():
            raise InterruptedError("Установка отменена")

    
    if info_callback: info_callback.emit("Подготовка")
    if is_waiting is not None: is_waiting.emit(True)

    check_cancel()
        
    versions_path = Path(settings.value("game_path", "")) / "versions"

    versions = vslib.read_versions()   

    final_version_path = versions_path / version

    if info_callback: info_callback.emit("Удаление версии")
        
    shutil.rmtree(final_version_path)

    if info_callback: info_callback.emit("Запись об удалении в реестр")
    versions[version]["is_installed"] = False
    vslib.write_versions(versions)

    if is_waiting is not None: is_waiting.emit(False)
    if info_callback: info_callback.emit("Удаление завершено")
    print("удаление завершено")

class Deleter(QObject):
    finished = Signal()
    error = Signal(str)
    success = Signal()
    final = Signal()
    is_waiting = Signal(bool)
    info = Signal(str)

    def __init__(self, version, cancel_event):
        super().__init__()
        self.version = version
        self.cancel_event = cancel_event

    @Slot()
    def run(self):
        try:
            delete(
                self.version,
                self.info,
                self.is_waiting,
                self.cancel_event
            )
            self.success.emit()
        except InterruptedError:
            print("Установка отменена")
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self.final.emit()
