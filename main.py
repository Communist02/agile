# This Python file uses the following encoding: utf-8
import sys
import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QGuiApplication, QAction, QPixmap, QCursor
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMenu, QFileDialog, QSizePolicy, QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox, QLabel

from rclone_python import rclone
from rclone_python import remote_types
from rclone import Rclone

import main_window
import new_remote_window

rc = Rclone('MB', True)


class NewRemoteWindow(QDialog):
    def __init__(self, edit_mode: bool = False, remote_name: str = None):
        super(NewRemoteWindow, self).__init__()
        self.ui = new_remote_window.Ui_NewRemoteWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(
            lambda: self.new_remote(edit_mode, remote_name))
        self.ui.buttonBox.rejected.connect(self.close)

        if edit_mode:
            self.setWindowTitle(f'Edit {remote_name}')
            config = rc.config('dump')
            type = config[remote_name[:-1]]['type']
            match type:
                case 'drive':
                    self.ui.tabWidget.setCurrentIndex(0)
                case 'yandex':
                    self.ui.tabWidget.setCurrentIndex(1)
                case 'ftp':
                    self.ui.tabWidget.setCurrentIndex(2)
                    host = config[remote_name[:-1]]['host']
                    port = config[remote_name[:-1]]['port']
                    user = config[remote_name[:-1]]['user']
                    tls = bool(config[remote_name[:-1]]['tls'] == 'true')
                    self.ui.lineEdit_ftp_host.setText(host)
                    self.ui.lineEdit_ftp_port.setText(port)
                    self.ui.lineEdit_ftp_login.setText(user)
                    self.ui.checkBox_ftp_tls.setChecked(tls)
                case 'webdav':
                    self.ui.tabWidget.setCurrentIndex(3)
                    url = config[remote_name[:-1]]['url']
                    user = config[remote_name[:-1]]['user']
                    self.ui.lineEdit_webdav_url.setText(url)
                    self.ui.lineEdit_webdav_login.setText(user)
                case 'http':
                    self.ui.tabWidget.setCurrentIndex(4)
                    url = config[remote_name[:-1]]['url']
                    self.ui.lineEdit_url.setText(url)
                case 'local':
                    self.ui.tabWidget.setCurrentIndex(5)

            self.ui.lineEdit_name.setText(remote_name[:-1])
            self.ui.tabWidget.tabBar().setVisible(False)

    def new_remote(self, edit_mode: bool = False, remote_name: str = None):
        name = self.ui.lineEdit_name.text().strip()
        if name != '':
            if edit_mode:
                rc.config('delete', remote_name[:-1])
            match self.ui.tabWidget.currentIndex():
                case 0:
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.drive)
                    self.close()
                case 1:
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.yandex)
                    self.close()
                case 2:
                    rclone.create_remote(name,
                                         remote_type=remote_types.RemoteTypes.ftp,
                                         host=self.ui.lineEdit_ftp_host.text().strip(),
                                         port=self.ui.lineEdit_ftp_port.text().strip(),
                                         user=self.ui.lineEdit_ftp_login.text().strip(),
                                         tls=str(self.ui.checkBox_ftp_tls.isChecked()).lower())
                    if self.ui.lineEdit_ftp_password.text().strip() != '':
                        rc.config('password', name, 'pass',
                                  self.ui.lineEdit_ftp_password.text().strip())
                    self.close()
                case 3:
                    vendors = ['other', 'fastmail', 'nextcloud', 'owncloud', 'sharepoint', 'sharepoint-ntlm', 'rclone']
                    rclone.create_remote(name,
                                         remote_type=remote_types.RemoteTypes.webdav,
                                         url=self.ui.lineEdit_webdav_url.text().strip(),
                                         user=self.ui.lineEdit_webdav_login.text().strip(),
                                         vendor=vendors[self.ui.comboBox_webdav_vendor.currentIndex()]
                                         )
                    if self.ui.lineEdit_webdav_password.text().strip() != '':
                        rc.config('password', name, 'pass',
                                  self.ui.lineEdit_webdav_password.text().strip())
                    self.close()
                case 4:
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.http, url=self.ui.lineEdit_url.text().strip())
                    self.close()
                case 5:
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.local)
                    self.close()
        else:
            alert = QMessageBox()
            alert.setWindowTitle('Enter name')
            alert.setText('Enter name for new remote')
            alert.exec()


class MainWindow(QMainWindow):
    download_path: str = str(Path.home() / "Downloads")
    remotes_paths = {}

    files: list = []
    current_remote: str = ''

    temp_dir: str = ''
    tree: list = []

    cache: dict = {}

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.file_view.header().resizeSection(0, 300)
        self.ui.file_view.header().resizeSection(1, 80)
        self.ui.file_view.header().resizeSection(2, 120)

        self.ui.actionExit.triggered.connect(self.close)
        self.ui.action_new_remote.triggered.connect(
            self.open_new_remote_window)

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

    def clear_cache(self, remote_name, path):
        if remote_name in self.cache and path in self.cache[remote_name]:
            del self.cache[remote_name][path]

    def open_folder(self, remote_name: str, path_dir: str = ''):
        self.current_remote = remote_name
        self.remotes_paths[remote_name] = path_dir
        self.ui.file_view.clear()

        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()

        button = QPushButton(remote_name)
        button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        button.clicked.connect(lambda t, a=remote_name: self.open_folder(a))
        self.ui.path_list.addWidget(button)

        temp_path = ''
        for name in path_dir.split('/'):
            if name != '':
                temp_path += name + '/'
                arrow_label = QLabel("/")
                arrow_label.setAlignment(Qt.AlignCenter)
                # arrow_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                self.ui.path_list.addWidget(arrow_label)
                button = QPushButton(name)
                button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                button.clicked.connect(lambda t, a=self.current_remote, b=temp_path[:-1]: self.open_folder(a, b))
                self.ui.path_list.addWidget(button)

        if remote_name in self.cache and path_dir in self.cache[remote_name]:
            tree = self.cache[remote_name][path_dir]
        else:
            tree = rc.lsjson(f'"{remote_name}{path_dir}"')

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
            if remote_name in self.cache:
                self.cache[remote_name][path_dir] = tree
            else:
                self.cache[remote_name] = {path_dir: tree}

        tree = sorted(
            tree, key=lambda element: element['is_dir'], reverse=True)

        for file in tree:
            tree_item = QTreeWidgetItem(
                [file['name'], file['size'], file['modified'], file['type']])
            self.ui.file_view.addTopLevelItem(tree_item)



    def open_remote(self, item: QTreeWidgetItem):
        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()
        self.open_folder(item.text())

    def open_item(self, item: QTreeWidgetItem):
        if self.current_remote:
            if self.remotes_paths[self.current_remote] != '':
                file_path = self.remotes_paths[self.current_remote] + '/' + item.text(0)
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
            rc.copy(f'"{self.current_remote}{file_path}"',
                    f'"{download_path}"')

    def mount_remote(self, name: str):
        if os.name == 'nt':
            rc.mount(f'"{name}"', f'*')
        else:
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

    def edit_remote(self, name: str):
        open_win = NewRemoteWindow(edit_mode=True, remote_name=name)
        open_win.setModal(True)
        open_win.exec()
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
        action.setText('Edit')
        action.triggered.connect(lambda: self.edit_remote(item.text()))
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
