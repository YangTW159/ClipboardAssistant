"""Dialog that shows the result of an AI action."""
from PyQt6.QtWidgets import (
    QApplication, QDialog, QHBoxLayout, QPlainTextEdit, QPushButton, QVBoxLayout,
)


class AiResultDialog(QDialog):
    def __init__(self, action: str, result: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"AI {action} 结果")
        self.resize(640, 420)

        layout = QVBoxLayout(self)

        self.view = QPlainTextEdit()
        self.view.setReadOnly(True)
        self.view.setPlainText(result)
        layout.addWidget(self.view)

        buttons = QHBoxLayout()
        copy_button = QPushButton("复制结果到剪贴板")
        copy_button.clicked.connect(self._copy)
        close_button = QPushButton("关闭")
        close_button.clicked.connect(self.accept)
        buttons.addStretch()
        buttons.addWidget(copy_button)
        buttons.addWidget(close_button)
        layout.addLayout(buttons)

    def _copy(self):
        QApplication.clipboard().setText(self.view.toPlainText())
