import keyboard
from PyQt6.QtCore import QObject, pyqtSignal

class HotKeyWorker(QObject):
    show_window_signal = pyqtSignal()

    def __init__(self):
        super().__init__()

    def start_listen(self):
        def callback():
            self.show_window_signal.emit()

        keyboard.add_hotkey('ctrl+alt+v', callback)
        keyboard.wait()