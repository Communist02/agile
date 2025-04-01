# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'new_serve_window.ui'
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
from PySide6.QtWidgets import (QAbstractButton, QApplication, QCheckBox, QDialog,
    QDialogButtonBox, QGroupBox, QHBoxLayout, QLabel,
    QLineEdit, QRadioButton, QSizePolicy, QSpacerItem,
    QVBoxLayout, QWidget)

class Ui_NewServeWindow(object):
    def setupUi(self, NewServeWindow):
        if not NewServeWindow.objectName():
            NewServeWindow.setObjectName(u"NewServeWindow")
        NewServeWindow.resize(640, 480)
        icon = QIcon(QIcon.fromTheme(u"applications-internet"))
        NewServeWindow.setWindowIcon(icon)
        NewServeWindow.setModal(True)
        self.verticalLayout = QVBoxLayout(NewServeWindow)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(NewServeWindow)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.horizontalLayout_2 = QHBoxLayout(self.groupBox_2)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.radioButton_ftp = QRadioButton(self.groupBox_2)
        self.radioButton_ftp.setObjectName(u"radioButton_ftp")
        self.radioButton_ftp.setChecked(True)

        self.horizontalLayout_2.addWidget(self.radioButton_ftp)

        self.radioButton_dnla = QRadioButton(self.groupBox_2)
        self.radioButton_dnla.setObjectName(u"radioButton_dnla")

        self.horizontalLayout_2.addWidget(self.radioButton_dnla)

        self.radioButton_http = QRadioButton(self.groupBox_2)
        self.radioButton_http.setObjectName(u"radioButton_http")

        self.horizontalLayout_2.addWidget(self.radioButton_http)

        self.radioButton_webdav = QRadioButton(self.groupBox_2)
        self.radioButton_webdav.setObjectName(u"radioButton_webdav")

        self.horizontalLayout_2.addWidget(self.radioButton_webdav)

        self.radioButton_sftp = QRadioButton(self.groupBox_2)
        self.radioButton_sftp.setObjectName(u"radioButton_sftp")

        self.horizontalLayout_2.addWidget(self.radioButton_sftp)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)


        self.verticalLayout.addWidget(self.groupBox_2)

        self.label_3 = QLabel(NewServeWindow)
        self.label_3.setObjectName(u"label_3")

        self.verticalLayout.addWidget(self.label_3)

        self.lineEdit_path = QLineEdit(NewServeWindow)
        self.lineEdit_path.setObjectName(u"lineEdit_path")

        self.verticalLayout.addWidget(self.lineEdit_path)

        self.groupBox = QGroupBox(NewServeWindow)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_4 = QVBoxLayout(self.groupBox)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.verticalLayout_4.addWidget(self.label_4)

        self.lineEdit_address = QLineEdit(self.groupBox)
        self.lineEdit_address.setObjectName(u"lineEdit_address")

        self.verticalLayout_4.addWidget(self.lineEdit_address)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.verticalLayout_2.addWidget(self.label)

        self.lineEdit_username = QLineEdit(self.groupBox)
        self.lineEdit_username.setObjectName(u"lineEdit_username")

        self.verticalLayout_2.addWidget(self.lineEdit_username)


        self.horizontalLayout.addLayout(self.verticalLayout_2)

        self.verticalLayout_3 = QVBoxLayout()
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.verticalLayout_3.addWidget(self.label_2)

        self.lineEdit_password = QLineEdit(self.groupBox)
        self.lineEdit_password.setObjectName(u"lineEdit_password")
        self.lineEdit_password.setEchoMode(QLineEdit.EchoMode.Password)

        self.verticalLayout_3.addWidget(self.lineEdit_password)


        self.horizontalLayout.addLayout(self.verticalLayout_3)


        self.verticalLayout_4.addLayout(self.horizontalLayout)


        self.verticalLayout.addWidget(self.groupBox)

        self.checkBox_read_only = QCheckBox(NewServeWindow)
        self.checkBox_read_only.setObjectName(u"checkBox_read_only")

        self.verticalLayout.addWidget(self.checkBox_read_only)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        self.buttonBox = QDialogButtonBox(NewServeWindow)
        self.buttonBox.setObjectName(u"buttonBox")
        self.buttonBox.setOrientation(Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(QDialogButtonBox.StandardButton.Cancel|QDialogButtonBox.StandardButton.Ok)

        self.verticalLayout.addWidget(self.buttonBox)


        self.retranslateUi(NewServeWindow)
        self.buttonBox.accepted.connect(NewServeWindow.accept)
        self.buttonBox.rejected.connect(NewServeWindow.reject)

        QMetaObject.connectSlotsByName(NewServeWindow)
    # setupUi

    def retranslateUi(self, NewServeWindow):
        NewServeWindow.setWindowTitle(QCoreApplication.translate("NewServeWindow", u"New serve", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("NewServeWindow", u"Protocol", None))
        self.radioButton_ftp.setText(QCoreApplication.translate("NewServeWindow", u"FTP", None))
        self.radioButton_dnla.setText(QCoreApplication.translate("NewServeWindow", u"DNLA", None))
        self.radioButton_http.setText(QCoreApplication.translate("NewServeWindow", u"HTTP", None))
        self.radioButton_webdav.setText(QCoreApplication.translate("NewServeWindow", u"WebDAV", None))
        self.radioButton_sftp.setText(QCoreApplication.translate("NewServeWindow", u"SFTP", None))
        self.label_3.setText(QCoreApplication.translate("NewServeWindow", u"Path", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_path.setToolTip(QCoreApplication.translate("NewServeWindow", u"Can be \"myremote:path/to/dir\", \"myremote:bucket\", \"myremote:\" or \"/local/path\"", None))
#endif // QT_CONFIG(tooltip)
        self.lineEdit_path.setPlaceholderText(QCoreApplication.translate("NewServeWindow", u"Can be \"myremote:path/to/dir\", \"myremote:bucket\", \"myremote:\" or \"/local/path\"", None))
        self.groupBox.setTitle(QCoreApplication.translate("NewServeWindow", u"Optional", None))
        self.label_4.setText(QCoreApplication.translate("NewServeWindow", u"Address", None))
#if QT_CONFIG(tooltip)
        self.lineEdit_address.setToolTip(QCoreApplication.translate("NewServeWindow", u"<html><head/><body><p>Port or :Port to bind server</p><p>Default:</p><p>FTP - <span style=\" font-family:'Courier New';\">localhost:2121</span></p><p><span style=\" font-family:'Courier New';\">DNLA - :7879</span></p><p><span style=\" font-family:'Courier New';\">HTTP - 127.0.0.1:8080</span></p><p><span style=\" font-family:'Courier New';\">WebDAV - 127.0.0.1:8080</span></p><p><span style=\" font-family:'Courier New';\">SFTP - localhost:2022</span></p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.label.setText(QCoreApplication.translate("NewServeWindow", u"Username", None))
        self.label_2.setText(QCoreApplication.translate("NewServeWindow", u"Password", None))
        self.checkBox_read_only.setText(QCoreApplication.translate("NewServeWindow", u"Read-only", None))
    # retranslateUi

