import sys
from pathlib import Path

from PyQt6.QtWidgets import QMenu, QSystemTrayIcon
from PyQt6.QtGui import QIcon

from core.settings import load_settings


def resource_path(name: str) -> Path:
    base_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base_path / name


class TrayIcon(QSystemTrayIcon):
    def __init__(self, parent, show_cb, quit_cb):
        super().__init__(parent)
        self.show_cb = show_cb
        self.quit_cb = quit_cb
        self.right_menu = QMenu()
        self.refresh_icon()
        self.setToolTip("剪贴板助手 | 左键打开窗口，右键菜单")

        self.right_menu.addAction("打开主窗口", self.show_cb)
        self.right_menu.addAction("彻底退出程序", self.quit_cb)
        self.setContextMenu(self.right_menu)
        self.activated.connect(self.click_event)
        self.setVisible(True)

    def click_event(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show_cb()

    def refresh_icon(self):
        custom_icon = load_settings()["icon_path"]
        icon_path = Path(custom_icon) if custom_icon and Path(custom_icon).is_file() else resource_path("1.ico")
        self.setIcon(QIcon(str(icon_path)))
