"""Background worker that calls the AI API without freezing the UI thread."""
from PyQt6.QtCore import QThread, pyqtSignal

from core.ai_assistant import call_ai


class AiWorker(QThread):
    succeeded = pyqtSignal(str, str)  # action, result text
    failed = pyqtSignal(str)          # error message

    def __init__(self, base_url: str, api_key: str, model: str,
                 action: str, text: str, parent=None):
        super().__init__(parent)
        self._args = (base_url, api_key, model, action, text)

    def run(self):
        try:
            result = call_ai(*self._args)
            self.succeeded.emit(self._args[3], result)
        except Exception as error:  # surface any failure to the UI thread
            self.failed.emit(str(error))
