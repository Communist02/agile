import asyncio
import asyncio.base_futures
import shutil
import sys
import os
import subprocess
from multiprocessing import Process

from PySide6.QtCore import QMimeData, QUrl, Qt, QTimer
from PySide6.QtGui import QDrag, QDragEnterEvent, QIcon, QAction, QCursor
from PySide6.QtWidgets import QInputDialog, QMainWindow, QApplication, QDialog, QMenu, QFileDialog, QProgressBar, QSizePolicy, QTreeWidgetItem, QPushButton, QMessageBox, QLabel
import PySide6.QtAsyncio as QtAsyncio

from rclone_python import rclone
from rclone_python import remote_types
from rclone import Rclone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import main_window
import new_remote_window
import win32api

rc = Rclone()


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, target_file, file_name):
        super().__init__()
        self.target_file = target_file
        self.file_name = file_name

    def on_created(self, event):
        if os.path.basename(event.src_path) == os.path.basename(self.target_file):
            window.download_path = event.src_path


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
        self.progress = 0
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
            self.progress = round((size / full_size) * 100)
        else:
            self.progress = 0

    def set_status(self, is_done: bool):
        if is_done:
            self.progress = 100
            self.speed = '-'
            self.estimated = '-'
            self.status = 'Done'
        else:
            self.status = 'Running'

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
    download_path: str = ''
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

        self.ui.tree_files.header().resizeSection(0, 300)
        self.ui.tree_files.header().resizeSection(1, 80)
        self.ui.tree_files.header().resizeSection(2, 120)

        self.ui.actionExit.triggered.connect(self.close)
        self.ui.action_new_remote.triggered.connect(
            self.open_new_remote_window)

        self.ui.tree_remotes.itemClicked.connect(self.open_remote)
        self.ui.tree_files.itemDoubleClicked.connect(
            lambda item: self.open_item(item.text(0), item.text(3) == 'inode/directory'))
        self.ui.tasks.itemDoubleClicked.connect(self.open_task_dir)

        self.ui.tree_files.startDrag = self.start_drag

        self.ui.tree_files.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tree_files.customContextMenuRequested.connect(
            self.show_context_menu_tree)

        self.ui.tree_remotes.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tree_remotes.customContextMenuRequested.connect(
            self.show_context_menu_remote)

        self.ui.tasks.setContextMenuPolicy(Qt.CustomContextMenu)
        self.ui.tasks.customContextMenuRequested.connect(
            self.show_context_menu_task)

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
                item = QTreeWidgetItem()
                match self.tasks[i].operation:
                    case 'Download':
                        item.setIcon(0, QIcon.fromTheme('emblem-downloads'))
                    case 'Upload':
                        item.setIcon(0, QIcon.fromTheme('go-up'))
                    case 'Opening':
                        item.setIcon(0, QIcon.fromTheme('document-open'))
                self.ui.tasks.addTopLevelItem(item)
            else:
                item = self.ui.tasks.topLevelItem(i)

            item.setText(0, self.tasks[i].operation)
            item.setText(1, self.tasks[i].source)
            item.setText(2, self.tasks[i].destination)

            if len(rc.tasks) > i:
                self.tasks[i].set_full_size(rc.tasks[i]['full_size'])
                self.tasks[i].set_size(rc.tasks[i]['current_size'])
                self.tasks[i].set_speed(rc.tasks[i]['speed'])
                self.tasks[i].set_estimated(rc.tasks[i]['estimated'])
                self.tasks[i].set_status(rc.tasks[i]['is_done'])

                item.setText(3, self.tasks[i].status)
                item.setText(4, self.tasks[i].size)
                self.ui.tasks.setItemWidget(
                    item, 5, QProgressBar(value=self.tasks[i].progress))
                item.setText(6, self.tasks[i].speed)
                item.setText(7, self.tasks[i].estimated)

    def closeEvent(self, event):
        if self.temp_dir != '':
            shutil.rmtree(self.temp_dir)
        return super().closeEvent(event)

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls() and event.mimeData().text() != '.cloud_explorer_file_temp':
            event.accept()

    def dropEvent(self, event):
        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        for url in event.mimeData().urls():
            source_path = url.toLocalFile()
            if os.path.isfile(source_path) or os.path.isdir(source_path):
                asyncio.ensure_future(self.upload_file(
                    source_path, destination_remote, destination_path))

    def start_drag(self, supportedActions):
        item = self.ui.tree_files.currentItem()
        if not item:
            return

        self.download_path = ''

        if self.temp_dir == '':
            self.temp_dir = rclone.tempfile.mkdtemp(prefix='cloud_explorer-')
        open(self.temp_dir + '/.cloud_explorer_file_temp', 'a').close()

        mime_data = QMimeData()
        mime_data.setText('.cloud_explorer_file_temp')
        url = QUrl.fromLocalFile(self.temp_dir + '/.cloud_explorer_file_temp')
        mime_data.setUrls([url])

        drag: QDrag = QDrag(self)
        drag.setMimeData(mime_data)

        if os.name == 'nt':
            observers = []
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.replace('\x00', '').split('\\')[:-1]

            handler = FileMonitorHandler(
                '.cloud_explorer_file_temp', item.text(0))

            for disk in drives:
                observer = Observer()
                observer.schedule(handler, disk + '\\', recursive=True)
                try:
                    observer.start()
                    observers.append(observer)
                except PermissionError:
                    pass
        else:
            observer = Observer()
            observer.schedule(handler, '/', recursive=True)
            observer.start()

        drag.exec(Qt.DropAction.MoveAction)
        if os.name == 'nt':
            for obs in observers:
                obs.stop()
        else:
            observer.stop()
        if self.download_path != '':
            os.remove(self.download_path)
            self.download_file(self.ui.tree_files.selectedItems(), self.download_path[:-len(
                '.cloud_explorer_file_temp') - 1])

    async def upload_file(self, source_path: str, destination_remote: str, destination_path: str):
        self.tasks.append(Task(operation='Upload', source=source_path,
                          destination=f'{destination_remote}{destination_path}'))
        self.ui.dock_tasks.show()
        is_dir = await rc.is_dir(source_path)

        dest_path = destination_path
        if is_dir:
            if len(destination_path) > 0 and destination_path[-1] != '/':
                dest_path += '/' + \
                    source_path.replace('\\', '/').split('/')[-1]
            else:
                dest_path += source_path.replace('\\', '/').split('/')[-1]

        await rc.copy(source_path, f'{destination_remote}{dest_path}')
        await self.update_dir(destination_remote, destination_path)

    def update_remotes(self):
        remotes = rc.listremotes(True)
        self.ui.tree_remotes.clear()
        for remote in remotes:
            if remote['type'] != 'local':
                self.ui.tree_remotes.addTopLevelItem(
                    QTreeWidgetItem([remote['name'] + ':', remote['type']]))
            else:
                self.ui.tree_remotes.addTopLevelItem(
                    QTreeWidgetItem([remote['name'] + ':/', remote['type']]))

    def open_new_remote_window(self):
        open_win = NewRemoteWindow()
        open_win.setModal(True)
        open_win.exec()
        self.update_remotes()

    def menu_open(self):
        self.ui.tree_remotes.setVisible(not self.ui.tree_remotes.isVisible())

    def clear_cache(self, remote_name: str, path: str):
        if remote_name in self.cache and path in self.cache[remote_name]:
            del self.cache[remote_name][path]

    async def open_dir(self, remote_name: str, path_dir: str = '', update=False):
        self.current_remote = remote_name
        self.remotes_paths[remote_name] = path_dir

        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()

        button = QPushButton(remote_name)
        button.setSizePolicy(QSizePolicy.Policy.Fixed,
                             QSizePolicy.Policy.Expanding)
        button.setFlat(True)
        button.clicked.connect(
            lambda t, a=remote_name: asyncio.ensure_future(self.open_dir(a)))
        self.ui.path_list.addWidget(button)

        temp_path = ''
        for name in path_dir.split('/'):
            if name != '':
                temp_path += name + '/'
                arrow_label = QLabel("/")
                arrow_label.setAlignment(Qt.AlignCenter)
                self.ui.path_list.addWidget(arrow_label)
                button = QPushButton(name)
                button.setSizePolicy(
                    QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                button.setFlat(True)
                button.clicked.connect(
                    lambda t, a=self.current_remote, b=temp_path[:-1]: asyncio.ensure_future(self.open_dir(a, b)))
                self.ui.path_list.addWidget(button)

        self.ui.statusbar.showMessage(f'Opening {remote_name}{path_dir}')
        while True:
            if remote_name in self.cache and path_dir in self.cache[remote_name] and not update:
                tree = self.cache[remote_name][path_dir]
                update = True
                self.ui.statusbar.showMessage(
                    f'Updating {remote_name}{path_dir}')
            else:
                if not update:
                    self.ui.tree_files.clear()
                update = False
                tree = await rc.lsjson(f'{remote_name}{path_dir}')
                self.ui.statusbar.showMessage('')

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

                    modified = modified.replace(
                        'T', ' ').replace('Z', ' ').split('.')[0]
                    tree[i] = {'name': name, 'size': size, 'modified': modified,
                               'path': path, 'is_dir': is_dir, 'type': type}
                if remote_name in self.cache:
                    self.cache[remote_name][path_dir] = tree
                else:
                    self.cache[remote_name] = {path_dir: tree}

            if f'{self.current_remote}{self.remotes_paths[self.current_remote]}' == f'{remote_name}{path_dir}':
                tree = sorted(
                    tree, key=lambda element: element['is_dir'], reverse=True)

                self.ui.tree_files.clear()
                for file in tree:
                    item = QTreeWidgetItem(
                        [file['name'], file['size'], file['modified'], file['type']])
                    item.setTextAlignment(1, Qt.AlignmentFlag.AlignRight)
                    item.setData(0, Qt.ItemDataRole.UserRole, file['name'])

                    if file['is_dir']:
                        item.setIcon(0, QIcon.fromTheme('folder'))
                    else:
                        if os.name == 'nt':
                            item.setIcon(0, QIcon.fromTheme(
                                'emblem-documents'))
                        else:
                            type_file = file['type'].split(
                                ';')[0].replace('/', '-')
                            item.setIcon(0, QIcon.fromTheme(type_file))
                    self.ui.tree_files.addTopLevelItem(item)

            if not update:
                break

    def open_remote(self, item: QTreeWidgetItem):
        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()
        asyncio.ensure_future(self.open_dir(item.text(0)))

    async def open_file(self, file_path: str, file_name: str):
        if self.temp_dir == '':
            self.temp_dir = rclone.tempfile.mkdtemp(prefix='cloud_explorer-')
        self.tasks.append(Task(
            operation='Opening', source=f'{self.current_remote}{file_path}', destination=self.temp_dir))
        self.ui.dock_tasks.show()
        await rc.copy(f'{self.current_remote}{file_path}', self.temp_dir)
        if os.name == 'nt':
            os.startfile(self.temp_dir + '\\' + file_name)
        else:
            subprocess.call(['xdg-open', self.temp_dir + '/' + file_name])

    def open_item(self, file_name: str, is_dir: bool):
        if self.current_remote:
            if self.remotes_paths[self.current_remote] != '':
                file_path = self.remotes_paths[self.current_remote] + \
                    '/' + file_name
            else:
                file_path = file_name
            if is_dir:
                asyncio.ensure_future(self.open_dir(
                    self.current_remote, file_path))
            else:
                asyncio.ensure_future(self.open_file(file_path, file_name))

    def download_file(self, items: list[QTreeWidgetItem], download_path: str = None):
        if download_path is None:
            download_path = QFileDialog.getExistingDirectory()
        if download_path is not None and download_path != '':
            for item in items:
                if self.remotes_paths[self.current_remote] != '':
                    file_path = f'{self.remotes_paths[self.current_remote]}/{item.text(0)}'
                else:
                    file_path = item.text(0)

                self.tasks.append(Task(
                    operation='Download', source=f'{self.current_remote}{file_path}', destination=download_path))
                self.ui.dock_tasks.show()

                if item.text(3) != 'inode/directory':
                    asyncio.ensure_future(rc.copy(
                        f'{self.current_remote}{file_path}', download_path))
                else:
                    if len(download_path) > 0 and (download_path[-1] != '/' or download_path[-1] != '\\'):
                        asyncio.ensure_future(rc.copy(
                            f'{self.current_remote}{file_path}', f'{download_path}/{item.text(0)}'))
                    else:
                        asyncio.ensure_future(rc.copy(
                            f'{self.current_remote}{file_path}', f'{download_path}{item.text(0)}'))

    def mount_remote(self, name: str):
        if os.name == 'nt':
            p1 = Process(target=rc.mount, args=(name, '*'), daemon=True)
            p1.start()
        else:
            mount_path = QFileDialog.getExistingDirectory()
            if mount_path is not None and mount_path != '':
                rc.mount(f'"{name}"', f'"{mount_path}"')

    def copy_file(self, file_name: str):
        if self.remotes_paths[self.current_remote] != '':
            file_path = f'{self.current_remote}{self.remotes_paths[self.current_remote]}/{file_name}'
        else:
            file_path = f'{self.current_remote}{file_name}'
        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setText(file_path)
        url = QUrl.fromLocalFile(file_path)
        mime_data.setUrls([url])
        clipboard.setMimeData(mime_data)

    def delete_file(self, items: list[QTreeWidgetItem]):
        if len(items) == 1:
            question = f'Are you sure you want to delete {item.text(0)} ?'
        else:
            question = f'Are you sure you want to delete {len(items)} files ?'
        confirmation = QMessageBox.question(self, 'Delete', question)
        if confirmation == QMessageBox.Yes:
            for item in items:
                if self.remotes_paths[self.current_remote] != '':
                    file_path = f'{self.current_remote}{self.remotes_paths[self.current_remote]}/{item.text(0)}'
                else:
                    file_path = f'{self.current_remote}{item.text(0)}'
                if not item.text(3) == 'inode/directory':
                    rc.deletefile(file_path)
                else:
                    rc.purge(file_path)
            asyncio.ensure_future(self.update_dir(
                self.current_remote, self.remotes_paths[self.current_remote]))

    async def update_dir(self, remote_name: str, path: str):
        self.clear_cache(remote_name, path)

        if f'{remote_name}{path}' == f'{self.current_remote}{self.remotes_paths[self.current_remote]}':
            await self.open_dir(remote_name, path)

    async def paste_file(self):
        clipboard = QApplication.clipboard()

        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        for url in clipboard.mimeData().urls():
            source_path = url.toLocalFile()
            self.upload_file(source_path, destination_remote, destination_path)

    def exit_folder(self):
        if self.current_remote != '' and self.remotes_paths[self.current_remote] != '':
            path_dir = f'{self.remotes_paths[self.current_remote]}'
            path = '/'.join(path_dir.split('/')[:-1])
            asyncio.ensure_future(self.open_dir(self.current_remote, path))

    async def new_folder(self):
        folder_name, ok = QInputDialog.getText(
            self, "New Folder", "Enter folder name:", text="New Folder")

        if ok and folder_name.strip():
            if self.remotes_paths[self.current_remote] != '':
                folder_path = f'{self.current_remote}{self.remotes_paths[self.current_remote]}/{folder_name.strip()}'
            else:
                folder_path = f'{self.current_remote}{self.remotes_paths[self.current_remote]}{folder_name.strip()}'
            await rc.mkdir(folder_path)
            await self.update_dir(self.current_remote, self.remotes_paths[self.current_remote])

    def delete_remote(self, name: str):
        rc.config('delete', name[:-1])
        self.update_remotes()

    def edit_remote(self, name: str):
        open_win = NewRemoteWindow(edit_mode=True, remote_name=name)
        open_win.setModal(True)
        open_win.exec()
        self.update_remotes()

    def open_task_dir(self, item: QTreeWidgetItem):
        if os.name == 'nt':
            os.startfile(item.text(2))
        else:
            subprocess.call(['xdg-open', item.text(2)])

    def clear_task(self, index: int):
        del self.tasks[index]
        del rc.tasks[index]
        self.ui.tasks.takeTopLevelItem(index)

    def show_context_menu_tree(self, point):
        index = self.ui.tree_files.indexAt(point)
        selected = self.ui.tree_files.selectedItems()

        menu = QMenu()

        if not index.isValid():
            action = QAction(window)
            action.setText('Paste')
            action.setIcon(QIcon.fromTheme('edit-paste'))
            action.triggered.connect(
                lambda: asyncio.ensure_future(self.paste_file()))
            menu.addAction(action)

            action = QAction(window)
            action.setText('New Folder')
            action.setIcon(QIcon.fromTheme('folder-new'))
            action.triggered.connect(
                lambda: asyncio.ensure_future(self.new_folder()))
            menu.addAction(action)
        else:
            item = self.ui.tree_files.itemAt(point)
            file_name = item.text(0)
            is_dir = item.text(3) == 'inode/directory'

            action = QAction(window)
            action.setText('Open')
            action.setIcon(QIcon.fromTheme('document-open'))
            action.triggered.connect(lambda: self.open_item(file_name, is_dir))
            menu.addAction(action)

            action = QAction(window)
            action.setText('Download')
            action.setIcon(QIcon.fromTheme('emblem-downloads'))
            action.triggered.connect(
                lambda: self.download_file(selected))
            menu.addAction(action)

            menu.addSeparator()

            action = QAction(window)
            action.setText('Copy')
            action.setIcon(QIcon.fromTheme('edit-copy'))
            action.triggered.connect(lambda: self.copy_file(file_name))
            menu.addAction(action)

            action = QAction(window)
            action.setText('Paste')
            action.setIcon(QIcon.fromTheme('edit-paste'))
            action.triggered.connect(
                lambda: asyncio.ensure_future(self.paste_file()))
            menu.addAction(action)

            menu.addSeparator()

            action = QAction(window)
            action.setText('Rename')
            action.setIcon(QIcon.fromTheme('format-text-italic'))
            # action.triggered.connect(lambda: self.download_file(0))
            menu.addAction(action)

            action = QAction(window)
            action.setText('Delete')
            action.setIcon(QIcon.fromTheme('edit-delete'))
            action.triggered.connect(
                lambda: self.delete_file(selected))
            menu.addAction(action)

            menu.addSeparator()

            action = QAction(window)
            action.setText('New Folder')
            action.setIcon(QIcon.fromTheme('folder-new'))
            action.triggered.connect(
                lambda: asyncio.ensure_future(self.new_folder()))
            menu.addAction(action)

        menu.exec(QCursor.pos())

    def show_context_menu_remote(self, point):
        index = self.ui.tree_remotes.indexAt(point)

        if not index.isValid():
            return

        item = self.ui.tree_remotes.itemAt(point)

        menu = QMenu()

        action = QAction(window)
        action.setText('Open')
        action.setIcon(QIcon.fromTheme('folder-open'))
        action.triggered.connect(lambda: self.open_remote(item))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Edit')
        action.setIcon(QIcon.fromTheme('applications-development'))
        action.triggered.connect(lambda: self.edit_remote(item.text(0)))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Mount')
        action.setIcon(QIcon.fromTheme('drive-harddisk'))
        action.triggered.connect(lambda: self.mount_remote(item.text(0)))
        menu.addAction(action)

        action = QAction(window)
        action.setText('Delete')
        action.setIcon(QIcon.fromTheme('edit-delete'))
        action.triggered.connect(lambda: self.delete_remote(item.text(0)))
        menu.addAction(action)

        menu.exec(QCursor.pos())

    def show_context_menu_task(self, point):
        index = self.ui.tasks.indexAt(point)

        if not index.isValid():
            return

        item = self.ui.tasks.itemAt(point)

        menu = QMenu()

        action = QAction(window)
        action.setText('Open folder')
        action.setIcon(QIcon.fromTheme('folder-open'))
        action.triggered.connect(lambda: self.open_task_dir(item))
        menu.addAction(action)

        if item.text(3) == 'Done':
            action = QAction(window)
            action.setText('Clear')
            action.setIcon(QIcon.fromTheme('edit-clear'))
            action.triggered.connect(lambda: self.clear_task(index.row()))
            menu.addAction(action)

        menu.exec(QCursor.pos())


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()

    window.show()
    sys.exit(QtAsyncio.run())
