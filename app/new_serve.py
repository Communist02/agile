import os
import subprocess
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

import app.main_window as main_window
from app.rclone import Rclone
from app.views import new_serve_window


class NewServeWindow(QDialog):
    def __init__(self, parent=None):
        super(NewServeWindow, self).__init__()
        self.ui = new_serve_window.Ui_NewServeWindow()
        self.ui.setupUi(self)

        self.parent = parent

        self.setWindowIcon(
            QIcon(os.path.dirname(__file__) + '/resources/' + 'favicon.ico'))

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

        rc = Rclone()
        process: subprocess.Popen = rc.serve(
            protocol, path, user, password, address, read_only, args)
        try:
            process.wait(1)
            QMessageBox.critical(self, self.tr('Error'),
                                 self.tr('Check the data!'))
        except subprocess.TimeoutExpired:
            self.parent.serve.append(main_window.Serve(
                protocol, path, address, user, password, read_only=read_only, process=process))
            self.close()
