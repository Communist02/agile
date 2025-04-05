# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'main_window.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QDockWidget, QFrame,
    QHBoxLayout, QHeaderView, QMainWindow, QMenu,
    QMenuBar, QPushButton, QSizePolicy, QSpacerItem,
    QStatusBar, QTreeWidget, QTreeWidgetItem, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1280, 800)
        icon = QIcon(QIcon.fromTheme(u"weather-overcast"))
        MainWindow.setWindowIcon(icon)
        self.action_new_remote = QAction(MainWindow)
        self.action_new_remote.setObjectName(u"action_new_remote")
        icon1 = QIcon(QIcon.fromTheme(u"system-file-manager"))
        self.action_new_remote.setIcon(icon1)
        self.action_exit = QAction(MainWindow)
        self.action_exit.setObjectName(u"action_exit")
        icon2 = QIcon(QIcon.fromTheme(u"application-exit"))
        self.action_exit.setIcon(icon2)
        self.action_about = QAction(MainWindow)
        self.action_about.setObjectName(u"action_about")
        icon3 = QIcon(QIcon.fromTheme(u"help-about"))
        self.action_about.setIcon(icon3)
        self.action_list_remotes = QAction(MainWindow)
        self.action_list_remotes.setObjectName(u"action_list_remotes")
        self.action_list_remotes.setCheckable(True)
        self.action_list_remotes.setChecked(True)
        self.action_new_serve = QAction(MainWindow)
        self.action_new_serve.setObjectName(u"action_new_serve")
        icon4 = QIcon(QIcon.fromTheme(u"applications-internet"))
        self.action_new_serve.setIcon(icon4)
        self.action_settings = QAction(MainWindow)
        self.action_settings.setObjectName(u"action_settings")
        icon5 = QIcon(QIcon.fromTheme(u"applications-development"))
        self.action_settings.setIcon(icon5)
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
        icon6 = QIcon(QIcon.fromTheme(u"go-previous"))
        self.pushButton_2.setIcon(icon6)
        self.pushButton_2.setFlat(True)

        self.horizontalLayout.addWidget(self.pushButton_2)

        self.pushButton_3 = QPushButton(self.centralwidget)
        self.pushButton_3.setObjectName(u"pushButton_3")
        sizePolicy.setHeightForWidth(self.pushButton_3.sizePolicy().hasHeightForWidth())
        self.pushButton_3.setSizePolicy(sizePolicy)
        self.pushButton_3.setMinimumSize(QSize(34, 34))
        self.pushButton_3.setMaximumSize(QSize(34, 34))
        icon7 = QIcon(QIcon.fromTheme(u"go-next"))
        self.pushButton_3.setIcon(icon7)
        self.pushButton_3.setFlat(True)

        self.horizontalLayout.addWidget(self.pushButton_3)

        self.button_exit_dir = QPushButton(self.centralwidget)
        self.button_exit_dir.setObjectName(u"button_exit_dir")
        sizePolicy.setHeightForWidth(self.button_exit_dir.sizePolicy().hasHeightForWidth())
        self.button_exit_dir.setSizePolicy(sizePolicy)
        self.button_exit_dir.setMinimumSize(QSize(34, 34))
        self.button_exit_dir.setMaximumSize(QSize(34, 34))
        icon8 = QIcon(QIcon.fromTheme(u"go-up"))
        self.button_exit_dir.setIcon(icon8)
        self.button_exit_dir.setFlat(True)

        self.horizontalLayout.addWidget(self.button_exit_dir)

        self.button_update = QPushButton(self.centralwidget)
        self.button_update.setObjectName(u"button_update")
        self.button_update.setMinimumSize(QSize(34, 34))
        self.button_update.setMaximumSize(QSize(34, 34))
        icon9 = QIcon(QIcon.fromTheme(u"view-refresh"))
        self.button_update.setIcon(icon9)
        self.button_update.setFlat(True)

        self.horizontalLayout.addWidget(self.button_update)

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
        self.horizontalLayout_3 = QHBoxLayout(self.path_list_frame)
        self.horizontalLayout_3.setSpacing(3)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.path_list = QHBoxLayout()
        self.path_list.setSpacing(0)
        self.path_list.setObjectName(u"path_list")

        self.horizontalLayout_3.addLayout(self.path_list)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer)


        self.horizontalLayout.addWidget(self.path_list_frame)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.tree_remotes = QTreeWidget(self.centralwidget)
        self.tree_remotes.setObjectName(u"tree_remotes")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.tree_remotes.sizePolicy().hasHeightForWidth())
        self.tree_remotes.setSizePolicy(sizePolicy2)
        self.tree_remotes.setRootIsDecorated(False)
        self.tree_remotes.setSortingEnabled(True)

        self.horizontalLayout_2.addWidget(self.tree_remotes)

        self.tree_files = QTreeWidget(self.centralwidget)
        self.tree_files.setObjectName(u"tree_files")
        self.tree_files.setDragEnabled(True)
        self.tree_files.setDragDropMode(QAbstractItemView.DragDropMode.DragOnly)
        self.tree_files.setDefaultDropAction(Qt.DropAction.CopyAction)
        self.tree_files.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tree_files.setRootIsDecorated(False)
        self.tree_files.setSortingEnabled(True)

        self.horizontalLayout_2.addWidget(self.tree_files)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1280, 33))
        self.menuClient = QMenu(self.menubar)
        self.menuClient.setObjectName(u"menuClient")
        self.menuOther = QMenu(self.menubar)
        self.menuOther.setObjectName(u"menuOther")
        self.menuView = QMenu(self.menubar)
        self.menuView.setObjectName(u"menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        self.statusbar.setSizeGripEnabled(False)
        MainWindow.setStatusBar(self.statusbar)
        self.dock_tasks = QDockWidget(MainWindow)
        self.dock_tasks.setObjectName(u"dock_tasks")
        self.dockWidgetContents = QWidget()
        self.dockWidgetContents.setObjectName(u"dockWidgetContents")
        self.verticalLayout_2 = QVBoxLayout(self.dockWidgetContents)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.tasks = QTreeWidget(self.dockWidgetContents)
        self.tasks.setObjectName(u"tasks")
        self.tasks.setRootIsDecorated(False)

        self.verticalLayout_2.addWidget(self.tasks)

        self.dock_tasks.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.dock_tasks)

        self.menubar.addAction(self.menuClient.menuAction())
        self.menubar.addAction(self.menuView.menuAction())
        self.menubar.addAction(self.menuOther.menuAction())
        self.menuClient.addAction(self.action_new_remote)
        self.menuClient.addAction(self.action_new_serve)
        self.menuClient.addSeparator()
        self.menuClient.addAction(self.action_settings)
        self.menuClient.addSeparator()
        self.menuClient.addAction(self.action_exit)
        self.menuOther.addAction(self.action_about)
        self.menuView.addAction(self.action_list_remotes)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Cloud Explorer", None))
        self.action_new_remote.setText(QCoreApplication.translate("MainWindow", u"New remote", None))
        self.action_exit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.action_about.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.action_list_remotes.setText(QCoreApplication.translate("MainWindow", u"List remotes", None))
        self.action_new_serve.setText(QCoreApplication.translate("MainWindow", u"New serve", None))
        self.action_settings.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.pushButton_2.setText("")
        self.pushButton_3.setText("")
        self.button_exit_dir.setText("")
        ___qtreewidgetitem = self.tree_remotes.headerItem()
        ___qtreewidgetitem.setText(1, QCoreApplication.translate("MainWindow", u"Type", None));
        ___qtreewidgetitem.setText(0, QCoreApplication.translate("MainWindow", u"Name", None));
        ___qtreewidgetitem1 = self.tree_files.headerItem()
        ___qtreewidgetitem1.setText(3, QCoreApplication.translate("MainWindow", u"Type", None));
        ___qtreewidgetitem1.setText(2, QCoreApplication.translate("MainWindow", u"Modified", None));
        ___qtreewidgetitem1.setText(1, QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtreewidgetitem1.setText(0, QCoreApplication.translate("MainWindow", u"Name", None));
        self.menuClient.setTitle(QCoreApplication.translate("MainWindow", u"Client", None))
        self.menuOther.setTitle(QCoreApplication.translate("MainWindow", u"Other", None))
        self.menuView.setTitle(QCoreApplication.translate("MainWindow", u"View", None))
        ___qtreewidgetitem2 = self.tasks.headerItem()
        ___qtreewidgetitem2.setText(7, QCoreApplication.translate("MainWindow", u"Estimated", None));
        ___qtreewidgetitem2.setText(6, QCoreApplication.translate("MainWindow", u"Speed", None));
        ___qtreewidgetitem2.setText(5, QCoreApplication.translate("MainWindow", u"Progress", None));
        ___qtreewidgetitem2.setText(4, QCoreApplication.translate("MainWindow", u"Size", None));
        ___qtreewidgetitem2.setText(3, QCoreApplication.translate("MainWindow", u"Status", None));
        ___qtreewidgetitem2.setText(2, QCoreApplication.translate("MainWindow", u"Destination", None));
        ___qtreewidgetitem2.setText(1, QCoreApplication.translate("MainWindow", u"Source", None));
        ___qtreewidgetitem2.setText(0, QCoreApplication.translate("MainWindow", u"Operation", None));
    # retranslateUi

