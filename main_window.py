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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QHeaderView,
    QListWidget, QListWidgetItem, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QToolButton, QTreeWidget, QTreeWidgetItem,
    QVBoxLayout, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1033, 771)
        MainWindow.setStyleSheet(u"#path_list_frame1 QPushButton {\n"
"	border: 0px;\n"
"}")
        self.action_new_remote = QAction(MainWindow)
        self.action_new_remote.setObjectName(u"action_new_remote")
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
        self.pushButton_2 = QPushButton(self.centralwidget)
        self.pushButton_2.setObjectName(u"pushButton_2")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton_2.sizePolicy().hasHeightForWidth())
        self.pushButton_2.setSizePolicy(sizePolicy)
        self.pushButton_2.setMinimumSize(QSize(34, 34))
        self.pushButton_2.setMaximumSize(QSize(34, 34))
        self.pushButton_2.setFlat(True)

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QSize(34, 34))
        self.pushButton_3.setMaximumSize(QSize(34, 34))
        self.pushButton_3.setFlat(True)

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.button_exit_dir = QPushButton(self.centralwidget)
        self.button_exit_dir.setObjectName(u"button_exit_dir")
        sizePolicy.setHeightForWidth(self.button_exit_dir.sizePolicy().hasHeightForWidth())
        self.button_exit_dir.setSizePolicy(sizePolicy)
        self.button_exit_dir.setMinimumSize(QSize(34, 34))
        self.button_exit_dir.setMaximumSize(QSize(34, 34))
        self.button_exit_dir.setFlat(True)

        self.horizontalLayout.addWidget(self.button_exit_dir)

        self.openMenuButton = QToolButton(self.centralwidget)
        self.openMenuButton.setObjectName(u"openMenuButton")
        self.openMenuButton.setMinimumSize(QSize(34, 34))
        self.openMenuButton.setMaximumSize(QSize(34, 34))

        self.horizontalLayout.addWidget(self.openMenuButton)

        self.path_list_frame = QFrame(self.centralwidget)
        self.path_list_frame.setObjectName(u"path_list_frame")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.path_list_frame.sizePolicy().hasHeightForWidth())
        self.path_list_frame.setSizePolicy(sizePolicy1)
        self.path_list_frame.setMinimumSize(QSize(0, 34))
        self.path_list_frame.setMaximumSize(QSize(16777215, 34))
        self.path_list_frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.path_list_frame.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout_3 = QHBoxLayout(self.path_list_frame)
        self.horizontalLayout_3.setSpacing(3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.path_list = QHBoxLayout()
        self.path_list.setObjectName(u"path_list")

        self.horizontalLayout_3.addLayout(self.path_list)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.horizontalLayout.addWidget(self.path_list_frame)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.disk_list = QListWidget(self.centralwidget)
        self.disk_list.setObjectName(u"disk_list")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.disk_list.sizePolicy().hasHeightForWidth())
        self.disk_list.setSizePolicy(sizePolicy2)

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
        self.menuClient.addAction(self.action_new_remote)
        self.menuClient.addAction(self.actionExit)
        self.menuOther.addAction(self.actionAbout)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Cloud Explorer", None))
        self.action_new_remote.setText(QCoreApplication.translate("MainWindow", u"New remote", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionAbout.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"\u1438", None))
        self.pushButton_3.setText(QCoreApplication.translate("MainWindow", u"\u1433", None))
        self.button_exit_dir.setText(QCoreApplication.translate("MainWindow", u"\u1431", None))
        self.openMenuButton.setText(QCoreApplication.translate("MainWindow", u"\u2630", None))
        ___qtreewidgetitem = self.file_view.headerItem()
        ___qtreewidgetitem.setText(3, QCoreApplication.translate("MainWindow", u"Type", None));
        ___qtreewidgetitem.setText(2, QCoreApplication.translate("MainWindow", u"Modified", None));
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Name", None));
        self.menuClient.setTitle(QCoreApplication.translate("MainWindow", u"Client", None))
        self.menuOther.setTitle(QCoreApplication.translate("MainWindow", u"Other", None))
    # retranslateUi

