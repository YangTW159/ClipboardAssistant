from PyQt6.QtCore import QThread, pyqtSignal, QMimeData
from PyQt6.QtWidgets import QApplication
from datetime import datetime

class ClipboardMonitor(QThread):
    # 信号：向外发送 时间、类型、显示文本、原始数据
    new_clip_signal = pyqtSignal(str, str, str, QMimeData)

    def __init__(self):
        super().__init__()
        self.last_mime_data = None  # 上一次剪贴数据，用来去重
        self.running = True

    def run(self):
        clipboard = QApplication.clipboard()
        while self.running:
            # 获取当前剪贴板数据
            current_mime = clipboard.mimeData()

            # ========== 1. 去重判断：和上次一样直接跳过 ==========
            if self.is_same_data(current_mime, self.last_mime_data):
                self.msleep(200)  # 200ms轮询一次，降低CPU占用
                continue

            # 更新上次记录
            self.last_mime_data = current_mime

            # ========== 2. 判断剪贴类型，生成友好展示文字 ==========
            now_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_type = ""
            show_content = ""

            if current_mime.hasText():
                data_type = "text"
                text = current_mime.text().strip()
                show_content = text if len(text) < 80 else text[:80] + "..."
            elif current_mime.hasImage():
                data_type = "image"
                show_content = "[图片剪贴内容，暂不预览]"
            elif current_mime.hasUrls():
                data_type = "file"
                paths = [url.toLocalFile() for url in current_mime.urls()]
                show_content = "[文件粘贴] " + " | ".join(paths)
            else:
                data_type = "other"
                show_content = "[未知剪贴数据]"

            # 发送信号给主窗口更新列表
            self.new_clip_signal.emit(now_time, data_type, show_content, current_mime)
            self.msleep(200)

    def is_same_data(self, new_mime: QMimeData, old_mime: QMimeData) -> bool:
        """判断两次剪贴内容是否一致，用于去重"""
        if old_mime is None:
            return False

        # 文本对比
        if new_mime.hasText() and old_mime.hasText():
            return new_mime.text() == old_mime.text()
        # 图片/文件直接判定为不同（避免图片重复刷屏）
        return False

    def stop_monitor(self):
        self.running = False
        self.wait()