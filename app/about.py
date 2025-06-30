import os
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog
from app.views import about_window


class AboutWindow(QDialog):
    def __init__(self):
        super(AboutWindow, self).__init__()
        self.ui = about_window.Ui_Dialog()
        self.ui.setupUi(self)

        self.setWindowIcon(
            QIcon(os.path.dirname(__file__) + '/resources/' + 'favicon.ico'))
