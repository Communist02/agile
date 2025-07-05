import os

from PySide6.QtCore import QSettings, Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QDialog, QStyleFactory
from app.palettes import palettes
from app.views import settings_window


class SettingsWindow(QDialog):
    def __init__(self):
        super(SettingsWindow, self).__init__()
        self.ui = settings_window.Ui_SettingsWindow()
        self.ui.setupUi(self)

        self.settings = QSettings('Rclone Explorer', 'Rclone Explorer')

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

        unique_list = []
        for palette in palettes_list:
            if palette not in unique_list:
                unique_list.append(palette)

        self.ui.comboBox_palette.addItems(unique_list)
        self.ui.comboBox_palette.setCurrentText(
            self.settings.value('palette', 'System'))

        self.ui.buttonBox.accepted.connect(self.ok)

    def ok(self):
        QApplication.setStyle(self.ui.comboBox_style.currentText())
        palette = self.ui.comboBox_palette.currentText()
        if QApplication.styleHints().colorScheme() == Qt.ColorScheme.Light:
            palette += ' Light'
        else:
            palette += ' Dark'
        QApplication.setPalette(palettes.get(palette, palettes['System']))

        self.settings.setValue('style', self.ui.comboBox_style.currentText())
        self.settings.setValue(
            'palette', self.ui.comboBox_palette.currentText())
