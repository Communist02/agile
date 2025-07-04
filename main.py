import sys
import os
import PySide6.QtAsyncio as QtAsyncio

from PySide6.QtNetwork import QLocalServer, QLocalSocket
from PySide6.QtCore import QLibraryInfo, QLocale, QSettings, QTranslator, Qt
from PySide6.QtWidgets import QApplication

from app.palettes import palettes
from app.main_window import MainWindow


def is_already_running(server_name: str):
    socket = QLocalSocket()
    socket.connectToServer(server_name)
    if socket.waitForConnected(100):
        socket.write(b'ACTIVATE')
        socket.flush()
        socket.disconnectFromServer()
        return True
    return False


def start_server(window: MainWindow, server_name: str):
    server = QLocalServer()
    try:
        server.removeServer(server_name)
    except:
        pass
    server.listen(server_name)

    def on_new_connection():
        client = server.nextPendingConnection()
        if client:
            client.waitForReadyRead(100)
            window.showNormal()
            window.activateWindow()
            client.disconnectFromServer()

    server.newConnection.connect(on_new_connection)


if __name__ == '__main__':
    app = QApplication()
    app.setQuitOnLastWindowClosed(False)
    settings = QSettings('Rclone Explorer', 'Rclone Explorer')
    app.setStyle(settings.value('style', ''))
    palette = settings.value('palette', 'System')
    if palette not in palettes.keys():
        if app.styleHints().colorScheme() == Qt.ColorScheme.Light:
            palette += ' Light'
        else:
            palette += ' Dark'
    app.setPalette(palettes.get(palette, palettes['System']))

    qt_translator = QTranslator()
    translator = QTranslator()

    qt_translator.load(f'qtbase_{QLocale.system().name()}.qm', QLibraryInfo.path(
        QLibraryInfo.LibraryPath.TranslationsPath))
    app.installTranslator(qt_translator)

    if translator.load(f'{os.path.dirname(__file__) + os.sep}translations{os.sep}{QLocale.system().language().name}.qm'):
        app.installTranslator(translator)

    server_name = 'Rclone Explorer'
    server = QLocalServer()

    if is_already_running(server_name):
        print('The application has already been launched')
        sys.exit(0)

    window = MainWindow()
    window.show()

    start_server(window, server_name)

    sys.exit(QtAsyncio.run())
