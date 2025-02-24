# This Python file uses the following encoding: utf-8
import sys
import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QGuiApplication, QAction, QPixmap, QCursor
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMenu, QFileDialog, QTreeWidget, QTreeWidgetItem, QPushButton

from rclone_python import rclone

import main_window


class MainWindow(QMainWindow):
    download_path = str(Path.home() / "Downloads")
    disk_paths = {}

    files = []
    current_disk = ''

    temp_dir = ''
    tree = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.disk_list.itemClicked.connect(self.open_disk)

        self.ui.file_view.itemDoubleClicked.connect(self.open_item)

        self.ui.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.file_view.customContextMenuRequested.connect(
            self.show_context_menu_tree)

        self.ui.actionExit.triggered.connect(lambda: self.close())
        self.ui.button_exit_dir.clicked.connect(self.exit_folder)

        self.disks = rclone.get_remotes()
        for disk in self.disks:
            self.ui.disk_list.addItem(disk)

    def open_folder(self, disk_name: str, path_dir: str = ''):
        self.current_disk = disk_name
        self.ui.file_view.clear()

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

            if is_dir:
                size = ''
            else:
                for _ in range(4):
                    if size >= 1024:
                        size = round(float(size) / 1024, 2)
                        index += 1
                size = f'{size} {sizes[index]}'

            if path_dir != '':
                path = path_dir + "/" + tree[i]["Path"]
            else:
                path = tree[i]["Path"]

            modified = modified.replace('T', ' ').replace('Z', ' ')
            tree[i] = {"name": name, "size": size,
                       "modified": modified, "path": path, "is_dir": is_dir, "type": type}
            tree_item = QTreeWidgetItem(
                [name, size, modified, type])
            if is_dir:
                tree_item.setFlags(tree_item.flags() | Qt.ItemIsSelectable)
            self.ui.file_view.addTopLevelItem(tree_item)
        # print(tree)

        tree = sorted(
            tree, key=lambda element: element['is_dir'], reverse=True)

    def open_disk(self, item):
        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()
        self.ui.path_list.addWidget(QPushButton(item.text()))
        self.open_folder(item.text())

    def open_item(self, item: QTreeWidgetItem):
        if self.current_disk:
            if self.disk_paths[self.current_disk] != '':
                file_path = self.disk_paths[self.current_disk] + \
                    '/' + item.text(0)
            else:
                file_path = item.text(0)
            if item.text(3) == 'inode/directory':
                self.open_folder(self.current_disk, file_path)
            else:
                if self.temp_dir == '':
                    self.temp_dir = rclone.tempfile.mkdtemp(
                        prefix='cloud_explorer-')
                if os.name == 'nt':
                    new_file = self.temp_dir + '\\' + item.text(0)
                    print(new_file)
                    print(f'{self.current_disk}{file_path}')
                    rclone.copyto(f'{self.current_disk}{file_path}', new_file)
                    os.startfile(new_file)
                else:
                    new_file = self.temp_dir + '/' + file_path
                    print(new_file)
                    rclone.copyto(f'{self.current_disk}{file_path}', new_file)
                    subprocess.call(['xdg-open', new_file])

    def download_file(self, file_name: str):
        download_path = QFileDialog.getSaveFileName(dir=file_name)
        if download_path is not None and download_path != '' and download_path[0] != '':
            new_file = download_path[0]
            if self.disk_paths[self.current_disk] != '':
                file_path = self.disk_paths[self.current_disk] + \
                    '/' + file_name
            else:
                file_path = file_name
            print(new_file)
            rclone.copyto(f'{self.current_disk}{file_path}', new_file)

    def exit_folder(self):
        if self.current_disk != '' and self.disk_paths[self.current_disk] != '':
            path_dir = f'{self.disk_paths[self.current_disk]}'
            path = '/'.join(path_dir.split('/')[:-1])
            self.open_folder(self.current_disk, path)

    def show_context_menu_tree(self, point):
        index = self.ui.file_view.indexAt(point)

        if not index.isValid():
            return

        item = self.ui.file_view.itemAt(point)
        # name = item.text(0)  # The text of the node.

        menu = QMenu()

        action = QAction(window)
        action.setText('Open')
        action.triggered.connect(lambda: self.open_item(item))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Download')
        action.triggered.connect(lambda: self.download_file(item.text(0)))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Copy')
        # action.triggered.connect(lambda: self.download_file(0))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Rename')
        # action.triggered.connect(lambda: self.download_file(0))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Delete')
        # action.triggered.connect(lambda: self.download_file(0))
        menu.addAction(action)

        menu.exec(QCursor.pos())


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()

    window.show()
    sys.exit(app.exec())
