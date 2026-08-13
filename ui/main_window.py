from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog, QHBoxLayout, QLineEdit, QListWidget, QListWidgetItem,
    QMainWindow, QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from db.database import (
    clear_all_records, delete_record, export_to_txt, get_all_records, insert_record,
)


class MainWindow(QMainWindow):
    copy_requested = pyqtSignal(str)
    settings_requested = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("剪贴板助手")
        self.resize(1000, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)

        self.search_edit = QLineEdit(placeholderText="搜索剪贴历史内容...")
        self.search_edit.textChanged.connect(self.load_records)
        layout.addWidget(self.search_edit)

        self.record_list = QListWidget()
        self.record_list.setWordWrap(True)
        self.record_list.itemDoubleClicked.connect(self.copy_record)
        self.record_list.setContextMenuPolicy(Qt.ContextMenuPolicy.ActionsContextMenu)
        delete_action = self.record_list.addAction("删除此记录")
        delete_action.triggered.connect(self.delete_selected_record)
        layout.addWidget(self.record_list)

        buttons = QHBoxLayout()
        self.btn_clear = QPushButton("清空全部记录")
        self.btn_clear.clicked.connect(self.clear_all)
        self.btn_export = QPushButton("导出记录到文件")
        self.btn_export.clicked.connect(self.export_to_file)
        self.btn_settings = QPushButton("设置")
        self.btn_settings.clicked.connect(self.settings_requested)
        buttons.addWidget(self.btn_clear)
        buttons.addStretch()
        buttons.addWidget(self.btn_settings)
        buttons.addWidget(self.btn_export)
        layout.addLayout(buttons)
        self.load_records()

    def load_records(self, search_text=""):
        self.record_list.clear()
        for record_id, content, created_at in get_all_records(search_text):
            item = QListWidgetItem(f"[{created_at}]\n{content}")
            item.setData(Qt.ItemDataRole.UserRole, content)
            item.setData(Qt.ItemDataRole.UserRole + 1, record_id)
            self.record_list.addItem(item)
        self.record_list.scrollToTop()

    def add_record(self, content: str):
        if insert_record(content):
            self.load_records(self.search_edit.text())
            self.record_list.setCurrentRow(0)

    def copy_record(self, item):
        content = item.data(Qt.ItemDataRole.UserRole)
        if content:
            self.copy_requested.emit(content)
            self.statusBar().showMessage("已复制原始内容到剪贴板", 2000)

    def delete_selected_record(self):
        item = self.record_list.currentItem()
        if not item:
            return
        delete_record(item.data(Qt.ItemDataRole.UserRole + 1))
        self.load_records(self.search_edit.text())
        self.statusBar().showMessage("已删除记录", 2000)

    def clear_all(self):
        if not self.record_list.count():
            return
        answer = QMessageBox.question(self, "确认清空", "确定要删除所有剪贴板历史记录吗？")
        if answer == QMessageBox.StandardButton.Yes:
            clear_all_records()
            self.load_records()
            self.statusBar().showMessage("已清空全部剪贴记录", 2000)

    def export_to_file(self):
        if not get_all_records():
            QMessageBox.information(self, "提示", "暂无记录可导出")
            return
        save_path, _ = QFileDialog.getSaveFileName(
            self, "导出剪贴板历史", "剪贴板历史记录.txt", "文本文件 (*.txt)"
        )
        if save_path:
            export_to_txt(save_path)
            self.statusBar().showMessage(f"已导出至：{save_path}", 3000)

    def closeEvent(self, event):
        event.ignore()
        self.hide()
