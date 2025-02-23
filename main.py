# This Python file uses the following encoding: utf-8
import sys
import os
import subprocess
from pathlib import Path

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject, Slot, Signal

from rclone_python import rclone


class Backend(QObject):
    open_disk_signal = Signal(str, list)  # Сигнал для добавления вкладки
    open_folder_signal = Signal(str, list)
    current_disk_path_update_signal = Signal(str)
    download_path = str(Path.home() / "Downloads")

    disk_paths = {}
    current_disk = ''

    temp_dir = ''

    def __init__(self):
        super().__init__()
        self.tab_count = 0

    @Slot()
    def quit(self):
        app.quit()

    @Slot(bool, str, str)
    def open_folder(self, new_tab: bool, disk_name: str, path_dir: str = ""):
        tree = rclone.ls(f'{disk_name}{path_dir}')
        self.disk_paths[disk_name] = path_dir

        # print(tree)
        for i in range(len(tree)):
            sizes = ['bytes', 'KB', 'MB', 'GB', 'TB']
            index = 0
            size = tree[i]["Size"]
            name = tree[i]["Name"]
            modified = tree[i]["ModTime"]
            is_dir = tree[i]["IsDir"]
            type = tree[i]["MimeType"]
            if path_dir != "":
                path = path_dir + "/" + tree[i]["Path"]
            else:
                path = tree[i]["Path"]
            for _ in range(4):
                if size >= 1024:
                    size = round(float(size) / 1024, 2)
                    index += 1
            tree[i] = {"name": name, "size": f'{size} {sizes[index]}',
                       "modified": modified, "path": path, "is_dir": is_dir, "type": type}
        # print(tree)

        tree = sorted(
            tree, key=lambda element: element['is_dir'], reverse=True)
        if new_tab:
            # Отправка сигнала в QML
            self.open_disk_signal.emit(disk_name, tree)
        else:
            self.open_folder_signal.emit(
                disk_name, tree)  # Отправка сигнала в QML
            self.current_disk = disk_name
            self.current_disk_path_update_signal.emit(f'{disk_name}{path_dir}')

    @Slot()
    def exit_folder(self):
        if self.current_disk != '' and self.disk_paths[self.current_disk] != '':
            path_dir = f'{self.disk_paths[self.current_disk]}'
            path = '/'.join(path_dir.split('/')[:-1])
            self.open_folder(False, self.current_disk, path)

    @Slot(str, str)
    def open_file(self, disk_name: str, file_path: str):
        if self.temp_dir == '':
            self.temp_dir = rclone.tempfile.mkdtemp(prefix='cloud_explorer-')
        new_file = self.temp_dir + '/' + file_path
        rclone.copyto(f'{disk_name}{file_path}', new_file)
        if os.name == 'nt':
            subprocess.call(['start', new_file])
        else:
            subprocess.call(['xdg-open', new_file])

    @Slot(str, str, str, str)
    def download_file(self, disk_name: str, file_path: str, download_path: str, file_name: str):
        print(disk_name, file_path, download_path, file_name)
        new_file = download_path + '/' + file_name
        print(new_file)
        if os.name == 'nt':
            new_file = new_file[8:]
        else:
            new_file = new_file[7:]
        rclone.copyto(f'{disk_name}{file_path}', new_file)


if __name__ == "__main__":
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()

    disks_list = rclone.get_remotes()
    for i in range(len(disks_list)):
        disks_list[i] = {"text": disks_list[i]}

    backend = Backend()

    engine.rootContext().setContextProperty("backend", backend)
    engine.rootContext().setContextProperty("disksListModel", disks_list)

    qml_file = Path(__file__).resolve().parent / "main.qml"
    engine.load(qml_file)
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
