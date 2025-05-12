from argparse import Action
import asyncio
import shutil
import signal
import sys
import os
import subprocess
import threading
import types
import json

from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QFileInfo, QLibraryInfo, QLocale, QMimeData, QPoint, QSettings, QSize, QTranslator, QUrl, Qt, QTimer, QRegularExpression
from PySide6.QtGui import QCloseEvent, QColorConstants, QDesktopServices, QDrag, QDragEnterEvent, QIcon, QAction, QCursor, QKeySequence, QPainter, QPixmap, QRegularExpressionValidator, QShortcut
from PySide6.QtWidgets import QFileIconProvider, QHBoxLayout, QInputDialog, QMainWindow, QApplication, QDialog, QMenu, QFileDialog, QProgressBar, QSizePolicy, QSlider, QStyleFactory, QSystemTrayIcon, QTreeWidgetItem, QPushButton, QMessageBox, QLabel, QWidget, QSpacerItem
import PySide6.QtAsyncio as QtAsyncio

from rclone_python import rclone
from rclone_python import remote_types
from rclone import Rclone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from palettes import palettes

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
            window.download_path = event.src_path[:-
                                                  len(os.path.basename(self.target_file)) - 1]
            while True:
                try:
                    os.remove(event.src_path)
                    break
                except PermissionError:
                    pass
                except FileNotFoundError:
                    break


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

        palettes_list = palettes.keys()
        self.ui.comboBox_palette.addItems(palettes_list)
        self.ui.comboBox_palette.setCurrentText(
            settings.value('palette', 'System'))

        self.ui.buttonBox.accepted.connect(self.ok)

    def ok(self):
        app.setStyle(self.ui.comboBox_style.currentText())
        app.setPalette(palettes[self.ui.comboBox_palette.currentText()])

        settings.setValue('style', self.ui.comboBox_style.currentText())
        settings.setValue('palette', self.ui.comboBox_palette.currentText())


class NewServeWindow(QDialog):
    def __init__(self):
        super(NewServeWindow, self).__init__()
        self.ui = new_serve_window.Ui_NewServeWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(
            QIcon(f'{os.path.dirname(__file__) + os.sep}favicon.ico'))

        self.ui.buttonBox.accepted.connect(self.new_serve)
        self.ui.button_select_dir.clicked.connect(self.select_dir)

    def select_dir(self):
        path = QFileDialog.getExistingDirectory()
        if path is not None and path != '':
            self.ui.lineEdit_path.setText(path)

    def new_serve(self):
        path = self.ui.lineEdit_path.text()
        user = self.ui.lineEdit_username.text()
        password = self.ui.lineEdit_password.text()
        address = self.ui.lineEdit_address.text()
        read_only = self.ui.checkBox_read_only.isChecked()
        args = ''
        if self.ui.radioButton_ftp.isChecked():
            protocol = 'ftp'
            if address.strip() == '':
                address = 'localhost:2121'
        elif self.ui.radioButton_dnla.isChecked():
            protocol = 'dnla'
            if address.strip() == '':
                address = ':7879'
        elif self.ui.radioButton_http.isChecked():
            protocol = 'http'
            read_only = True
            if address.strip() == '':
                address = '127.0.0.1:8080'
        elif self.ui.radioButton_webdav.isChecked():
            protocol = 'webdav'
            if address.strip() == '':
                address = '127.0.0.1:8080'
        elif self.ui.radioButton_sftp.isChecked():
            protocol = 'sftp'
            if not user or not password:
                args += '--no-auth'
            if address.strip() == '':
                address = 'localhost:2022'

        process: subprocess.Popen = rc.serve(
            protocol, path, user, password, address, read_only, args)
        try:
            process.wait(1)
            QMessageBox.critical(self, self.tr('Error'),
                                 self.tr('Check the data!'))
        except subprocess.TimeoutExpired:
            window.serve.append(Serve(protocol, path, address, user, password, read_only=read_only, process=process))
            self.close()


class NewRemoteWindow(QDialog):
    def __init__(self, edit_mode: bool = False, remote_name: str = None):
        super(NewRemoteWindow, self).__init__()
        self.ui = new_remote_window.Ui_NewRemoteWindow()
        self.ui.setupUi(self)

        self.setWindowIcon(
            QIcon(f'{os.path.dirname(__file__) + os.sep}favicon.ico'))

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
                    self.ui.lineEdit_webdav_url.setText(url)
                    self.ui.lineEdit_webdav_login.setText(user)
                    match config[remote_name[:-1]].setdefault('vendor', 'other'):
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
                    match config[remote_name[:-1]].setdefault('region', 'global'):
                        case 'us':
                            region = 1
                        case 'cn':
                            region = 2
                        case _:
                            region = 0
                    self.ui.comboBox_onedrive_region.setCurrentIndex(region)
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
                    vendor = ['other', 'fastmail', 'nextcloud', 'owncloud', 'sharepoint',
                              'sharepoint-ntlm', 'rclone'][self.ui.comboBox_webdav_vendor.currentIndex()]
                    rclone.create_remote(name,
                                         remote_type=remote_types.RemoteTypes.webdav,
                                         url=self.ui.lineEdit_webdav_url.text().strip(),
                                         user=self.ui.lineEdit_webdav_login.text().strip(),
                                         vendor=vendor
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
                    region = [
                        'global', 'us', 'cn'][self.ui.comboBox_onedrive_region.currentIndex()]
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.onedrive, region=region)
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
                case 'tab_union':
                    self.close()
        else:
            QMessageBox.warning(self, self.tr('Enter name'),
                                self.tr('Enter name for new remote') + '!')


class Task():
    last_index = 0

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

        match operation:
            case 'Download' | 'Upload' | 'Opening':
                self.index = Task.last_index
                Task.last_index += 1
            case _:
                self.index = -1

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

class Serve():
    def __init__(self, protocol: str, path: str, address: str, user: str, password: str, read_only: bool, process: subprocess.Popen = None):
        self.protocol = protocol
        self.path = path
        self.address = address
        self.user = user
        self.password = password
        self.read_only = read_only
        self.process = process

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
    copy_files: list = []
    history: dict = {}
    serve: list[Serve] = []

    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = main_window.Ui_MainWindow()
        self.ui.setupUi(self)

        self.search_process_is_running: int = 0

        self.setWindowIcon(
            QIcon(f'{os.path.dirname(__file__) + os.sep}favicon.ico'))

        self.ui.tree_files.header().resizeSection(0, 300)
        self.ui.tree_files.header().resizeSection(1, 80)
        self.ui.tree_files.header().resizeSection(2, 120)
        self.ui.treeWidget_search.header().resizeSection(0, 300)
        self.ui.treeWidget_search.header().resizeSection(1, 80)
        self.ui.treeWidget_search.header().resizeSection(2, 120)

        self.ui.tree_files.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.ui.tree_remotes.header().setSortIndicator(0, Qt.SortOrder.AscendingOrder)
        self.ui.tree_remotes.setIconSize(QSize(28, 28))
        self.ui.dock_tasks.hide()

        def close():
            self.hide()
            self.close()

        self.ui.action_exit.triggered.connect(close)
        self.ui.action_new_remote.triggered.connect(
            self.open_new_remote_window)
        self.ui.action_new_serve.triggered.connect(self.open_new_serve_window)
        self.ui.action_list_remotes.triggered.connect(self.open_list_remotes)
        self.ui.action_settings.triggered.connect(self.open_settings_window)
        self.ui.action_about.triggered.connect(
            lambda: QMessageBox.aboutQt(self))
        self.ui.action_show_tasks.triggered.connect(self.ui.dock_tasks.show)

        self.ui.tree_remotes.itemClicked.connect(self.open_remote)
        self.ui.tree_files.itemDoubleClicked.connect(
            lambda item: self.open_item(item.data(0, Qt.ItemDataRole.UserRole)['remote'], item.data(0, Qt.ItemDataRole.UserRole)['path'], item.data(0, Qt.ItemDataRole.UserRole)['name'], item.data(0, Qt.ItemDataRole.UserRole)['is_dir']))
        self.ui.treeWidget_search.itemDoubleClicked.connect(
            lambda item: self.open_item(item.data(0, Qt.ItemDataRole.UserRole)['remote'], item.data(0, Qt.ItemDataRole.UserRole)['path'], item.data(0, Qt.ItemDataRole.UserRole)['name'], item.data(0, Qt.ItemDataRole.UserRole)['is_dir']))
        self.ui.tasks.itemDoubleClicked.connect(self.open_task_dir)

        self.ui.button_exit_dir.clicked.connect(self.exit_folder)
        self.ui.button_update.clicked.connect(lambda: asyncio.ensure_future(
            self.update_dir(self.current_remote, self.remotes_paths.setdefault(self.current_remote, ''))))
        self.ui.button_prev_history.clicked.connect(self.prev_history)
        self.ui.button_next_history.clicked.connect(self.next_history)
        self.ui.button_new_serve.clicked.connect(self.open_new_serve_window)
        self.ui.button_search.clicked.connect(
            lambda: asyncio.ensure_future(self.search()))
        self.ui.lineEdit_search.editingFinished.connect(
            lambda: asyncio.ensure_future(self.search()))

        self.ui.tree_files.startDrag = self.start_drag
        self.ui.treeWidget_search.startDrag = self.start_drag

        self.ui.tree_files.customContextMenuRequested.connect(
            self.show_context_menu_tree)
        self.ui.treeWidget_search.customContextMenuRequested.connect(
            self.show_context_menu_tree_search)
        self.ui.tree_remotes.customContextMenuRequested.connect(
            self.show_context_menu_remote)
        self.ui.treeWidget_serve.customContextMenuRequested.connect(
            self.show_context_menu_serve)
        self.ui.tasks.customContextMenuRequested.connect(
            self.show_context_menu_task)

        statusbar_widget = QWidget()
        h_layout = QHBoxLayout(statusbar_widget)
        h_layout.setContentsMargins(0, 0, 9, 0)

        self.slider_scale: QSlider = QSlider(statusbar_widget)
        self.slider_scale.setFixedWidth(128)
        self.slider_scale.setMinimum(0)
        self.slider_scale.setMaximum(16)
        self.slider_scale.setValue(2)
        self.set_scale(2)
        self.slider_scale.setOrientation(Qt.Orientation.Horizontal)
        self.slider_scale.valueChanged.connect(self.set_scale)

        self.layout_free_size = QLabel('', statusbar_widget)
        h_layout.addItem(QSpacerItem(
            0, 0, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        h_layout.addWidget(self.layout_free_size)
        h_layout.addWidget(QLabel(self.tr('Scale') + ':', statusbar_widget))
        h_layout.addWidget(self.slider_scale)
        self.ui.statusbar.addPermanentWidget(statusbar_widget)

        self.update_remotes()

        self.timer = QTimer(interval=500)
        self.timer.timeout.connect(self.timer_update)
        self.timer.start()

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.windowIcon())
        self.tray_icon.setContextMenu(self.context_menu_tray_icon())
        self.tray_icon.activated.connect(self.tray_icon_activated)
        self.tray_icon.show()

        self.start_file_monitor()
        self.shortcuts()

    def tray_icon_activated(self, reason: QSystemTrayIcon.ActivationReason):
        match reason:
            case QSystemTrayIcon.ActivationReason.Trigger:
                self.show()
                self.activateWindow()

    def timer_update(self):
        if self.download_path != '':
            self.download_file(self.copy_files, self.download_path)
            self.download_path = ''

        for i in range(len(self.serve)):
            if i >= self.ui.treeWidget_serve.topLevelItemCount():
                item = QTreeWidgetItem()
                self.ui.treeWidget_serve.addTopLevelItem(item)
                item.setText(0, self.serve[i].protocol)
                item.setText(1, self.serve[i].path)
                item.setText(2, self.serve[i].address)
                item.setText(3, self.serve[i].user)
                item.setText(4, self.serve[i].password)
                item.setText(5, '+' if self.serve[i].read_only else '-')


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
                    case 'Delete':
                        item.setIcon(0, QIcon.fromTheme('edit-delete'))
                self.ui.tasks.addTopLevelItem(item)
                self.ui.dock_tasks.show()
            else:
                item = self.ui.tasks.topLevelItem(i)

            item.setText(0, self.tasks[i].operation)
            item.setText(1, self.tasks[i].source)
            item.setText(2, self.tasks[i].destination)
            item.setText(3, self.tasks[i].status)

            if self.tasks[i].index != -1:
                if self.tasks[i].operation in ['Upload', 'Download', 'Opening']:
                    self.tasks[i].set_full_size(
                        rc.tasks[self.tasks[i].index]['full_size'])
                    self.tasks[i].set_size(
                        rc.tasks[self.tasks[i].index]['current_size'])
                    self.tasks[i].set_speed(
                        rc.tasks[self.tasks[i].index]['speed'])
                    self.tasks[i].set_estimated(
                        rc.tasks[self.tasks[i].index]['estimated'])
                    self.tasks[i].set_status(
                        rc.tasks[self.tasks[i].index]['is_done'])

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

    def start_file_monitor(self):
        if self.temp_dir == '':
            self.temp_dir = rclone.tempfile.mkdtemp(prefix='cloud_explorer-')
        open(self.temp_dir + '/.cloud_explorer_file_temp', 'a').close()

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
            observer_thread = threading.Thread(target=observer.start)
            observer_thread.daemon = True
            observer_thread.start()

    async def search(self):
        remote_name = self.ui.comboBox_search.currentText()
        text = self.ui.lineEdit_search.text()

        self.search_process_is_running += 1
        search_process_is_running = self.search_process_is_running

        self.ui.statusbar.showMessage(f'Search in {remote_name}')
        self.ui.treeWidget_search.clear()
        process = rc.search(remote_name, 20)

        loop = asyncio.get_running_loop()

        while True:
            line = await loop.run_in_executor(None, process.stdout.readline)
            if not line or search_process_is_running != self.search_process_is_running:
                break
            line = line.decode()

            if 'error' in line:
                print(line)

            if len(line) > 10:
                line = json.loads(line.replace(',\n', ''))
                sizes = ['B', 'KB', 'MB', 'GB', 'TB']
                index = 0
                size = line['Size']
                name = line['Name']
                modified = line['ModTime']
                is_dir = line['IsDir']
                type = line['MimeType']
                path = remote_name + line['Path']

                if is_dir:
                    size = ''
                else:
                    for _ in range(4):
                        if size >= 1024:
                            size = round(float(size) / 1024, 2)
                            index += 1
                    size = f'{size} {sizes[index]}'

                modified = modified.replace(
                    'T', ' ').replace('Z', ' ').split('.')[0]
                file = {'name': name, 'size': size, 'modified': modified,
                        'path': path, 'is_dir': is_dir, 'type': type}

                if file['name'].lower().rfind(text.lower()) != -1:
                    item = QTreeWidgetItem(
                        [file['name'], file['size'], file['modified'], file['type'], file['path']])
                    item.setTextAlignment(
                        1, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
                    item.setSizeHint(0, QSize(0, self.scale))

                    if file['is_dir']:
                        icon = QFileIconProvider().icon(QFileIconProvider().IconType.Folder)
                        item.setIcon(0, icon)
                    else:
                        file_info = QFileInfo(file['name'])
                        icon = QFileIconProvider().icon(file_info)
                        item.setIcon(0, icon)
                    item.setData(0, Qt.ItemDataRole.UserRole, {
                                 'name': file['name'], 'remote': remote_name, 'path': line['Path'], 'is_dir': file['is_dir']})
                    self.ui.treeWidget_search.addTopLevelItem(item)

        if search_process_is_running == self.search_process_is_running:
            self.ui.statusbar.showMessage('')

    async def update_free_size(self, remote_name: str, clear: bool = False):
        if clear:
            self.layout_free_size.setText('')
        size = await rc.about(remote_name)
        free = size['free']
        total = size['total']

        sizes = ['B', 'KB', 'MB', 'GB', 'TB']
        index_free = 0
        for _ in range(4):
            if free >= 1024:
                free = round(float(free) / 1024, 2)
                index_free += 1

        index_total = 0
        for _ in range(4):
            if total >= 1024:
                total = round(float(total) / 1024, 2)
                index_total += 1

        total_text = self.tr('Total')
        free_text = self.tr('Free')
        self.layout_free_size.setText(
            f'{total_text}: {total} {sizes[index_total]} | {free_text}: {free} {sizes[index_free]}    ')

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
        self.ui.treeWidget_search.setIconSize(
            QSize(sizes_icon[index], sizes_icon[index]))

        for i in range(self.ui.tree_files.topLevelItemCount()):
            item = self.ui.tree_files.topLevelItem(i)
            item.setSizeHint(0, QSize(0, value))

        for i in range(self.ui.treeWidget_search.topLevelItemCount()):
            item = self.ui.treeWidget_search.topLevelItem(i)
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
        match self.ui.tabWidget.currentIndex():
            case 0:
                items = self.ui.tree_files.selectedItems()
            case 1:
                items = self.ui.treeWidget_search.selectedItems()

        if items is None or len(items) == 0:
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

        match len(items):
            case 1 | 2 | 3 | 4:
                icon_size = 64
                pixmap_size = 132
            case 5 | 6 | 7 | 8 | 9:
                icon_size = 48
                pixmap_size = 150
            case 10 | 11 | 12 | 13 | 14 | 15 | 16:
                icon_size = 32
                pixmap_size = 136
            case _:
                icon_size = 16
                pixmap_size = 144

        pixmap = QPixmap(QSize(pixmap_size, pixmap_size))
        pixmap.fill(QColorConstants.Transparent)
        painter = QPainter(pixmap)

        i = 0
        is_i_max = False
        j = 0
        self.copy_files = []
        for item in items:
            self.copy_files.append(item.data(0, Qt.ItemDataRole.UserRole))

            painter.drawPixmap(i, j, item.icon(
                0).pixmap(QSize(icon_size, icon_size)).scaled(icon_size, icon_size))
            if j < pixmap_size:
                i += icon_size + 2
                if i >= pixmap_size:
                    j += icon_size + 2
                    i = 0
                    is_i_max = True
        painter.end()

        if is_i_max:
            i = pixmap_size

        drag.setPixmap(pixmap)
        drag.setHotSpot(QPoint(i / 2, -9))
        drag.exec(Qt.DropAction.CopyAction)

    def prev_history(self):
        if self.current_remote in self.history.keys():
            if self.history[self.current_remote][1] > 0:
                self.history[self.current_remote][1] -= 1
                asyncio.ensure_future(self.open_dir(
                    self.current_remote, self.history[self.current_remote][0][self.history[self.current_remote][1]]))
                self.ui.button_next_history.setEnabled(True)
            if self.history[self.current_remote][1] < 1:
                self.ui.button_prev_history.setEnabled(False)

    def next_history(self):
        if self.current_remote in self.history.keys() and self.history[self.current_remote][1] < len(self.history[self.current_remote][0]) - 1:
            self.history[self.current_remote][1] += 1
            self.ui.button_prev_history.setEnabled(True)
            if self.history[self.current_remote][1] == len(self.history[self.current_remote][0]) - 1:
                self.ui.button_next_history.setEnabled(False)
            asyncio.ensure_future(self.open_dir(
                self.current_remote, self.history[self.current_remote][0][self.history[self.current_remote][1]]))

    def update_history(self):
        if self.current_remote in self.history.keys():
            if self.history[self.current_remote][0][self.history[self.current_remote][1]] != self.remotes_paths[self.current_remote]:
                self.history[self.current_remote][1] += 1
                self.history[self.current_remote][0] = self.history[self.current_remote][0][:self.history[self.current_remote][1]]
                self.history[self.current_remote][0].append(
                    self.remotes_paths[self.current_remote])
        else:
            self.history[self.current_remote] = [
                [self.remotes_paths[self.current_remote]], 0]

        if self.history[self.current_remote][1] > 0:
            self.ui.button_prev_history.setEnabled(True)
        else:
            self.ui.button_prev_history.setEnabled(False)

        if self.history[self.current_remote][1] < len(self.history[self.current_remote][0]) - 1:
            self.ui.button_next_history.setEnabled(True)
        else:
            self.ui.button_next_history.setEnabled(False)

    def update_remotes(self):
        remotes = rc.listremotes(True)
        remotes.sort(key=lambda x: x['name'].lower())
        self.ui.tree_remotes.clear()
        self.ui.comboBox_search.clear()
        for remote in remotes:
            item = QTreeWidgetItem([remote['name'] + ':', remote['type']])
            item.setSizeHint(0, QSize(0, 32))
            if QApplication.styleHints().colorScheme() == Qt.ColorScheme.Dark and QApplication.style().name() != 'windowsvista' and not (len(settings.value('palette', 'System')) > 5 and settings.value('palette', 'System')[-5:].lower() == 'light'):
                inv = '_inv'
            else:
                inv = ''

            file = f'{os.path.dirname(__file__) + os.sep}images{os.sep}{remote['type']}{inv}.png'
            if not os.path.isfile(file):
                file = f'{os.path.dirname(__file__) + os.sep}images{os.sep}unknown{inv}.png'
            item.setIcon(0, QPixmap(file))
            self.ui.tree_remotes.addTopLevelItem(item)
            self.ui.comboBox_search.addItem(
                QPixmap(file), remote['name'] + ':')
            self.ui.comboBox_remote.addItem(
                QPixmap(file), remote['name'] + ':')

    async def upload_file(self, source_path: str, destination_remote: str, destination_path: str):
        self.tasks.append(Task(operation='Upload', source=source_path,
                          destination=f'{destination_remote}{destination_path}'))
        is_dir = await rc.is_dir(source_path)

        dest_path = destination_path
        if is_dir:
            if len(destination_path) > 0 and destination_path[-1] != '/':
                dest_path += '/' + \
                    source_path.replace(
                        '\\', '/').split(':')[-1].split('/')[-1]
            else:
                dest_path += source_path.replace('\\',
                                                 '/').split(':')[-1].split('/')[-1]

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

        self.update_history()

        if path_dir != '':
            self.ui.button_exit_dir.setEnabled(True)
        else:
            self.ui.button_exit_dir.setEnabled(False)

        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()

        button = QPushButton(remote_name)
        button.setSizePolicy(QSizePolicy.Policy.Fixed,
                             QSizePolicy.Policy.Expanding)
        button.setFlat(True)
        button.setStyleSheet('QPushButton {font-weight: bold;}')
        button.setIcon(self.ui.tree_remotes.findItems(
            remote_name, Qt.MatchFlag.MatchContains)[0].icon(0))
        button.clicked.connect(lambda t, remote_name=remote_name: asyncio.ensure_future(
            self.open_dir(remote_name)))
        self.ui.path_list.addWidget(button)

        temp_path = ''
        for name in path_dir.split('/'):
            if name != '':
                temp_path += name + '/'
                arrow_label = QLabel("/")
                arrow_label.setStyleSheet('QLabel {font-weight: bold;}')
                arrow_label.setAlignment(Qt.AlignCenter)
                self.ui.path_list.addWidget(arrow_label)
                button = QPushButton(name)
                button.setSizePolicy(
                    QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
                button.setStyleSheet('QPushButton {font-weight: bold;}')
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
                        icon = QFileIconProvider().icon(QFileIconProvider().IconType.Folder)
                        item.setIcon(0, icon)
                    else:
                        file_info = QFileInfo(file['name'])
                        icon = QFileIconProvider().icon(file_info)
                        item.setIcon(0, icon)
                    item.setData(0, Qt.ItemDataRole.UserRole, {
                                 'name': file['name'], 'remote': remote_name, 'path': file['path'], 'is_dir': file['is_dir']})
                    self.ui.tree_files.addTopLevelItem(item)

            if not update:
                break

    def open_remote(self, item: QTreeWidgetItem):
        for i in range(self.ui.path_list.count()):
            self.ui.path_list.itemAt(i).widget().deleteLater()
        if item.text(0) not in self.remotes_paths.keys():
            self.remotes_paths[item.text(0)] = ''
        asyncio.ensure_future(self.open_dir(
            item.text(0), self.remotes_paths[item.text(0)]))
        asyncio.ensure_future(self.update_free_size(item.text(0), True))

    async def open_file(self, remote: str, file_path: str, file_name: str, is_with: bool = False):
        if self.temp_dir == '':
            self.temp_dir = rclone.tempfile.mkdtemp(prefix='cloud_explorer-')
        self.tasks.append(Task(
            operation='Opening', source=remote + file_path, destination=self.temp_dir))
        await rc.copy(remote + file_path, self.temp_dir)
        if not is_with:
            QDesktopServices.openUrl(QUrl.fromLocalFile(
                self.temp_dir + '/' + file_name))
        else:
            if os.name == 'nt':
                subprocess.run(
                    ['rundll32', 'shell32.dll,OpenAs_RunDLL', self.temp_dir + '\\' + file_name])
            else:
                QDesktopServices.openUrl(QUrl.fromLocalFile(
                    self.temp_dir + '/' + file_name))

    def open_item(self, remote: str, file_path: str, file_name: str, is_dir: bool, is_with: bool = False):
        if remote:
            if is_dir:
                asyncio.ensure_future(self.open_dir(
                    remote, file_path))
            else:
                asyncio.ensure_future(self.open_file(
                    remote, file_path, file_name, is_with))

    def download_file(self, list_files: list[dict], download_path: str = None):
        if download_path is None:
            download_path = QFileDialog.getExistingDirectory()
        if download_path is not None and download_path != '':
            for file in list_files:
                base_name = file.get(
                    'name', file['path'].split(':')[-1].split('/')[-1])
                file_path = file['path']
                source_remote = file['remote']

                self.tasks.append(Task(
                    operation='Download', source=f'{source_remote}{file_path}', destination=download_path))

                if not file['is_dir']:
                    asyncio.ensure_future(
                        rc.copy(source_remote + file_path, download_path))
                else:
                    if len(download_path) > 0 and download_path[-1] != '/' and download_path[-1] != '\\':
                        asyncio.ensure_future(rc.copy(
                            f'{source_remote}{file_path}', f'{download_path}/{base_name}'))
                    else:
                        asyncio.ensure_future(rc.copy(
                            f'{source_remote}{file_path}', f'{download_path}{base_name}'))

    def mount_remote(self, name: str, type: str):
        if os.name == 'nt':
            if type in ['local', 'alias', 'union']:
                process = rc.mount(name, '*')
            else:
                process = rc.mount(name, '*', '--network-mode')
            self.tasks.append(
                Task(operation='Mount', source=name, process=process))
        else:
            mount_path = QFileDialog.getExistingDirectory()
            if mount_path is not None and mount_path != '':
                rc.mount(f'"{name}"', f'"{mount_path}"')

    def copy_files(self, items: list[QTreeWidgetItem]):
        self.copy_files = []
        for item in items:
            self.copy_files.append(item.data(0, Qt.ItemDataRole.UserRole))

        clipboard = QApplication.clipboard()
        mime_data = QMimeData()
        mime_data.setText('.cloud_explorer_file_temp')
        url = QUrl.fromLocalFile(self.temp_dir + '/.cloud_explorer_file_temp')
        mime_data.setUrls([url])
        clipboard.setMimeData(mime_data)

    async def delete_files(self, files: list[dict]):
        if len(files) == 1:
            question = self.tr(
                'Are you sure you want to delete') + ' ' + files[0]['name'] + ' ?'
        else:
            question = self.tr('Are you sure you want to delete') + \
                ' ' + str(len(files)) + ' ' + self.tr('files') + ' ?'

        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle(self.tr('Delete'))
        msg_box.setText(question)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        async def delete(button):
            if msg_box.buttonRole(button) == QMessageBox.YesRole:
                for file in files:
                    file_path = file['remote'] + file['path']

                    task = Task(operation='Delete', source=file_path)
                    self.tasks.append(task)

                    if file['is_dir']:
                        await rc.purge(file_path)
                    else:
                        await rc.deletefile(file_path)
                    task.done()
                    items = self.ui.tree_files.findItems(
                        file['name'], Qt.MatchFlag.MatchContains)
                    if len(items) > 0 and items[0].data(0, Qt.ItemDataRole.UserRole)['remote'] == file['remote'] and items[0].data(0, Qt.ItemDataRole.UserRole)['path'] == file['path']:
                        items[0].setHidden(True)

                    items = self.ui.treeWidget_search.findItems(
                        file['name'], Qt.MatchFlag.MatchContains)
                    if len(items) > 0 and items[0].data(0, Qt.ItemDataRole.UserRole)['remote'] == file['remote'] and items[0].data(0, Qt.ItemDataRole.UserRole)['path'] == file['path']:
                        items[0].setHidden(True)

        msg_box.buttonClicked.connect(
            lambda button: asyncio.ensure_future(delete(button)))
        msg_box.show()

    async def update_dir(self, remote_name: str, path: str):
        if remote_name != '':
            self.clear_cache(remote_name, path)

            if f'{remote_name}{path}' == f'{self.current_remote}{self.remotes_paths[self.current_remote]}':
                await self.open_dir(remote_name, path, update=True)

    def paste_file(self):
        clipboard = QApplication.clipboard()

        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        if clipboard.mimeData().text() == '.cloud_explorer_file_temp':
            for file in self.copy_files:
                asyncio.ensure_future(self.upload_file(
                    file[0], destination_remote, destination_path))
        else:
            for url in clipboard.mimeData().urls():
                source_path = url.toLocalFile()
                asyncio.ensure_future(self.upload_file(
                    source_path, destination_remote, destination_path))

    def exit_folder(self):
        if self.current_remote != '' and self.remotes_paths[self.current_remote] != '':
            self.update_history()
            path_dir = f'{self.remotes_paths[self.current_remote]}'
            path = '/'.join(path_dir.split('/')[:-1])
            asyncio.ensure_future(self.open_dir(self.current_remote, path))

    async def new_folder(self):
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle(self.tr("New Folder"))
        input_dialog.setLabelText(self.tr("Enter folder name:"))
        input_dialog.setTextValue(self.tr("New Folder"))
        input_dialog.setModal(True)
        input_dialog.show()

        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        async def create_folder():
            folder_name = input_dialog.textValue().strip()
            if destination_path != '':
                folder_path = f'{destination_remote}{destination_path}/{folder_name.strip()}'
            else:
                folder_path = f'{destination_remote}{destination_path}{folder_name.strip()}'
            await rc.mkdir(folder_path)
            await self.update_dir(destination_remote, destination_path)

        input_dialog.accepted.connect(
            lambda: asyncio.ensure_future(create_folder()))

    async def rename_file(self, file_name: str):
        input_dialog = QInputDialog(self)
        input_dialog.setWindowTitle(self.tr("Rename"))
        input_dialog.setLabelText(self.tr("Enter new name:"))
        input_dialog.setTextValue(file_name)
        input_dialog.setModal(True)
        input_dialog.show()

        destination_remote = self.current_remote
        destination_path = self.remotes_paths[self.current_remote]

        async def rename():
            new_file_name = input_dialog.textValue().strip()
            if new_file_name.strip() != '':
                if destination_path != '':
                    new_file_path = f'{destination_remote}{destination_path}/{new_file_name.strip()}'
                    old_file_path = f'{destination_remote}{destination_path}/{file_name}'
                else:
                    new_file_path = f'{destination_remote}{destination_path}{new_file_name.strip()}'
                    old_file_path = f'{destination_remote}{destination_path}{file_name}'
                await rc.moveto(old_file_path, new_file_path)
                await self.update_dir(destination_remote, destination_path)

        input_dialog.accepted.connect(
            lambda: asyncio.ensure_future(rename()))

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

    def shortcuts(self):
        def delete():
            selected = self.ui.tree_files.selectedItems()
            selected_files = []
            for item in selected:
                selected_files.append(item.data(0, Qt.ItemDataRole.UserRole))
            if len(selected) > 0:
                asyncio.ensure_future(self.delete_files(selected_files))

        def delete_search():
            selected = self.ui.treeWidget_search.selectedItems()
            selected_files = []
            for item in selected:
                selected_files.append(item.data(0, Qt.ItemDataRole.UserRole))
            if len(selected) > 0:
                asyncio.ensure_future(self.delete_files(selected_files))

        self.delete_shortcut = QShortcut(
            QKeySequence("Del"), self.ui.tree_files)
        self.delete_shortcut.activated.connect(delete)

        self.delete_shortcut_search = QShortcut(
            QKeySequence("Del"), self.ui.treeWidget_search)
        self.delete_shortcut_search.activated.connect(delete_search)

        self.copy_shortcut = QShortcut(
            QKeySequence("Ctrl+C"), self.ui.tree_files)
        self.copy_shortcut.activated.connect(
            lambda: self.copy_files(self.ui.tree_files.selectedItems()))

        self.copy_shortcut = QShortcut(
            QKeySequence("Ctrl+C"), self.ui.treeWidget_search)
        self.copy_shortcut.activated.connect(
            lambda: self.copy_files(self.ui.treeWidget_search.selectedItems()))

        self.paste_shortcut = QShortcut(
            QKeySequence("Ctrl+V"), self.ui.tree_files)
        self.paste_shortcut.activated.connect(self.paste_file)

        def rename():
            selected = self.ui.tree_files.selectedItems()
            if len(selected) > 0:
                asyncio.ensure_future(self.rename_file(selected[0].text(0)))

        self.rename_shortcut = QShortcut(
            QKeySequence("F2"), self.ui.tree_files)
        self.rename_shortcut.activated.connect(rename)

        self.update_shortcut = QShortcut(
            QKeySequence("F5"), self.ui.tree_files)
        self.update_shortcut.activated.connect(lambda: asyncio.ensure_future(
            self.update_dir(self.current_remote, self.remotes_paths.setdefault(self.current_remote, ''))))

        self.new_folder_shortcut = QShortcut(
            QKeySequence("F7"), self.ui.tree_files)
        self.new_folder_shortcut.activated.connect(
            lambda: asyncio.ensure_future(self.new_folder()))

    def show_context_menu_tree(self, point):
        selected = self.ui.tree_files.selectedItems()
        selected_files = []
        for item in selected:
            selected_files.append(item.data(0, Qt.ItemDataRole.UserRole))

        menu = QMenu()

        if self.current_remote != '':
            if len(selected) < 1:
                action = QAction(self)
                action.setText(self.tr('Paste'))
                action.setIcon(QIcon.fromTheme('edit-paste'))
                action.triggered.connect(self.paste_file)
                action.setShortcut(QKeySequence('Ctrl+V'))
                menu.addAction(action)

                action = QAction(self)
                action.setText(self.tr('New Folder'))
                action.setIcon(QIcon.fromTheme('folder-new'))
                action.triggered.connect(
                    lambda: asyncio.ensure_future(self.new_folder()))
                action.setShortcut(QKeySequence('F7'))
                menu.addAction(action)
            else:
                item = self.ui.tree_files.itemAt(point)
                file_name = item.data(0, Qt.ItemDataRole.UserRole)['name']
                is_dir = item.data(0, Qt.ItemDataRole.UserRole)['is_dir']
                remote = item.data(0, Qt.ItemDataRole.UserRole)['remote']
                file_path = item.data(0, Qt.ItemDataRole.UserRole)['path']

                action = QAction(self)
                action.setText(self.tr('Open'))
                action.setIcon(item.icon(0))
                action.triggered.connect(
                    lambda: self.open_item(remote, file_path, file_name, is_dir))
                menu.addAction(action)

                if not is_dir and os.name == 'nt':
                    action = QAction(self)
                    action.setText(self.tr('Open With...'))
                    action.setIcon(QIcon.fromTheme('document-open'))
                    action.triggered.connect(
                        lambda: self.open_item(remote, file_path, file_name, is_dir, True))
                    menu.addAction(action)

                action = QAction(self)
                action.setText(self.tr('Download'))
                action.setIcon(QIcon.fromTheme('emblem-downloads'))
                action.triggered.connect(
                    lambda: self.download_file(selected_files))
                menu.addAction(action)

                menu.addSeparator()

                action = QAction(self)
                action.setText(self.tr('Copy'))
                action.setIcon(QIcon.fromTheme('edit-copy'))
                action.triggered.connect(lambda: self.copy_files(selected))
                action.setShortcut(QKeySequence('Ctrl+C'))
                menu.addAction(action)

                action = QAction(self)
                action.setText(self.tr('Paste'))
                action.setIcon(QIcon.fromTheme('edit-paste'))
                action.triggered.connect(self.paste_file)
                action.setShortcut(QKeySequence('Ctrl+V'))
                menu.addAction(action)

                menu.addSeparator()

                action = QAction(self)
                action.setText(self.tr('Rename'))
                action.setIcon(QIcon.fromTheme('format-text-italic'))
                action.triggered.connect(lambda: asyncio.ensure_future(
                    self.rename_file(file_name)))
                action.setShortcut(QKeySequence('F2'))
                menu.addAction(action)

                action = QAction(self)
                action.setText(self.tr('Delete'))
                action.setIcon(QIcon.fromTheme('edit-delete'))
                action.triggered.connect(
                    lambda: asyncio.ensure_future(self.delete_files(selected_files)))
                action.setShortcut(QKeySequence('Del'))
                menu.addAction(action)

                menu.addSeparator()

                action = QAction(self)
                action.setText(self.tr('New Folder'))
                action.setIcon(QIcon.fromTheme('folder-new'))
                action.triggered.connect(
                    lambda: asyncio.ensure_future(self.new_folder()))
                action.setShortcut(QKeySequence('F7'))
                menu.addAction(action)

        menu.exec(QCursor.pos())

    def show_context_menu_tree_search(self, point):
        selected = self.ui.treeWidget_search.selectedItems()
        selected_files = []
        for item in selected:
            selected_files.append(item.data(0, Qt.ItemDataRole.UserRole))

        if len(selected) == 0:
            return

        item = self.ui.treeWidget_search.itemAt(point)
        file_name = item.data(0, Qt.ItemDataRole.UserRole)['name']
        is_dir = item.data(0, Qt.ItemDataRole.UserRole)['is_dir']
        remote = item.data(0, Qt.ItemDataRole.UserRole)['remote']
        file_path = item.data(0, Qt.ItemDataRole.UserRole)['path']

        async def show():
            path = file_path[0:-len(file_name)]
            self.ui.tabWidget.setCurrentIndex(0)

            self.ui.tree_remotes.clearSelection()
            items = self.ui.tree_remotes.findItems(
                remote, Qt.MatchFlag.MatchContains)
            items[0].setSelected(True)

            await self.open_dir(remote, path)
            items = self.ui.tree_files.findItems(
                file_name, Qt.MatchFlag.MatchContains)
            items[0].setSelected(True)

        menu = QMenu()

        action = QAction(self)
        action.setText(self.tr('Open file location'))
        action.setIcon(QIcon.fromTheme('system-file-manager'))
        action.triggered.connect(lambda: asyncio.ensure_future(show()))
        menu.addAction(action)

        if not is_dir:
            menu.addSeparator()

            action = QAction(self)
            action.setText(self.tr('Open'))
            action.setIcon(item.icon(0))
            action.triggered.connect(
                lambda: self.open_item(remote, file_path, file_name, is_dir))
            menu.addAction(action)

        if not is_dir and os.name == 'nt':
            action = QAction(self)
            action.setText(self.tr('Open With...'))
            action.setIcon(QIcon.fromTheme('document-open'))
            action.triggered.connect(
                lambda: self.open_item(remote, file_path, file_name, is_dir, True))
            menu.addAction(action)

        menu.addSeparator()

        action = QAction(self)
        action.setText(self.tr('Download'))
        action.setIcon(QIcon.fromTheme('emblem-downloads'))
        action.triggered.connect(
            lambda: self.download_file(selected_files))
        menu.addAction(action)

        menu.addSeparator()

        action = QAction(self)
        action.setText(self.tr('Copy'))
        action.setIcon(QIcon.fromTheme('edit-copy'))
        action.triggered.connect(lambda: self.copy_files(selected))
        action.setShortcut(QKeySequence('Ctrl+C'))
        menu.addAction(action)

        action = QAction(self)
        action.setText(self.tr('Delete'))
        action.setIcon(QIcon.fromTheme('edit-delete'))
        action.triggered.connect(
            lambda: asyncio.ensure_future(self.delete_files(selected_files)))
        action.setShortcut(QKeySequence('Del'))
        menu.addAction(action)

        menu.exec(QCursor.pos())

    def show_context_menu_remote(self, point):
        index = self.ui.tree_remotes.indexAt(point)

        if not index.isValid():
            return

        item = self.ui.tree_remotes.itemAt(point)

        menu = QMenu()

        action = QAction(self)
        action.setText(self.tr('Open'))
        action.setIcon(QIcon.fromTheme('folder-open'))
        action.triggered.connect(lambda: self.open_remote(item))
        menu.addAction(action)

        action = QAction(self)
        action.setText(self.tr('Edit'))
        action.setIcon(QIcon.fromTheme('applications-development'))
        action.triggered.connect(lambda: self.edit_remote(item.text(0)))
        menu.addAction(action)

        action = QAction(self)
        action.setText(self.tr('Mount', 'verb'))
        action.setIcon(QIcon.fromTheme('drive-harddisk'))
        action.triggered.connect(
            lambda: self.mount_remote(item.text(0), item.text(1)))
        menu.addAction(action)

        action = QAction(self)
        action.setText(self.tr('Delete'))
        action.setIcon(QIcon.fromTheme('edit-delete'))
        action.triggered.connect(lambda: self.delete_remote(item.text(0)))
        menu.addAction(action)

        menu.exec(QCursor.pos())

    def show_context_menu_serve(self, point):
        index = self.ui.treeWidget_serve.indexAt(point)
        menu = QMenu()

        def stop_serve(index: int):
            self.serve[index].process.send_signal(signal.CTRL_BREAK_EVENT)
            self.ui.treeWidget_serve.takeTopLevelItem(index)
            del self.serve[index]

        if index.isValid():
            action = QAction(self)
            action.setText(self.tr('Stop'))
            action.triggered.connect(lambda: stop_serve(index.row()))
            menu.addAction(action)

        menu.exec(QCursor.pos())

    def show_context_menu_task(self, point):
        index = self.ui.tasks.indexAt(point)
        menu = QMenu()

        def clear_tasks():
            for i in range(len(self.tasks)):
                if self.tasks[i].status == 'Done':
                    self.ui.tasks.topLevelItem(i).setHidden(True)

        def stop_task(index: int):
            self.tasks[index].process.send_signal(signal.CTRL_BREAK_EVENT)
            self.ui.tasks.takeTopLevelItem(index)
            del self.tasks[index]

        if not index.isValid():
            action = QAction(self)
            action.setText(self.tr('Clear Completed'))
            action.setIcon(QIcon.fromTheme('edit-clear'))
            action.triggered.connect(clear_tasks)
            menu.addAction(action)
        else:
            item = self.ui.tasks.itemAt(point)

            if item.text(0) in ['Download', 'Upload', 'Opening']:
                action = QAction(self)
                action.setText(self.tr('Open Folder'))
                action.setIcon(QIcon.fromTheme('folder-open'))
                action.triggered.connect(lambda: self.open_task_dir(item))
                menu.addAction(action)

            if item.text(3) == 'Done':
                action = QAction(self)
                action.setText(self.tr('Clear Task'))
                action.setIcon(QIcon.fromTheme('edit-clear'))
                action.triggered.connect(
                    lambda: self.ui.tasks.topLevelItem(index.row()).setHidden(True))
                menu.addAction(action)

            if item.text(0) in ['Mount', 'Serve']:
                action = QAction(self)
                action.setText(self.tr('Stop'))
                action.triggered.connect(lambda: stop_task(index.row()))
                menu.addAction(action)

            action = QAction(self)
            action.setText(self.tr('Clear Completed'))
            action.setIcon(QIcon.fromTheme('edit-clear'))
            action.triggered.connect(clear_tasks)
            menu.addAction(action)

        menu.exec(QCursor.pos())

    def context_menu_tray_icon(self):
        menu = QMenu()

        def open():
            self.show()
            self.activateWindow()

        def close():
            self.hide()
            self.close()

        action = QAction(self)
        action.setText(self.tr('Open'))
        action.setIcon(self.windowIcon())
        action.triggered.connect(open)
        menu.addAction(action)

        menu.addSeparator()
        menu.addAction(self.ui.action_new_remote)
        menu.addAction(self.ui.action_new_serve)
        menu.addSeparator()
        menu.addAction(self.ui.action_settings)
        menu.addSeparator()

        action = QAction(self)
        action.setText(self.tr('Exit'))
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
            window.showNormal()
            window.activateWindow()
            client.disconnectFromServer()

    server.newConnection.connect(on_new_connection)


if __name__ == '__main__':
    app = QApplication()
    app.setQuitOnLastWindowClosed(False)
    settings = QSettings('Denis Mazur', 'Cloud Explorer')
    app.setStyle(settings.value('style', ''))
    app.setPalette(palettes[settings.value('palette', 'System')])

    qt_translator = QTranslator()
    translator = QTranslator()

    qt_translator.load(f'qtbase_{QLocale.system().name()}.qm', QLibraryInfo.path(
        QLibraryInfo.LibraryPath.TranslationsPath))
    app.installTranslator(qt_translator)

    if translator.load(f'{os.path.dirname(__file__) + os.sep}translations{os.sep}{QLocale.system().language().name}.qm'):
        app.installTranslator(translator)

    server_name = 'Cloud Explorer'
    server = QLocalServer()

    if is_already_running(server_name):
        print('The application has already been launched')
        sys.exit(0)

    window = MainWindow()
    window.show()

    start_server(window, server_name)

    sys.exit(QtAsyncio.run())
