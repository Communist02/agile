import os

from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QStyleFactory
from app.palettes import palettes
from app.views import settings_window


class SettingsWindow(QDialog):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.ui = settings_window.Ui_SettingsWindow()
        self.ui.setupUi(self)

        self.settings = QSettings('Cloud Explorer', 'Cloud Explorer')

        self.setWindowIcon(
            QIcon(os.path.dirname(__file__) + '/resources/' + 'favicon.ico'))

        styles = QStyleFactory.keys()
        for i in range(len(styles)):
            styles[i] = styles[i].lower()
        self.ui.comboBox_style.addItems(styles)
        self.ui.comboBox_style.setCurrentText(self.settings.value('style', self.style().name()))

        palettes_list: list = list(palettes.keys())
        # if self.ui.comboBox_style.currentText() != 'fusion' and self.ui.comboBox_style.currentText() != 'windows':
        for i in range(len(palettes_list)):
            palettes_list[i] = palettes_list[i].replace(' Dark', '').replace(' Light', '')

        self.ui.comboBox_palette.addItems(set(palettes_list))
        self.ui.comboBox_palette.setCurrentText(
            self.settings.value('palette', 'System'))

        self.ui.buttonBox.accepted.connect(self.ok)

    def ok(self):
        # app.setStyle(self.ui.comboBox_style.currentText())
        # app.setPalette(palettes[self.ui.comboBox_palette.currentText()])

        self.settings.setValue('style', self.ui.comboBox_style.currentText())
        self.settings.setValue(
            'palette', self.ui.comboBox_palette.currentText())
