from pathlib import Path

from PyQt6.QtWidgets import (
    QCheckBox, QDialog, QFileDialog, QFormLayout, QHBoxLayout, QLabel,
    QLineEdit, QMessageBox, QPushButton, QSpinBox, QVBoxLayout,
)

from core.settings import load_settings, save_settings


class SettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("设置")
        self.setMinimumWidth(430)
        settings = load_settings()

        self.auto_start = QCheckBox("开机自动启动")
        self.auto_start.setChecked(settings["auto_start"])
        self.show_on_start = QCheckBox("启动后显示主窗口")
        self.show_on_start.setChecked(settings["show_window_on_start"])
        self.max_records = QSpinBox()
        self.max_records.setRange(50, 10000)
        self.max_records.setValue(settings["max_records"])
        self.duplicate_seconds = QSpinBox()
        self.duplicate_seconds.setRange(0, 60)
        self.duplicate_seconds.setSuffix(" 秒")
        self.duplicate_seconds.setValue(settings["duplicate_window_seconds"])
        self.icon_path = QLineEdit(settings["icon_path"])
        browse = QPushButton("选择图标")
        browse.clicked.connect(self.select_icon)
        icon_layout = QHBoxLayout()
        icon_layout.addWidget(self.icon_path)
        icon_layout.addWidget(browse)

        form = QFormLayout()
        form.addRow(self.auto_start)
        form.addRow(self.show_on_start)
        form.addRow("最多保存记录：", self.max_records)
        form.addRow("相同内容去重：", self.duplicate_seconds)
        form.addRow("托盘图标：", icon_layout)

        self.ai_base = QLineEdit(settings["ai_api_base"])
        self.ai_key = QLineEdit(settings["ai_api_key"])
        self.ai_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.ai_model = QLineEdit(settings["ai_model"])
        form.addRow("AI 接口地址：", self.ai_base)
        form.addRow("AI API Key：", self.ai_key)
        form.addRow("模型名称：", self.ai_model)

        note = QLabel(
            "右键历史记录可单条删除，也可一键 AI 总结/翻译/润色。\n"
            "AI 功能兼容 OpenAI 接口（如 DeepSeek、火山方舟），Key 仅保存在本机。"
        )
        note.setWordWrap(True)
        save_button = QPushButton("保存")
        save_button.clicked.connect(self.save)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        buttons = QHBoxLayout()
        buttons.addStretch()
        buttons.addWidget(cancel_button)
        buttons.addWidget(save_button)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(note)
        layout.addLayout(buttons)

    def select_icon(self):
        selected, _ = QFileDialog.getOpenFileName(
            self, "选择图标", self.icon_path.text(), "图标文件 (*.ico *.png *.jpg *.jpeg)"
        )
        if selected:
            self.icon_path.setText(selected)

    def save(self):
        icon_path = self.icon_path.text().strip()
        if icon_path and not Path(icon_path).is_file():
            QMessageBox.warning(self, "图标无效", "选择的图标文件不存在。")
            return
        try:
            save_settings({
                "auto_start": self.auto_start.isChecked(),
                "show_window_on_start": self.show_on_start.isChecked(),
                "max_records": self.max_records.value(),
                "duplicate_window_seconds": self.duplicate_seconds.value(),
                "icon_path": icon_path,
                "ai_api_base": self.ai_base.text().strip(),
                "ai_api_key": self.ai_key.text().strip(),
                "ai_model": self.ai_model.text().strip(),
            })
        except RuntimeError as error:
            QMessageBox.warning(self, "保存失败", str(error))
            return
        self.accept()
