# This Python file uses the following encoding: utf-8
import asyncio
import shutil
import sys
import os
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt, QTimer, QPoint
from PySide6.QtGui import QIcon, QGuiApplication, QAction, QPixmap, QCursor
from PySide6.QtWidgets import QMainWindow, QApplication, QDialog, QMenu, QFileDialog, QSizePolicy, QTreeWidget, QTreeWidgetItem, QPushButton, QMessageBox, QLabel
import PySide6.QtAsyncio as QtAsyncio

from rclone_python import rclone
from rclone_python import remote_types
from rclone import Rclone
from rclone_async import Rclone_async

import main_window
import new_remote_window

rc = Rclone('MB', True)
rc_async = Rclone_async(True)


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
                    vendor = config[remote_name[:-1]
                                    ].setdefault('vendor', 'other')
                    self.ui.lineEdit_webdav_url.setText(url)
                    self.ui.lineEdit_webdav_login.setText(user)
                    match vendor:
                        case 'fastmail':
                            vendor = 1
                        case 'nextcloud':
                            vendor = 2
                        case 'owncloud':
                            vendor = 3
                        case 'sharepoint':
                            vendor = 4
                        case 'sharepoint-ntlm':
                            vendor = 5
                        case 'rclone':
                            vendor = 6
                        case _:
                            vendor = 0

                    self.ui.comboBox_webdav_vendor.setCurrentIndex(vendor)
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
                    vendors = ['other', 'fastmail', 'nextcloud',
                               'owncloud', 'sharepoint', 'sharepoint-ntlm', 'rclone']
                    rclone.create_remote(name,
                                         remote_type=remote_types.RemoteTypes.webdav,
                                         url=self.ui.lineEdit_webdav_url.text().strip(),
                                         user=self.ui.lineEdit_webdav_login.text().strip(),
                                         vendor=vendors[self.ui.comboBox_webdav_vendor.currentIndex(
                                         )]
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


class Task():
    def __init__(self, operation, source, destination):
        self.operation = operation
        self.source = source
        self.destination = destination
        self.status = 'Executing'
        self.size = ''
        self.full_size = 0
        self.progress = ''
        self.speed = ''
        self.estimated = ''

    def set_full_size(self, size: float):
        self.full_size = size

    def set_size(self, size: float):
        sizes = ['B', 'KB', 'MB', 'GB', 'TB']
        index = 0
        full_size = self.full_size

        for _ in range(4):
            if full_size >= 1024:
                full_size = round(float(full_size) / 1024, 2)
                size = round(float(size) / 1024, 2)
                index += 1

        self.size = f'{size} / {full_size} {sizes[index]}'
        if full_size != 0:
            self.progress = f'{round((size / full_size) * 100)}%'
        else:
            self.progress = '0%'

    def set_status(self, status):
        self.status = status

    def set_speed(self, speed: float):
        sizes = ['B/s', 'KB/s', 'MB/s', 'GB/s', 'TB/s']
        index = 0

        for _ in range(4):
            if speed >= 1024:
                speed = speed / 1024
                index += 1

        self.speed = f'{round(speed, 2)} {sizes[index]}'

    def set_estimated(self, estimated: str):
        self.estimated = estimated


class MainWindow(QMainWindow):
    download_path: str = str(Path.home() / "Downloads")
    remotes_paths = {}
    files: list = []
    current_remote: str = ''
    temp_dir: str = ''
    tree: list = []
    cache: dict = {}
    tasks: list[Task] = []

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

        self.timer = QTimer(interval=500)
        self.timer.timeout.connect(self.timer_update)
        self.timer.start()

    def timer_update(self):
        # self.ui.tasks.clear()
        for i in range(len(self.tasks)):
            if i >= self.ui.tasks.topLevelItemCount():
                self.ui.tasks.addTopLevelItem(QTreeWidgetItem())
            item = self.ui.tasks.topLevelItem(i)
            item.setText(0, self.tasks[i].operation)
            item.setText(1, self.tasks[i].source)
            item.setText(2, self.tasks[i].destination)

            self.tasks[i].set_full_size(rc_async.tasks[i]['full_size'])
            self.tasks[i].set_size(rc_async.tasks[i]['size'])
            self.tasks[i].set_speed(rc_async.tasks[i]['speed'])
            self.tasks[i].set_estimated(rc_async.tasks[i]['estimated'])
            self.tasks[i].set_status(rc_async.tasks[i]['status'])

            item.setText(3, self.tasks[i].status)
            item.setText(4, self.tasks[i].size)
            item.setText(5, self.tasks[i].progress)
            item.setText(6, self.tasks[i].speed)
            item.setText(7, self.tasks[i].estimated)

    def closeEvent(self, event):
        if self.temp_dir != '':
            shutil.rmtree(self.temp_dir)
        return super().closeEvent(event)

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
        button.setSizePolicy(QSizePolicy.Policy.Fixed,
                             QSizePolicy.Policy.Expanding)
        button.setFlat(True)
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
                button.setSizePolicy(
                    QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                button.setFlat(True)
                button.clicked.connect(
                    lambda t, a=self.current_remote, b=temp_path[:-1]: self.open_folder(a, b))
                self.ui.path_list.addWidget(button)

        if remote_name in self.cache and path_dir in self.cache[remote_name]:
            tree = self.cache[remote_name][path_dir]
        else:
            tree = rc.lsjson(f'"{remote_name}{path_dir}"')

            for i in range(len(tree)):
                sizes = ['B', 'KB', 'MB', 'GB', 'TB']
                index = 0
                size = tree[i]['Size']
                name = tree[i]['Name']
                modified = tree[i]['ModTime']
                is_dir = tree[i]['IsDir']
                type = tree[i]['MimeType']

                if is_dir:
                    size = ''
                else:
                    for _ in range(4):
                        if size >= 1024:
                            size = round(float(size) / 1024, 2)
                            index += 1
                    size = f'{size} {sizes[index]}'

                if path_dir != '':
                    path = path_dir + '/' + tree[i]['Path']
                else:
                    path = tree[i]['Path']

                modified = modified.replace('T', ' ').replace('Z', ' ')
                tree[i] = {'name': name, 'size': size, 'modified': modified,
                           'path': path, 'is_dir': is_dir, 'type': type}
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

            self.tasks.append(Task(
                operation='Download', source=f'{self.current_remote}{file_path}', destination=download_path))
            self.ui.dock_tasks.show()
            asyncio.ensure_future(rc_async.copy(
                f'"{self.current_remote}{file_path}"', f'"{download_path}"'))

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
    sys.exit(QtAsyncio.run())
