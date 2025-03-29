# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_remote_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QComboBox,
    QDialog, QDialogButtonBox, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QRadioButton, QSizePolicy,
    QSpacerItem, QTabWidget, QVBoxLayout, QWidget)

class Ui_NewRemoteWindow(object):
    def setupUi(self, NewRemoteWindow):
        if not NewRemoteWindow.objectName():
            NewRemoteWindow.setObjectName(u"NewRemoteWindow")
        NewRemoteWindow.resize(640, 480)
        icon = QIcon(QIcon.fromTheme(u"weather-overcast"))
        NewRemoteWindow.setWindowIcon(icon)
        self.verticalLayout = QVBoxLayout(NewRemoteWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lineEdit_name = QLineEdit(NewRemoteWindow)
        self.lineEdit_name.setObjectName(u"lineEdit_name")

        self.verticalLayout.addWidget(self.lineEdit_name)

        self.tabWidget = QTabWidget(NewRemoteWindow)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_google_drive = QWidget()
        self.tab_google_drive.setObjectName(u"tab_google_drive")
        self.verticalLayout_9 = QVBoxLayout(self.tab_google_drive)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_3 = QLabel(self.tab_google_drive)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout_9.addWidget(self.label_3)

        self.verticalSpacer_3 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_3)

        self.tabWidget.addTab(self.tab_google_drive, "")
        self.tab_yandex_disk = QWidget()
        self.tab_yandex_disk.setObjectName(u"tab_yandex_disk")
        self.verticalLayout_8 = QVBoxLayout(self.tab_yandex_disk)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.label_6 = QLabel(self.tab_yandex_disk)
        self.label_6.setObjectName(u"label_6")

        self.verticalLayout_8.addWidget(self.label_6)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_4)

        self.tabWidget.addTab(self.tab_yandex_disk, "")
        self.tab_ftp = QWidget()
        self.tab_ftp.setObjectName(u"tab_ftp")
        self.verticalLayout_3 = QVBoxLayout(self.tab_ftp)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_2 = QLabel(self.tab_ftp)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_4.addWidget(self.label_2)

        self.lineEdit_ftp_host = QLineEdit(self.tab_ftp)
        self.lineEdit_ftp_host.setObjectName(u"lineEdit_ftp_host")

        self.verticalLayout_4.addWidget(self.lineEdit_ftp_host)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_port = QLabel(self.tab_ftp)
        self.label_port.setObjectName(u"label_port")

        self.verticalLayout_5.addWidget(self.label_port)

        self.lineEdit_ftp_port = QLineEdit(self.tab_ftp)
        self.lineEdit_ftp_port.setObjectName(u"lineEdit_ftp_port")

        self.verticalLayout_5.addWidget(self.lineEdit_ftp_port)


        self.horizontalLayout_2.addLayout(self.verticalLayout_5)


        self.verticalLayout_3.addLayout(self.horizontalLayout_2)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")

        self.verticalLayout_3.addLayout(self.horizontalLayout_3)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.label_4 = QLabel(self.tab_ftp)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_6.addWidget(self.label_4)

        self.lineEdit_ftp_login = QLineEdit(self.tab_ftp)
        self.lineEdit_ftp_login.setObjectName(u"lineEdit_ftp_login")

        self.verticalLayout_6.addWidget(self.lineEdit_ftp_login)


        self.horizontalLayout_4.addLayout(self.verticalLayout_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_5 = QLabel(self.tab_ftp)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_7.addWidget(self.label_5)

        self.lineEdit_ftp_password = QLineEdit(self.tab_ftp)
        self.lineEdit_ftp_password.setObjectName(u"lineEdit_ftp_password")

        self.verticalLayout_7.addWidget(self.lineEdit_ftp_password)


        self.horizontalLayout_4.addLayout(self.verticalLayout_7)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.groupBox = QGroupBox(self.tab_ftp)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.checkBox_ftp_tls = QCheckBox(self.groupBox)
        self.checkBox_ftp_tls.setObjectName(u"checkBox_ftp_tls")

        self.horizontalLayout_7.addWidget(self.checkBox_ftp_tls)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer)

        self.radioButton_ftp_false = QRadioButton(self.groupBox)
        self.radioButton_ftp_false.setObjectName(u"radioButton_ftp_false")
        self.radioButton_ftp_false.setEnabled(False)
        self.radioButton_ftp_false.setChecked(True)

        self.horizontalLayout_7.addWidget(self.radioButton_ftp_false)

        self.radioButton_ftp_true = QRadioButton(self.groupBox)
        self.radioButton_ftp_true.setObjectName(u"radioButton_ftp_true")
        self.radioButton_ftp_true.setEnabled(False)

        self.horizontalLayout_7.addWidget(self.radioButton_ftp_true)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tab_ftp, "")
        self.tab_webdav = QWidget()
        self.tab_webdav.setObjectName(u"tab_webdav")
        self.verticalLayout_10 = QVBoxLayout(self.tab_webdav)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.label_7 = QLabel(self.tab_webdav)
        self.label_7.setObjectName(u"label_7")

        self.verticalLayout_10.addWidget(self.label_7)

        self.lineEdit_webdav_url = QLineEdit(self.tab_webdav)
        self.lineEdit_webdav_url.setObjectName(u"lineEdit_webdav_url")

        self.verticalLayout_10.addWidget(self.lineEdit_webdav_url)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_11 = QVBoxLayout()
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.label_8 = QLabel(self.tab_webdav)
        self.label_8.setObjectName(u"label_8")

        self.verticalLayout_11.addWidget(self.label_8)

        self.lineEdit_webdav_login = QLineEdit(self.tab_webdav)
        self.lineEdit_webdav_login.setObjectName(u"lineEdit_webdav_login")

        self.verticalLayout_11.addWidget(self.lineEdit_webdav_login)


        self.horizontalLayout.addLayout(self.verticalLayout_11)

        self.verticalLayout_13 = QVBoxLayout()
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.label_9 = QLabel(self.tab_webdav)
        self.label_9.setObjectName(u"label_9")

        self.verticalLayout_13.addWidget(self.label_9)

        self.lineEdit_webdav_password = QLineEdit(self.tab_webdav)
        self.lineEdit_webdav_password.setObjectName(u"lineEdit_webdav_password")

        self.verticalLayout_13.addWidget(self.lineEdit_webdav_password)


        self.horizontalLayout.addLayout(self.verticalLayout_13)


        self.verticalLayout_10.addLayout(self.horizontalLayout)

        self.label_10 = QLabel(self.tab_webdav)
        self.label_10.setObjectName(u"label_10")

        self.verticalLayout_10.addWidget(self.label_10)

        self.comboBox_webdav_vendor = QComboBox(self.tab_webdav)
        self.comboBox_webdav_vendor.addItem("")
        self.comboBox_webdav_vendor.addItem("")
        self.comboBox_webdav_vendor.addItem("")
        self.comboBox_webdav_vendor.addItem("")
        self.comboBox_webdav_vendor.addItem("")
        self.comboBox_webdav_vendor.addItem("")
        self.comboBox_webdav_vendor.addItem("")
        self.comboBox_webdav_vendor.setObjectName(u"comboBox_webdav_vendor")

        self.verticalLayout_10.addWidget(self.comboBox_webdav_vendor)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_5)

        self.tabWidget.addTab(self.tab_webdav, "")
        self.tab_http = QWidget()
        self.tab_http.setObjectName(u"tab_http")
        self.verticalLayout_2 = QVBoxLayout(self.tab_http)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.tab_http)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.lineEdit_url = QLineEdit(self.tab_http)
        self.lineEdit_url.setObjectName(u"lineEdit_url")

        self.verticalLayout_2.addWidget(self.lineEdit_url)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.tabWidget.addTab(self.tab_http, "")
        self.tab_local = QWidget()
        self.tab_local.setObjectName(u"tab_local")
        self.tabWidget.addTab(self.tab_local, "")

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(NewRemoteWindow)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(NewRemoteWindow)

        self.tabWidget.setCurrentIndex(2)


        QMetaObject.connectSlotsByName(NewRemoteWindow)
    # setupUi

    def retranslateUi(self, NewRemoteWindow):
        NewRemoteWindow.setWindowTitle(QCoreApplication.translate("NewRemoteWindow", u"New remote", None))
        self.lineEdit_name.setText("")
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("NewRemoteWindow", u"Enter name for new remote", None))
        self.label_3.setText(QCoreApplication.translate("NewRemoteWindow", u"The browser will open", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_google_drive), QCoreApplication.translate("NewRemoteWindow", u"Google Drive", None))
        self.label_6.setText(QCoreApplication.translate("NewRemoteWindow", u"The browser will open", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_yandex_disk), QCoreApplication.translate("NewRemoteWindow", u"Yandex Disk", None))
        self.label_2.setText(QCoreApplication.translate("NewRemoteWindow", u"Host", None))
        self.label_port.setText(QCoreApplication.translate("NewRemoteWindow", u"Port", None))
        self.label_4.setText(QCoreApplication.translate("NewRemoteWindow", u"Login", None))
        self.label_5.setText(QCoreApplication.translate("NewRemoteWindow", u"Password", None))
        self.groupBox.setTitle(QCoreApplication.translate("NewRemoteWindow", u"FTPS", None))
        self.checkBox_ftp_tls.setText(QCoreApplication.translate("NewRemoteWindow", u"TLS", None))
        self.radioButton_ftp_false.setText(QCoreApplication.translate("NewRemoteWindow", u"Implict", None))
        self.radioButton_ftp_true.setText(QCoreApplication.translate("NewRemoteWindow", u"Explict", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ftp), QCoreApplication.translate("NewRemoteWindow", u"FTP", None))
        self.label_7.setText(QCoreApplication.translate("NewRemoteWindow", u"URL", None))
        self.label_8.setText(QCoreApplication.translate("NewRemoteWindow", u"Login", None))
        self.label_9.setText(QCoreApplication.translate("NewRemoteWindow", u"Password", None))
        self.label_10.setText(QCoreApplication.translate("NewRemoteWindow", u"Option vendor", None))
        self.comboBox_webdav_vendor.setItemText(0, QCoreApplication.translate("NewRemoteWindow", u"Other site/service or software", None))
        self.comboBox_webdav_vendor.setItemText(1, QCoreApplication.translate("NewRemoteWindow", u"Fastmail Files", None))
        self.comboBox_webdav_vendor.setItemText(2, QCoreApplication.translate("NewRemoteWindow", u"Nextcloud", None))
        self.comboBox_webdav_vendor.setItemText(3, QCoreApplication.translate("NewRemoteWindow", u"Owncloud", None))
        self.comboBox_webdav_vendor.setItemText(4, QCoreApplication.translate("NewRemoteWindow", u"Sharepoint Online, authenticated by Microsoft account", None))
        self.comboBox_webdav_vendor.setItemText(5, QCoreApplication.translate("NewRemoteWindow", u"Sharepoint with NTLM authentication, usually self-hosted or on-premises", None))
        self.comboBox_webdav_vendor.setItemText(6, QCoreApplication.translate("NewRemoteWindow", u"rclone WebDAV server to serve a remote over HTTP via the WebDAV protocol", None))

        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_webdav), QCoreApplication.translate("NewRemoteWindow", u"WebDAV", None))
        self.label.setText(QCoreApplication.translate("NewRemoteWindow", u"URL", None))
        self.lineEdit_url.setText(QCoreApplication.translate("NewRemoteWindow", u"http://127.0.0.1:8000/", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_http), QCoreApplication.translate("NewRemoteWindow", u"HTTP", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_local), QCoreApplication.translate("NewRemoteWindow", u"Local", None))
    # retranslateUi

