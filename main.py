# This Python file uses the following encoding: utf-8
import sys
import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QGuiApplication, QAction, QPixmap, QCursor
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMenu, QFileDialog, QTreeWidget, QTreeWidgetItem, QPushButton

from rclone_python import rclone
from rclone_python import remote_types
from rclone import Rclone

import main_window
import new_remote_window

rc = Rclone('MB', True)
# rclone.create_remote('qwertyq', remote_type=remote_types.RemoteTypes.http, url="http://127.0.0.1:8000/")


class NewRemoteWindow(QDialog):
    def __init__(self):
        super(NewRemoteWindow, self).__init__()
        self.ui = new_remote_window.Ui_NewRemoteWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(self.new_remote)

    def new_remote(self):
        name = self.ui.lineEdit_name.text().strip()

        match self.ui.tabWidget.currentIndex():
            case 0:
                pass
            case 4:
                rclone.create_remote(name, remote_type=remote_types.RemoteTypes.http, url=self.ui.lineEdit_url.text().strip())



class MainWindow(QMainWindow):
    download_path = str(Path.home() / "Downloads")
    remotes_paths = {}

    files = []
    current_remote = ''

    temp_dir = ''
    tree = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.file_view.header().resizeSection(0, 300)
        self.ui.file_view.header().resizeSection(1, 80)
        self.ui.file_view.header().resizeSection(2, 120)

        self.ui.actionExit.triggered.connect(self.close)
        self.ui.action_new_remote.triggered.connect(self.open_new_remote_window)

        self.ui.disk_list.itemClicked.connect(self.open_remote)
        self.ui.file_view.itemDoubleClicked.connect(self.open_item)

        self.ui.file_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.file_view.customContextMenuRequested.connect(
            self.show_context_menu_tree)

        self.ui.disk_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.disk_list.customContextMenuRequested.connect(
            self.show_context_menu_remote)


        self.ui.button_exit_dir.clicked.connect(self.exit_folder)
        self.ui.openMenuButton.clicked.connect(self.menu_open)

        self.update_remotes()


    def update_remotes(self):
        remotes = rclone.get_remotes()
        self.ui.disk_list.clear()
        for remote in remotes:
            self.ui.disk_list.addItem(remote)

    def open_new_remote_window(self):
        open_win = NewRemoteWindow()
        open_win.setModal(True)
        open_win.exec()
        self.update_remotes()

    def menu_open(self):
        self.ui.disk_list.setVisible(not self.ui.disk_list.isVisible())

    def open_folder(self, remote_name: str, path_dir: str = ''):
        self.current_remote = remote_name
        self.ui.file_view.clear()

        tree = rc.lsjson(f'"{remote_name}{path_dir}"')
        self.remotes_paths[remote_name] = path_dir

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
        # print(tree)

        tree = sorted(
            tree, key=lambda element: element['is_dir'], reverse=True)

        for file in tree:
            tree_item = QTreeWidgetItem([file['name'], file['size'], file['modified'], file['type']])
            self.ui.file_view.addTopLevelItem(tree_item)

    def open_remote(self, item):
        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()
        self.ui.path_list.addWidget(QPushButton(item.text()))
        self.open_folder(item.text())

    def open_item(self, item: QTreeWidgetItem):
        if self.current_remote:
            if self.remotes_paths[self.current_remote] != '':
                file_path = self.remotes_paths[self.current_remote] + \
                    '/' + item.text(0)
            else:
                file_path = item.text(0)
            if item.text(3) == 'inode/directory':
                self.open_folder(self.current_remote, file_path)
            else:
                if self.temp_dir == '':
                    self.temp_dir = rclone.tempfile.mkdtemp(
                        prefix='cloud_explorer-')
                if os.name == 'nt':
                    rc.copy(f'"{self.current_remote}{file_path}"',
                            f'"{self.temp_dir}"')
                    os.startfile(self.temp_dir + '\\' + item.text(0))
                else:
                    rc.copy(f'"{self.current_remote}{file_path}"',
                            f'"{self.temp_dir}"')
                    subprocess.call(
                        ['xdg-open', self.temp_dir + '/' + item.text(0)])

    def download_file(self, file_name: str):
        download_path = QFileDialog.getExistingDirectory()
        if download_path is not None and download_path != '':
            if self.remotes_paths[self.current_remote] != '':
                file_path = self.remotes_paths[self.current_remote] + \
                    '/' + file_name
            else:
                file_path = file_name
            rc.copy(f'"{self.current_remote}{file_path}"', f'"{download_path}"')

    def mount_remote(self, name):
        mount_path = QFileDialog.getExistingDirectory()
        if mount_path is not None and mount_path != '':
            rc.mount(f'"{name}"', f'"{mount_path}"')

    def exit_folder(self):
        if self.current_remote != '' and self.remotes_paths[self.current_remote] != '':
            path_dir = f'{self.remotes_paths[self.current_remote]}'
            path = '/'.join(path_dir.split('/')[:-1])
            self.open_folder(self.current_remote, path)

    def delete_remote(self, name: str):
        rc.config('delete', name[:-1])
        self.update_remotes()

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

    def show_context_menu_remote(self, point):
        index = self.ui.disk_list.indexAt(point)

        if not index.isValid():
            return

        item = self.ui.disk_list.itemAt(point)

        menu = QMenu()

        action = QAction(window)
        action.setText('Open')
        action.triggered.connect(lambda: self.open_remote(item))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Mount')
        action.triggered.connect(lambda: self.mount_remote(item.text()))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Rename')
        # action.triggered.connect(lambda: self.download_file(0))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Delete')
        action.triggered.connect(lambda: self.delete_remote(item.text()))
        menu.addAction(action)

        menu.exec(QCursor.pos())


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()

    window.show()
    sys.exit(app.exec())
