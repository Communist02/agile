import os

from PySide6.QtCore import QRegularExpression, Qt
from PySide6.QtGui import QIcon, QIntValidator, QRegularExpressionValidator
from PySide6.QtWidgets import QCheckBox, QComboBox, QDialog, QLineEdit, QListWidgetItem, QMessageBox, QWidget
from app.main_window import QLabel
from app.rclone import Rclone
from app.views import new_remote_window


class NewRemoteWindow(QDialog):
    def __init__(self, edit_mode: bool = False, remote_name: str = None):
        super(NewRemoteWindow, self).__init__()
        self.ui = new_remote_window.Ui_NewRemoteWindow()
        self.ui.setupUi(self)

        rc = Rclone()
        self.providers = rc.providers()
        self.remote = {}
        self.edit_mode = edit_mode

        self.setWindowIcon(
            QIcon(os.path.dirname(__file__) + '/resources/' + 'favicon.ico'))
        self.ui.tabWidget.tabBar().hide()

        self.ui.buttonBox.accepted.connect(
            lambda: self.new_remote(remote_name))
        self.ui.checkBox_ftp_tls.clicked.connect(self.set_view_ftp_tls_option)

        self.ui.listWidget_remotes.currentRowChanged.connect(
            self.ui.tabWidget.setCurrentIndex)
        self.ui.listWidget_advance.currentRowChanged.connect(
            self.advance_row_change)

        reg_exp = QRegularExpression('[a-zA-ZА-Яа-яЁё0-9_\\.\\-\\+@\\* ]*$')
        validator = QRegularExpressionValidator(reg_exp)
        self.ui.lineEdit_name.setValidator(validator)

        if edit_mode:
            self.setWindowTitle(self.tr('Edit') + ' ' + remote_name[:-1])
            config = rc.config('dump')
            remote_type = config[remote_name[:-1]]['type']
            self.ui.lineEdit_name.setText(remote_name[:-1])
            self.ui.tabWidget_mode.tabBar().hide()
            self.ui.tabWidget_mode.setCurrentIndex(1)
            self.ui.listWidget_advance.hide()

        for provider in self.providers:
            item = QListWidgetItem(f'{provider['Description']}')
            item.setToolTip(provider['Name'])
            self.ui.listWidget_advance.addItem(item)
            if edit_mode and remote_type == provider['Name']:
                self.remote = config[remote_name[:-1]]
                self.ui.listWidget_advance.setCurrentRow(
                    self.ui.listWidget_advance.count() - 1)
                break

        if not edit_mode:
            self.ui.listWidget_advance.setCurrentRow(0)

    def set_view_ftp_tls_option(self, value):
        self.ui.radioButton_ftp_false.setEnabled(value)
        self.ui.radioButton_ftp_true.setEnabled(value)

    def advance_row_change(self, index: int):
        provider: dict[str, dict] = self.providers[index]

        if not self.edit_mode:
            self.remote = {'type': provider['Name']}

        is_required_show = False
        is_not_required_show = False
        is_advanced_show = False

        for i in range(self.ui.groupBox_advanced.layout().count()):
            self.ui.groupBox_advanced.layout().itemAt(i).widget().deleteLater()
        for i in range(self.ui.groupBox_required.layout().count()):
            self.ui.groupBox_required.layout().itemAt(i).widget().deleteLater()
        for i in range(self.ui.groupBox_not_required.layout().count()):
            self.ui.groupBox_not_required.layout().itemAt(i).widget().deleteLater()

        def toggle_content(value):
            for child in self.ui.groupBox_advanced.findChildren(QWidget):
                child.setVisible(value)
                if value:
                    self.ui.groupBox_advanced.setFocus()

        self.ui.groupBox_advanced.toggled.connect(toggle_content)

        for option in provider['Options']:
            label_help = QLabel(option['Help'])
            label_help.setEnabled(False)

            if option['Advanced']:
                is_advanced_show = True
                layout = self.ui.groupBox_advanced.layout()
            elif option['Required']:
                is_required_show = True
                layout = self.ui.groupBox_required.layout()
                if not self.edit_mode:
                    self.remote[option['Name']] = option['Default']
            else:
                is_not_required_show = True
                layout = self.ui.groupBox_not_required.layout()

            if option['Type'] != 'bool':
                layout.addWidget(QLabel(option['Name']))
                layout.addWidget(label_help)

            match option['Type']:
                case 'string':
                    if not option.get('Examples', False):
                        widget = QLineEdit(option['Default'])
                        if option['IsPassword']:
                            widget .setEchoMode(QLineEdit.EchoMode.Password)
                        widget.textChanged.connect(
                            lambda text, name=option['Name']: self.remote.__setitem__(name, text))
                        if self.edit_mode and self.remote.get(option['Name'], False):
                            widget.setText(self.remote[option['Name']])
                    else:
                        widget = QComboBox(editable=True)
                        for example in option['Examples']:
                            widget.addItem(example['Value'])
                            widget.setItemData(
                                widget.count() - 1, example['Help'], Qt.ItemDataRole.ToolTipRole)
                        widget.editTextChanged.connect(
                            lambda text, name=option['Name']: self.remote.__setitem__(name, text))
                        if self.edit_mode and self.remote.get(option['Name'], False):
                            widget.setCurrentText(self.remote[option['Name']])
                        else:
                            widget.setCurrentText(option['Default'])
                    layout.addWidget(widget)
                case 'int':
                    line_edit = QLineEdit(str(option['Default']))
                    line_edit.setValidator(QIntValidator())
                    layout.addWidget(line_edit)
                    line_edit.textChanged.connect(
                        lambda text, name=option['Name']: self.remote.__setitem__(name, text))
                    if self.edit_mode and self.remote.get(option['Name'], False):
                        line_edit.setText(str(self.remote[option['Name']]))
                case 'bool':
                    checkbox = QCheckBox()
                    checkbox.setText(option['Name'])
                    layout.addWidget(checkbox)
                    layout.addWidget(label_help)
                    checkbox.toggled.connect(
                        lambda value, name=option['Name']: self.remote.__setitem__(name, value))
                    if self.edit_mode and self.remote.get(option['Name'], False):
                        checkbox.setChecked(bool(self.remote[option['Name']]))
                    else:
                        checkbox.setChecked(option['Default'])

        self.ui.groupBox_required.setVisible(is_required_show)
        self.ui.groupBox_not_required.setVisible(is_not_required_show)
        self.ui.groupBox_advanced.setVisible(is_advanced_show)
        if not self.ui.groupBox_advanced.isChecked():
            toggle_content(False)

    def new_remote(self, remote_name_delete: str = None):
        name = self.ui.lineEdit_name.text().strip()
        rc = Rclone()

        if name != '':
            if remote_name_delete:
                rc.config('delete', f'"{remote_name_delete[:-1]}"')
            if self.ui.tabWidget_mode.currentIndex() == 0:
                match self.ui.tabWidget.currentWidget().objectName():
                    case 'tab_google_drive':
                        rc.create_remote(
                            name, remote_type='drive')
                        self.close()
                    case 'tab_yandex_disk':
                        rc.create_remote(
                            name, remote_type='yandex')
                        self.close()
                    case 'tab_ftp':
                        if self.ui.checkBox_ftp_tls.isChecked():
                            explicit_tls = str(
                                self.ui.radioButton_ftp_true.isChecked()).lower()
                        else:
                            explicit_tls = 'false'
                        rc.create_remote(name,
                                         remote_type='ftp',
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
                        rc.create_remote(name,
                                         remote_type='webdav',
                                         url=self.ui.lineEdit_webdav_url.text().strip(),
                                         user=self.ui.lineEdit_webdav_login.text().strip(),
                                         vendor=vendor
                                         )
                        if self.ui.lineEdit_webdav_password.text().strip() != '':
                            rc.config('password', name, 'pass',
                                      self.ui.lineEdit_webdav_password.text().strip())
                        self.close()
                    case 'tab_http':
                        rc.create_remote(
                            name, remote_type='http', url=self.ui.lineEdit_url.text().strip())
                        self.close()
                    case 'tab_local':
                        rc.create_remote(
                            name, remote_type='local')
                        self.close()
                    case 'tab_onedrive':
                        region = [
                            'global', 'us', 'cn'][self.ui.comboBox_onedrive_region.currentIndex()]
                        config_type = ['onedrive', 'sharepoint', 'url', 'search', 'driveid',
                                       'siteid', 'path'][self.ui.comboBox_onedrive_type.currentIndex()]
                        rc.create_remote(
                            name, remote_type='onedrive', region=region, config_type=config_type)
                        self.close()
                    case 'tab_mailru':
                        rc.create_remote(name, remote_type='mailru',
                                         user=self.ui.lineEdit_mailru_login.text().strip())
                        if self.ui.lineEdit_mailru_password.text().strip() != '':
                            rc.config('password', name, 'pass',
                                      self.ui.lineEdit_mailru_password.text().strip())
                        self.close()
                    case 'tab_sftp':
                        rc.create_remote(name,
                                         remote_type='sftp',
                                         host=self.ui.lineEdit_sftp_host.text().strip(),
                                         port=self.ui.lineEdit_sftp_port.text().strip(),
                                         user=self.ui.lineEdit_sftp_login.text().strip()
                                         )
                        if self.ui.lineEdit_sftp_password.text().strip() != '':
                            rc.config('password', name, 'pass',
                                      self.ui.lineEdit_sftp_password.text().strip())
                        self.close()
                    case 'tab_alias':
                        rc.create_remote(
                            name, remote_type='alias', remote=self.ui.lineEdit_alias_path.text().strip())
                        self.close()
                    case 'tab_union':
                        self.close()
            else:
                arg = ''
                for key, value in self.remote.items():
                    if key != 'type':
                        match value:
                            case str():
                                arg += f'{key}="{value}" '
                            case int():
                                arg += f'{key}={value} '
                            case bool():
                                arg += f'{key}={str(value).lower()} '
                rc.create_remote(name, self.remote['type'], arg)
                self.close()
        else:
            QMessageBox.warning(self, self.tr('Enter name'),
                                self.tr('Enter name for new remote') + '!')
