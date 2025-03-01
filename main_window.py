# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QAction, QBrush, QColor, QConicalGradient,
    QCursor, QFont, QFontDatabase, QGradient,
    QIcon, QImage, QKeySequence, QLinearGradient,
    QPainter, QPalette, QPixmap, QRadialGradient,
    QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QHeaderView, QListWidget,
    QListWidgetItem, QMainWindow, QMenu, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QToolButton, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1033, 771)
        self.actionAdd_disk = QAction(MainWindow)
        self.actionAdd_disk.setObjectName(u"actionAdd_disk")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionAbout = QAction(MainWindow)
        self.actionAbout.setObjectName(u"actionAbout")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.openMenuButton = QToolButton(self.centralwidget)
        self.openMenuButton.setObjectName(u"openMenuButton")

        self.horizontalLayout.addWidget(self.openMenuButton)

        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.button_exit_dir = QPushButton(self.centralwidget)
        self.button_exit_dir.setObjectName(u"button_exit_dir")

        self.horizontalLayout.addWidget(self.button_exit_dir)

        self.path_list = QHBoxLayout()
        self.path_list.setObjectName(u"path_list")

        self.horizontalLayout.addLayout(self.path_list)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.disk_list = QListWidget(self.centralwidget)
        self.disk_list.setObjectName(u"disk_list")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.disk_list.sizePolicy().hasHeightForWidth())
        self.disk_list.setSizePolicy(sizePolicy)

        self.horizontalLayout_2.addWidget(self.disk_list)

        self.file_view = QTreeWidget(self.centralwidget)
        self.file_view.setObjectName(u"file_view")

        self.horizontalLayout_2.addWidget(self.file_view)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1033, 33))
        self.menuClient = QMenu(self.menubar)
        self.menuClient.setObjectName(u"menuClient")
        self.menuOther = QMenu(self.menubar)
        self.menuOther.setObjectName(u"menuOther")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.menubar.addAction(self.menuClient.menuAction())
        self.menubar.addAction(self.menuOther.menuAction())
        self.menuClient.addAction(self.actionAdd_disk)
        self.menuClient.addAction(self.actionExit)
        self.menuOther.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Cloud Explorer", None))
        self.actionAdd_disk.setText(QCoreApplication.translate("MainWindow", u"Add disk", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.openMenuButton.setText(QCoreApplication.translate("MainWindow", u"\u2630", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u1438", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u1433", None))
        self.button_exit_dir.setText(QCoreApplication.translate("MainWindow", u"\u1431", None))
        ___qtreewidgetitem = self.file_view.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("MainWindow", u"Type", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"Modified", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Name", None));
        self.menuClient.setTitle(QCoreApplication.translate("MainWindow", u"Client", None))
        self.menuOther.setTitle(QCoreApplication.translate("MainWindow", u"Other", None))
    # retranslateUi

