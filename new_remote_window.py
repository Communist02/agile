# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_remote_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QRadioButton, QSizePolicy, QSpacerItem,
    QTabWidget, QVBoxLayout, QWidget)

class Ui_NewRemoteWindow(object):
    def setupUi(self, NewRemoteWindow):
        if not NewRemoteWindow.objectName():
            NewRemoteWindow.setObjectName(u"NewRemoteWindow")
        NewRemoteWindow.resize(640, 480)
        self.verticalLayout = QVBoxLayout(NewRemoteWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.lineEdit_name = QLineEdit(NewRemoteWindow)
        self.lineEdit_name.setObjectName(u"lineEdit_name")

        self.verticalLayout.addWidget(self.lineEdit_name)

        self.tabWidget = QTabWidget(NewRemoteWindow)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_google = QWidget()
        self.tab_google.setObjectName(u"tab_google")
        self.tabWidget.addTab(self.tab_google, "")
        self.tab_yandex = QWidget()
        self.tab_yandex.setObjectName(u"tab_yandex")
        self.tabWidget.addTab(self.tab_yandex, "")
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

        self.lineEdit_host = QLineEdit(self.tab_ftp)
        self.lineEdit_host.setObjectName(u"lineEdit_host")

        self.verticalLayout_4.addWidget(self.lineEdit_host)


        self.horizontalLayout_2.addLayout(self.verticalLayout_4)

        self.verticalLayout_5 = QVBoxLayout()
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.label_port = QLabel(self.tab_ftp)
        self.label_port.setObjectName(u"label_port")

        self.verticalLayout_5.addWidget(self.label_port)

        self.lineEdit_port = QLineEdit(self.tab_ftp)
        self.lineEdit_port.setObjectName(u"lineEdit_port")

        self.verticalLayout_5.addWidget(self.lineEdit_port)


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

        self.lineEdit_login = QLineEdit(self.tab_ftp)
        self.lineEdit_login.setObjectName(u"lineEdit_login")

        self.verticalLayout_6.addWidget(self.lineEdit_login)


        self.horizontalLayout_4.addLayout(self.verticalLayout_6)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.label_5 = QLabel(self.tab_ftp)
        self.label_5.setObjectName(u"label_5")

        self.verticalLayout_7.addWidget(self.label_5)

        self.lineEdit_password = QLineEdit(self.tab_ftp)
        self.lineEdit_password.setObjectName(u"lineEdit_password")

        self.verticalLayout_7.addWidget(self.lineEdit_password)


        self.horizontalLayout_4.addLayout(self.verticalLayout_7)


        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.groupBox = QGroupBox(self.tab_ftp)
        self.groupBox.setObjectName(u"groupBox")
        self.horizontalLayout_7 = QHBoxLayout(self.groupBox)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.checkBox = QCheckBox(self.groupBox)
        self.checkBox.setObjectName(u"checkBox")

        self.horizontalLayout_7.addWidget(self.checkBox)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer)

        self.radioButton_2 = QRadioButton(self.groupBox)
        self.radioButton_2.setObjectName(u"radioButton_2")

        self.horizontalLayout_7.addWidget(self.radioButton_2)

        self.radioButton = QRadioButton(self.groupBox)
        self.radioButton.setObjectName(u"radioButton")

        self.horizontalLayout_7.addWidget(self.radioButton)


        self.verticalLayout_3.addWidget(self.groupBox)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_2)

        self.tabWidget.addTab(self.tab_ftp, "")
        self.tab_webdaw = QWidget()
        self.tab_webdaw.setObjectName(u"tab_webdaw")
        self.tabWidget.addTab(self.tab_webdaw, "")
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

        self.verticalLayout.addWidget(self.tabWidget)

        self.buttonBox = QDialogButtonBox(NewRemoteWindow)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(NewRemoteWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(NewRemoteWindow)
    # setupUi

    def retranslateUi(self, NewRemoteWindow):
        NewRemoteWindow.setWindowTitle(QCoreApplication.translate("NewRemoteWindow", u"New remote", None))
        self.lineEdit_name.setText("")
        self.lineEdit_name.setPlaceholderText(QCoreApplication.translate("NewRemoteWindow", u"New remote name", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_google), QCoreApplication.translate("NewRemoteWindow", u"Google Drive", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_yandex), QCoreApplication.translate("NewRemoteWindow", u"Yandex Drive", None))
        self.label_2.setText(QCoreApplication.translate("NewRemoteWindow", u"Host", None))
        self.label_port.setText(QCoreApplication.translate("NewRemoteWindow", u"Port", None))
        self.label_4.setText(QCoreApplication.translate("NewRemoteWindow", u"Login", None))
        self.label_5.setText(QCoreApplication.translate("NewRemoteWindow", u"Password", None))
        self.groupBox.setTitle(QCoreApplication.translate("NewRemoteWindow", u"FTPS", None))
        self.checkBox.setText(QCoreApplication.translate("NewRemoteWindow", u"TLS", None))
        self.radioButton_2.setText(QCoreApplication.translate("NewRemoteWindow", u"Explict", None))
        self.radioButton.setText(QCoreApplication.translate("NewRemoteWindow", u"Implict", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_ftp), QCoreApplication.translate("NewRemoteWindow", u"FTP", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_webdaw), QCoreApplication.translate("NewRemoteWindow", u"WebDAV", None))
        self.label.setText(QCoreApplication.translate("NewRemoteWindow", u"URL", None))
        self.lineEdit_url.setText(QCoreApplication.translate("NewRemoteWindow", u"http://127.0.0.1:8000/", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_http), QCoreApplication.translate("NewRemoteWindow", u"http", None))
    # retranslateUi

