import os

from PySide6.QtCore import QModelIndex, QRegularExpression
from PySide6.QtGui import QIcon, QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QCheckBox, QDialog, QLineEdit, QMessageBox, QWidget
from rclone_python import rclone, remote_types
from app.main_window import QLabel
from app.rclone import Rclone
from app.views import new_remote_window


class NewRemoteWindow(QDialog):
    def __init__(self, edit_mode: bool = False, remote_name: str = None):
        super(NewRemoteWindow, self).__init__()
        self.ui = new_remote_window.Ui_NewRemoteWindow()
        self.ui.setupUi(self)

        rc = Rclone()

        self.setWindowIcon(
            QIcon(os.path.dirname(__file__) + '/resources/' + 'favicon.ico'))
        self.ui.tabWidget.tabBar().hide()

        self.ui.buttonBox.accepted.connect(
            lambda: self.new_remote(edit_mode, remote_name))
        self.ui.checkBox_ftp_tls.clicked.connect(self.set_view_ftp_tls_option)

        self.ui.listWidget_remotes.currentRowChanged.connect(
            self.ui.tabWidget.setCurrentIndex)
        self.ui.listWidget_advance.currentRowChanged.connect(self.advance_row_change)

        reg_exp = QRegularExpression('[a-zA-ZА-Яа-яЁё0-9_\\.\\-\\+@\\* ]*$')
        validator = QRegularExpressionValidator(reg_exp)
        self.ui.lineEdit_name.setValidator(validator)

        self.providers = rc.providers()

        for provider in self.providers:
            self.ui.listWidget_advance.addItem(provider['Description'])

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
            self.ui.listWidget_remotes.hide()

    def set_view_ftp_tls_option(self, value):
        self.ui.radioButton_ftp_false.setEnabled(value)
        self.ui.radioButton_ftp_true.setEnabled(value)

    def advance_row_change(self, index: int):
        provider: dict[str, dict] = self.providers[index]
        print(provider)

        for i in range(self.ui.scrollAreaWidgetContents_advance.layout().count()):
            self.ui.scrollAreaWidgetContents_advance.layout().itemAt(i).widget().deleteLater()

        for option in provider['Options']:
            label_help = QLabel(option['Help'])
            label_help.setEnabled(False)

            if option['Type'] != 'bool':
                self.ui.scrollAreaWidgetContents_advance.layout().addWidget(QLabel(option['Name']))
                self.ui.scrollAreaWidgetContents_advance.layout().addWidget(label_help)

            match option['Type']:
                case 'string':
                    line_edit = QLineEdit(option['Default'])
                    if option['IsPassword']:
                        line_edit.setEchoMode(QLineEdit.EchoMode.Password)
                    self.ui.scrollAreaWidgetContents_advance.layout().addWidget(line_edit)
                case 'int':
                    line_edit = QLineEdit(str(option['Default']))
                    line_edit.setValidator(QIntValidator())
                    self.ui.scrollAreaWidgetContents_advance.layout().addWidget(line_edit)
                case 'bool':
                    checkbox = QCheckBox()
                    checkbox.setText(option['Name'])
                    checkbox.setChecked(option['Default'])
                    self.ui.scrollAreaWidgetContents_advance.layout().addWidget(checkbox)
                    self.ui.scrollAreaWidgetContents_advance.layout().addWidget(label_help)

    def new_remote(self, edit_mode: bool = False, remote_name: str = None):
        name = self.ui.lineEdit_name.text().strip()
        rc = Rclone()

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
                    config_type = ['onedrive', 'sharepoint', 'url', 'search', 'driveid',
                                   'siteid', 'path'][self.ui.comboBox_onedrive_type.currentIndex()]
                    rclone.create_remote(
                        name, remote_type=remote_types.RemoteTypes.onedrive, region=region, config_type=config_type)
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
