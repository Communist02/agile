import asyncio
import shutil
import signal
import sys
import os
import subprocess
import types

from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QByteArray, QMimeData, QSettings, QSize, QUrl, Qt, QTimer, QRegularExpression
from PySide6.QtGui import QCloseEvent, QDrag, QDragEnterEvent, QIcon, QAction, QCursor, QPixmap, QRegularExpressionValidator
from PySide6.QtWidgets import QInputDialog, QMainWindow, QApplication, QDialog, QMenu, QFileDialog, QProgressBar, QSizePolicy, QSlider, QStyleFactory, QSystemTrayIcon, QTreeWidgetItem, QPushButton, QMessageBox, QLabel, QWidget
import PySide6.QtAsyncio as QtAsyncio

from rclone_python import rclone
from rclone_python import remote_types
from rclone import Rclone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import main_window
import new_remote_window
import new_serve_window
import settings_window

if os.name == 'nt':
    import winreg
    import win32api

rc = Rclone()


class FileMonitorHandler(FileSystemEventHandler):
    def __init__(self, target_file):
        super().__init__()
        self.target_file = target_file

    def on_created(self, event):
        if os.path.basename(event.src_path) == os.path.basename(self.target_file):
            window.download_path = event.src_path


class SettingsWindow(QDialog):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.ui = settings_window.Ui_SettingsWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(
            QIcon(f'{os.path.dirname(__file__) + os.sep}favicon.ico'))

        styles = QStyleFactory.keys()
        for i in range(len(styles)):
            styles[i] = styles[i].lower()
        self.ui.comboBox_style.addItems(styles)
        self.ui.comboBox_style.setCurrentText(app.style().name())

        self.ui.buttonBox.accepted.connect(self.ok)

    def ok(self):
        app.setStyle(self.ui.comboBox_style.currentText())
        settings.setValue('style', self.ui.comboBox_style.currentText())


class NewServeWindow(QDialog):
    def __init__(self):
        super(NewServeWindow, self).__init__()
        self.ui = new_serve_window.Ui_NewServeWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(lambda: self.new_serve())

    def new_serve(self):
        path = self.ui.lineEdit_path.text()
        user = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()
        address = self.ui.lineEdit_address.text()
        read_only = self.ui.checkBox_read_only.isChecked()
        args = ''
        if self.ui.radioButton_ftp.isChecked():
            serve_type = 'ftp'
        elif self.ui.radioButton_dnla.isChecked():
            serve_type = 'dnla'
        elif self.ui.radioButton_http.isChecked():
            serve_type = 'http'
        elif self.ui.radioButton_webdav.isChecked():
            serve_type = 'webdav'
        elif self.ui.radioButton_sftp.isChecked():
            serve_type = 'sftp'
            if not user or not password:
                args += '--no-auth'

        process: subprocess.Popen = rc.serve(
            serve_type, path, user, password, address, read_only, args)
        try:
            process.wait(1)
            QMessageBox.critical(self, 'Error', 'Check the data!')
        except subprocess.TimeoutExpired:
            window.tasks.append(
                Task(operation='Serve', source=path, destination=serve_type, process=process))
            self.close()


class NewRemoteWindow(QDialog):
    def __init__(self, edit_mode: bool = False, remote_name: str = None):
        super(NewRemoteWindow, self).__init__()
        self.ui = new_remote_window.Ui_NewRemoteWindow()
        self.ui.setupUi(self)

        self.ui.buttonBox.accepted.connect(
            lambda: self.new_remote(edit_mode, remote_name))
        self.ui.checkBox_ftp_tls.clicked.connect(self.set_view_ftp_tls_option)

        reg_exp = QRegularExpression('[a-zA-ZА-Яа-яЁё0-9_\\.\\-\\+@\\* ]*$')
        validator = QRegularExpressionValidator(reg_exp)
        self.ui.lineEdit_name.setValidator(validator)

        if edit_mode:
            self.setWindowTitle(f'Edit {remote_name}')
            config = rc.config('dump')
            type = config[remote_name[:-1]]['type']
            match type:
                case 'drive':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_google_drive')))
                case 'yandex':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_yandex_disk')))
                case 'ftp':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_ftp')))
                    host = config[remote_name[:-1]]['host']
                    port = config[remote_name[:-1]]['port']
                    user = config[remote_name[:-1]]['user']
                    tls = config[remote_name[:-1]]['tls'] == 'true'
                    explicit_tls = config[remote_name[:-1]
                                          ]['explicit_tls'] == 'true'
                    if tls:
                        self.ui.radioButton_ftp_false.setEnabled(True)
                        self.ui.radioButton_ftp_true.setEnabled(True)
                    self.ui.lineEdit_ftp_host.setText(host)
                    self.ui.lineEdit_ftp_port.setText(port)
                    self.ui.lineEdit_ftp_login.setText(user)
                    self.ui.checkBox_ftp_tls.setChecked(tls)
                    self.ui.radioButton_ftp_true.setChecked(explicit_tls)
                case 'webdav':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_webdav')))
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
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_http')))
                    url = config[remote_name[:-1]]['url']
                    self.ui.lineEdit_url.setText(url)
                case 'local':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_local')))
                case 'onedrive':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_onedrive')))
                case 'mailru':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_mailru')))
                    user = config[remote_name[:-1]]['user']
                    self.ui.lineEdit_mailru_login.setText(user)
                case 'sftp':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_sftp')))
                    host = config[remote_name[:-1]]['host']
                    port = config[remote_name[:-1]]['port']
                    user = config[remote_name[:-1]]['user']
                    self.ui.lineEdit_sftp_host.setText(host)
                    self.ui.lineEdit_sftp_port.setText(port)
                    self.ui.lineEdit_sftp_login.setText(user)
                case 'alias':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_alias')))
                    remote = config[remote_name[:-1]]['remote']
                    self.ui.lineEdit_alias_path.setText(remote)
                case 'union':
                    self.ui.tabWidget.setCurrentIndex(self.ui.tabWidget.indexOf(
                        self.ui.tabWidget.findChild(QWidget, 'tab_union')))
            self.ui.lineEdit_name.setText(remote_name[:-1])
            self.ui.tabWidget.tabBar().hide()

    def set_view_ftp_tls_option(self, value):
        self.ui.radioButton_ftp_false.setEnabled(value)
        self.ui.radioButton_ftp_true.setEnabled(value)

    def new_remote(self, edit_mode: bool = False, remote_name: str = None):
        name = self.ui.lineEdit_name.text().strip()
        if name != '':
            if edit_mode:
                rc.config('delete', f'"{remote_name[:-1]}"')
            match self.ui.tabWidget.currentWidget().objectName():
                case 'tab_google_drive':
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.drive)
                    self.close()
                case 'tab_yandex_disk':
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.yandex)
                    self.close()
                case 'tab_ftp':
                    if self.ui.checkBox_ftp_tls.isChecked():
                        explicit_tls = str(
                            self.ui.radioButton_ftp_true.isChecked()).lower()
                    else:
                        explicit_tls = 'false'
                    rclone.create_remote(name,
                                         remote_type=remote_types.RemoteTypes.ftp,
                                         host=self.ui.lineEdit_ftp_host.text().strip(),
                                         port=self.ui.lineEdit_ftp_port.text().strip(),
                                         user=self.ui.lineEdit_ftp_login.text().strip(),
                                         tls=str(
                                             self.ui.checkBox_ftp_tls.isChecked()).lower(),
                                         explicit_tls=explicit_tls
                                         )
                    if self.ui.lineEdit_ftp_password.text().strip() != '':
                        rc.config('password', name, 'pass',
                                  self.ui.lineEdit_ftp_password.text().strip())
                    self.close()
                case 'tab_webdav':
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
                case 'tab_http':
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.http, url=self.ui.lineEdit_url.text().strip())
                    self.close()
                case 'tab_local':
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.local)
                    self.close()
                case 'tab_onedrive':
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.onedrive)
                    self.close()
                case 'tab_mailru':
                    rclone.create_remote(name, remote_type=remote_types.RemoteTypes.mailru,
                                         user=self.ui.lineEdit_mailru_login.text().strip())
                    if self.ui.lineEdit_mailru_password.text().strip() != '':
                        rc.config('password', name, 'pass',
                                  self.ui.lineEdit_mailru_password.text().strip())
                    self.close()
                case 'tab_sftp':
                    rclone.create_remote(name,
                                         remote_type=remote_types.RemoteTypes.sftp,
                                         host=self.ui.lineEdit_sftp_host.text().strip(),
                                         port=self.ui.lineEdit_sftp_port.text().strip(),
                                         user=self.ui.lineEdit_sftp_login.text().strip()
                                         )
                    if self.ui.lineEdit_sftp_password.text().strip() != '':
                        rc.config('password', name, 'pass',
                                  self.ui.lineEdit_sftp_password.text().strip())
                    self.close()
                case 'tab_alias':
                    rclone.create_remote(
                        name, remote_type='alias', remote=self.ui.lineEdit_alias_path.text().strip())
                    self.close()
                case 'tab_alias':
                    self.close()
        else:
            QMessageBox.warning(self, 'Enter name',
                                'Enter name for new remote')


class Task():
    def __init__(self, operation: str, source: str = '', destination: str = '', process: subprocess.Popen = None):
        self.operation = operation
        self.source = source
        self.destination = destination
        self.status = 'Running'
        self.size = ''
        self.full_size = 0
        self.progress = 0
        self.speed = ''
        self.estimated = ''
        self.process = process

    def done(self):
        self.status = 'Done'

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
    scale: int

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.tree_files.header().resizeSection(0, 300)
        self.ui.tree_files.header().resizeSection(1, 80)
        self.ui.tree_files.header().resizeSection(2, 120)
        self.ui.tree_files.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.ui.tree_remotes.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.ui.tree_remotes.setIconSize(QSize(28, 28))
        self.ui.dock_tasks.hide()

        self.ui.action_exit.triggered.connect(self.close)
        self.ui.action_new_remote.triggered.connect(
            self.open_new_remote_window)
        self.ui.action_new_serve.triggered.connect(self.open_new_serve_window)
        self.ui.action_list_remotes.triggered.connect(self.open_list_remotes)
        self.ui.action_settings.triggered.connect(self.open_settings_window)

        self.ui.tree_remotes.itemClicked.connect(self.open_remote)
        self.ui.tree_files.itemDoubleClicked.connect(
            lambda item: self.open_item(item.text(0), item.text(3) == 'inode/directory'))
        self.ui.tasks.itemDoubleClicked.connect(self.open_task_dir)

        self.ui.button_exit_dir.clicked.connect(self.exit_folder)
        self.ui.button_update.clicked.connect(lambda: asyncio.ensure_future(
            self.update_dir(self.current_remote, self.remotes_paths.setdefault(self.current_remote, ''))))

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

        self.slider_scale: QSlider = QSlider()
        self.slider_scale.setFixedWidth(128)
        self.slider_scale.setMinimum(0)
        self.slider_scale.setMaximum(16)
        self.slider_scale.setValue(2)
        self.set_scale(2)
        self.slider_scale.setOrientation(Qt.Orientation.Horizontal)
        self.slider_scale.valueChanged.connect(self.set_scale)
        self.ui.statusbar.addPermanentWidget(self.slider_scale)

        self.update_remotes()

        self.timer = QTimer(interval=500)
        self.timer.timeout.connect(self.timer_update)
        self.timer.start()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon.fromTheme('folder'))
        self.tray_icon.setContextMenu(self.context_menu_tray_icon())
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

    def tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason):
        match reason:
            case QSystemTrayIcon.ActivationReason.DoubleClick:
                self.show()
                self.activateWindow()

    def timer_update(self):
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
                    case 'Mount':
                        item.setIcon(0, QIcon.fromTheme('drive-harddisk'))
                    case 'Serve':
                        item.setIcon(0, QIcon.fromTheme(
                            'applications-internet'))
                self.ui.tasks.addTopLevelItem(item)
            else:
                item = self.ui.tasks.topLevelItem(i)

            item.setText(0, self.tasks[i].operation)
            item.setText(1, self.tasks[i].source)
            item.setText(2, self.tasks[i].destination)

            if len(rc.tasks) > i:
                if self.tasks[i].operation in ['Upload', 'Download', 'Opening']:
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

    def closeEvent(self, event: QCloseEvent):
        if self.isVisible():
            event.ignore()
            self.hide()
        else:
            if self.temp_dir != '':
                shutil.rmtree(self.temp_dir)
            event.accept()
            if os.name == 'nt':
                os._exit(0)
            else:
                sys.exit(0)

    def set_scale(self, index: int):
        sizes = [18, 22, 32, 48, 64, 80, 96, 112, 128,
                 144, 160, 176, 192, 208, 224, 240, 256]
        sizes_icon = [16, 16, 22, 34, 48, 64, 80, 96,
                      112, 128, 144, 160, 176, 192, 208, 224, 240]
        value = sizes[index]
        self.scale = value
        self.slider_scale.setToolTip(f'{value}px')

        self.ui.tree_files.setIconSize(
            QSize(sizes_icon[index], sizes_icon[index]))
        for i in range(self.ui.tree_files.topLevelItemCount()):
            item = self.ui.tree_files.topLevelItem(i)
            item.setSizeHint(0, QSize(0, value))

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

        handler = FileMonitorHandler('.cloud_explorer_file_temp')

        if os.name == 'nt':
            observers = []
            drives = win32api.GetLogicalDriveStrings()
            drives = drives.replace('\x00', '').split('\\')[:-1]

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
            observer.schedule(handler, os.environ['HOME'], recursive=True)
            observer.start()

        drag.setPixmap(QIcon.fromTheme(
            'emblem-documents').pixmap(QSize(64, 64)))
        drag.exec(Qt.DropAction.CopyAction)

        if os.name == 'nt':
            for obs in observers:
                obs.stop()
        else:
            observer.stop()

        if self.download_path != '':
            os.remove(self.download_path)
            self.download_file(self.ui.tree_files.selectedItems(
            ), self.download_path[:-len('.cloud_explorer_file_temp') - 1])

    def update_remotes(self):
        remotes = rc.listremotes(True)
        self.ui.tree_remotes.clear()
        for remote in remotes:
            item = QTreeWidgetItem([remote['name'] + ':', remote['type']])
            item.setSizeHint(0, QSize(0, 32))
            if QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark:
                inv = '_inv'
            else:
                inv = ''

            file = f'{os.path.dirname(__file__) + os.sep}images{os.sep}{remote['type']}{inv}.png'
            if not os.path.isfile(file):
                file = f'{os.path.dirname(__file__) + os.sep}images{os.sep}unknown{inv}.png'
            item.setIcon(0, QPixmap(file))
            self.ui.tree_remotes.addTopLevelItem(item)

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

    def open_new_remote_window(self):
        open_win = NewRemoteWindow()
        open_win.exec()
        self.update_remotes()

    def open_new_serve_window(self):
        open_win = NewServeWindow()
        open_win.exec()

    def open_list_remotes(self):
        self.ui.tree_remotes.setVisible(not self.ui.tree_remotes.isVisible())

    def open_settings_window(self):
        open_win = SettingsWindow()
        open_win.exec()

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
        button.clicked.connect(lambda t, remote_name=remote_name: asyncio.ensure_future(
            self.open_dir(remote_name)))
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
                def lt(self, other_item):
                    column = self.treeWidget().sortColumn()
                    if self.text(3) == 'inode/directory' and other_item.text(3) != 'inode/directory':
                        return True
                    elif other_item.text(3) == 'inode/directory' and self.text(3) != 'inode/directory':
                        return False
                    return self.text(column).lower() < other_item.text(column).lower()

                self.ui.tree_files.clear()
                for file in tree:
                    item = QTreeWidgetItem(
                        [file['name'], file['size'], file['modified'], file['type']])
                    item.setTextAlignment(
                        1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
                    item.setSizeHint(0, QSize(0, self.scale))
                    item.__lt__ = types.MethodType(lt, item)

                    if file['is_dir']:
                        item.setIcon(0, QIcon.fromTheme('folder'))
                    else:
                        if os.name == 'nt':
                            item.setIcon(0, QIcon.fromTheme(
                                'emblem-documents'))
                        else:
                            type_file = file['type'].split(
                                ';')[0].replace('/', '-')
                            if QIcon.fromTheme(type_file):
                                item.setIcon(0, QIcon.fromTheme(type_file))
                            else:
                                item.setIcon(0, QIcon.fromTheme('text-plain'))
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

    def mount_remote(self, name: str, type: str):
        if os.name == 'nt':
            if type in ['local', 'alias', 'union']:
                process = rc.mount(name, '*')
            else:
                process = rc.mount(name, '*', '--network-mode')
            self.tasks.append(
                Task(operation='Mount', source=name, process=process))
            self.ui.dock_tasks.show()
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

    async def delete_file(self, items: list[QTreeWidgetItem]):
        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        files = []
        for item in items:
            files.append([item.text(0), item.text(3) == 'inode/directory'])
            item.setHidden(True)

        if len(items) == 1:
            question = f'Are you sure you want to delete {items[0].text(0)} ?'
        else:
            question = f'Are you sure you want to delete {len(items)} files ?'
        confirmation = QMessageBox.question(self, 'Delete', question)
        if confirmation == QMessageBox.Yes:
            for file in files:
                if destination_path != '':
                    file_path = f'{destination_remote}{destination_path}/{file[0]}'
                else:
                    file_path = f'{destination_remote}{file[0]}'

                task = Task(operation='Delete',
                            source=f'{self.current_remote}{file_path}')
                self.tasks.append(task)
                self.ui.dock_tasks.show()

                if file[1]:
                    await rc.purge(file_path)
                else:
                    await rc.deletefile(file_path)
                task.done()
                self.clear_cache(destination_remote, destination_path)

    async def update_dir(self, remote_name: str, path: str):
        if remote_name != '':
            self.clear_cache(remote_name, path)

            if f'{remote_name}{path}' == f'{self.current_remote}{self.remotes_paths[self.current_remote]}':
                await self.open_dir(remote_name, path, update=True)

    def paste_file(self):
        clipboard = QApplication.clipboard()

        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        for url in clipboard.mimeData().urls():
            source_path = url.toLocalFile()
            asyncio.ensure_future(self.upload_file(
                source_path, destination_remote, destination_path))

    def exit_folder(self):
        if self.current_remote != '' and self.remotes_paths[self.current_remote] != '':
            path_dir = f'{self.remotes_paths[self.current_remote]}'
            path = '/'.join(path_dir.split('/')[:-1])
            asyncio.ensure_future(self.open_dir(self.current_remote, path))

    async def new_folder(self):
        folder_name, ok = QInputDialog.getText(
            self, "New Folder", "Enter folder name:", text="New Folder")

        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        if ok and folder_name.strip():
            if destination_path != '':
                folder_path = f'{destination_remote}{destination_path}/{folder_name.strip()}'
            else:
                folder_path = f'{destination_remote}{destination_path}{folder_name.strip()}'
            await rc.mkdir(folder_path)
            await self.update_dir(destination_remote, destination_path)

    async def rename_file(self, file_name: str, is_dir: bool):
        new_file_name, ok = QInputDialog.getText(
            self, "Rename", "Enter new name:", text=file_name)

        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        if ok and new_file_name.strip():
            if destination_path != '':
                new_file_path = f'{destination_remote}{destination_path}/{new_file_name.strip()}'
                old_file_path = f'{destination_remote}{destination_path}/{file_name}'
            else:
                new_file_path = f'{destination_remote}{destination_path}{new_file_name.strip()}'
                old_file_path = f'{destination_remote}{destination_path}{file_name}'
            await rc.moveto(old_file_path, new_file_path)
            await self.update_dir(destination_remote, destination_path)

    def delete_remote(self, name: str):
        rc.config('delete', f'"{name[:-1]}"')
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

    def stop_task(self, index: int):
        self.tasks[index].process.send_signal(signal.CTRL_BREAK_EVENT)
        self.ui.tasks.takeTopLevelItem(index)
        del self.tasks[index]

    def add_to_autostart(app_name, executable_path):
        if os.name == 'nt':
            key = winreg.HKEY_CURRENT_USER
            reg_path = r'Software\\Microsoft\\Windows\\CurrentVersion\\Run'

            try:
                with winreg.OpenKey(key, reg_path, 0, winreg.KEY_SET_VALUE) as reg_key:
                    winreg.SetValueEx(reg_key, app_name, 0,
                                      winreg.REG_SZ, executable_path)
            except Exception as e:
                print(f'Error: {e}')

    def show_context_menu_tree(self, point):
        index = self.ui.tree_files.indexAt(point)
        selected = self.ui.tree_files.selectedItems()

        menu = QMenu()

        if self.current_remote != '':
            if not index.isValid():
                action = QAction(self)
                action.setText('Paste')
                action.setIcon(QIcon.fromTheme('edit-paste'))
                action.triggered.connect(lambda: self.paste_file())
                menu.addAction(action)

                action = QAction(self)
                action.setText('New Folder')
                action.setIcon(QIcon.fromTheme('folder-new'))
                action.triggered.connect(
                    lambda: asyncio.ensure_future(self.new_folder()))
                menu.addAction(action)
            else:
                item = self.ui.tree_files.itemAt(point)
                file_name = item.text(0)
                is_dir = item.text(3) == 'inode/directory'

                action = QAction(self)
                action.setText('Open')
                action.setIcon(QIcon.fromTheme('document-open'))
                action.triggered.connect(
                    lambda: self.open_item(file_name, is_dir))
                menu.addAction(action)

                action = QAction(self)
                action.setText('Download')
                action.setIcon(QIcon.fromTheme('emblem-downloads'))
                action.triggered.connect(
                    lambda: self.download_file(selected))
                menu.addAction(action)

                menu.addSeparator()

                action = QAction(self)
                action.setText('Copy')
                action.setIcon(QIcon.fromTheme('edit-copy'))
                action.triggered.connect(lambda: self.copy_file(file_name))
                menu.addAction(action)

                action = QAction(self)
                action.setText('Paste')
                action.setIcon(QIcon.fromTheme('edit-paste'))
                action.triggered.connect(lambda: self.paste_file())
                menu.addAction(action)

                menu.addSeparator()

                action = QAction(self)
                action.setText('Rename')
                action.setIcon(QIcon.fromTheme('format-text-italic'))
                action.triggered.connect(lambda: asyncio.ensure_future(
                    self.rename_file(file_name, is_dir)))
                menu.addAction(action)

                action = QAction(self)
                action.setText('Delete')
                action.setIcon(QIcon.fromTheme('edit-delete'))
                action.triggered.connect(
                    lambda: asyncio.ensure_future(self.delete_file(selected)))
                menu.addAction(action)

                menu.addSeparator()

                action = QAction(self)
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

        action = QAction(self)
        action.setText('Open')
        action.setIcon(QIcon.fromTheme('folder-open'))
        action.triggered.connect(lambda: self.open_remote(item))
        menu.addAction(action)

        action = QAction(self)
        action.setText('Edit')
        action.setIcon(QIcon.fromTheme('applications-development'))
        action.triggered.connect(lambda: self.edit_remote(item.text(0)))
        menu.addAction(action)

        action = QAction(self)
        action.setText('Mount')
        action.setIcon(QIcon.fromTheme('drive-harddisk'))
        action.triggered.connect(
            lambda: self.mount_remote(item.text(0), item.text(1)))
        menu.addAction(action)

        action = QAction(self)
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

        if item.text(0) in ['Download', 'Upload', 'Opening']:
            action = QAction(self)
            action.setText('Open folder')
            action.setIcon(QIcon.fromTheme('folder-open'))
            action.triggered.connect(lambda: self.open_task_dir(item))
            menu.addAction(action)

        if item.text(3) == 'Done':
            action = QAction(self)
            action.setText('Clear')
            action.setIcon(QIcon.fromTheme('edit-clear'))
            action.triggered.connect(lambda: self.clear_task(index.row()))
            menu.addAction(action)

        if item.text(0) in ['Mount', 'Serve']:
            action = QAction(self)
            action.setText('Stop')
            action.triggered.connect(lambda: self.stop_task(index.row()))
            menu.addAction(action)

        menu.exec(QCursor.pos())

    def context_menu_tray_icon(self):
        menu = QMenu()

        def close():
            self.hide()
            self.close()

        action = QAction(self)
        action.setText('Exit')
        action.setIcon(QIcon.fromTheme('application-exit'))
        action.triggered.connect(close)
        menu.addAction(action)

        return menu


def is_already_running(server_name: str):
    socket = QLocalSocket()
    socket.connectToServer(server_name)
    if socket.waitForConnected(100):
        socket.write(b'ACTIVATE')
        socket.flush()
        socket.disconnectFromServer()
        return True
    return False


def start_server(window: MainWindow, server_name: str):
    server = QLocalServer()
    try:
        server.removeServer(server_name)  # На случай краша предыдущего запуска
    except:
        pass
    server.listen(server_name)

    def on_new_connection():
        client = server.nextPendingConnection()
        if client:
            client.waitForReadyRead(100)
            window.show()
            window.activateWindow()
            client.disconnectFromServer()

    server.newConnection.connect(on_new_connection)


if __name__ == '__main__':
    app = QApplication()

    server_name = 'Cloud Explorer'
    server = QLocalServer()

    if is_already_running(server_name):
        print('The application has already been launched')
        sys.exit(0)

    window = MainWindow()
    settings = QSettings('Denis Mazur', 'Cloud Explorer')
    app.setStyle(settings.value('style', ''))
    window.show()

    start_server(window, server_name)

    sys.exit(QtAsyncio.run())
