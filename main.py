import sys

from PyQt6.QtCore import Qt
from PyQt6.QtNetwork import QLocalServer, QLocalSocket
from PyQt6.QtWidgets import QApplication

from core.clipboard_listener import ClipboardListener
from core.settings import load_settings
from db.database import init_db
from ui.main_window import MainWindow
from ui.settings_dialog import SettingsDialog
from ui.tray_icon import TrayIcon


SERVER_NAME = "ClipboardAssistant.SingleInstance.v1"


def notify_existing_instance() -> bool:
    socket = QLocalSocket()
    socket.connectToServer(SERVER_NAME)
    if socket.waitForConnected(300):
        socket.write(b"show")
        socket.waitForBytesWritten(300)
        socket.disconnectFromServer()
        return True
    return False


def main():
    app = QApplication(sys.argv)
    if notify_existing_instance():
        return 0

    QLocalServer.removeServer(SERVER_NAME)
    server = QLocalServer()
    if not server.listen(SERVER_NAME):
        return 1

    app.setQuitOnLastWindowClosed(False)
    init_db()
    window = MainWindow()
    clipboard = app.clipboard()
    listener = ClipboardListener(clipboard)
    listener.new_content_signal.connect(window.add_record)

    def copy_from_history(content):
        listener.ignore_next_change(content)
        clipboard.setText(content)

    window.copy_requested.connect(copy_from_history)

    def show_window():
        window.show()
        window.setWindowState(Qt.WindowState.WindowNoState)
        window.raise_()
        window.activateWindow()

    def open_settings():
        dialog = SettingsDialog(window)
        if dialog.exec():
            tray.refresh_icon()
            window.load_records(window.search_edit.text())

    window.settings_requested.connect(open_settings)

    def handle_connection():
        connection = server.nextPendingConnection()
        connection.readyRead.connect(show_window)
        connection.disconnected.connect(connection.deleteLater)

    server.newConnection.connect(handle_connection)
    tray = TrayIcon(window, show_window, app.quit)
    if load_settings()["show_window_on_start"]:
        window.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
