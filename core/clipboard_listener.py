from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtGui import QClipboard
from PyQt6.QtWidgets import QApplication, QLineEdit


class ClipboardListener(QObject):
    """Forward text clipboard changes on Qt's main thread."""

    new_content_signal = pyqtSignal(str)

    def __init__(self, clipboard: QClipboard):
        super().__init__()
        self.clipboard = clipboard
        self._ignored_text = None
        self.clipboard.dataChanged.connect(self._on_clipboard_changed)

    def ignore_next_change(self, content: str):
        self._ignored_text = content

    def _on_clipboard_changed(self):
        text = self.clipboard.text()
        if not text.strip():
            return
        focused_widget = QApplication.instance().focusWidget()
        if isinstance(focused_widget, QLineEdit) and focused_widget.selectedText() == text:
            return
        if text == self._ignored_text:
            self._ignored_text = None
            return
        self._ignored_text = None
        self.new_content_signal.emit(text)
