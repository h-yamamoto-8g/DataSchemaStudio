"""未選択時のウェルカムパネル。"""
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class WelcomePanel(QWidget):
    """ツリーでアイテム未選択時に表示するパネル。"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        vl = QVBoxLayout(self)
        vl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("DataSchemaStudio")
        title.setStyleSheet("font-size: 20px; font-weight: 600; color: #6b7280;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(title)

        desc = QLabel("左のツリーからアイテムを選択して編集してください")
        desc.setStyleSheet("font-size: 13px; color: #9ca3af;")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        vl.addWidget(desc)
