"""サイドバーナビゲーション（2ページ版: エディタ / 設定）。"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QSize, Signal
from PySide6.QtWidgets import QToolButton, QVBoxLayout, QWidget

from app.ui.widgets.icon_utils import get_icon

_TEXT2 = "#6b7280"
_TEXT = "#333333"
_ACCENT = "#3b82f6"
_ACTIVE_BG = "#eff6ff"
_ICON_SIZE = QSize(22, 22)

PAGE_INFO: dict[str, tuple[str, str]] = {
    "editor":   ("エディタ", ":/icons/data.svg"),
    "settings": ("設定",     ":/icons/setting.svg"),
}


class _NavButton(QToolButton):
    """サイドバーのナビゲーションボタン。"""

    def __init__(self, page_id: str, label: str, svg_path: str,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._page_id = page_id
        self._svg_path = svg_path
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setFixedSize(60, 56)
        self.setIconSize(_ICON_SIZE)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(label)
        self.setText(label)
        self.set_active(False)

    def set_active(self, active: bool) -> None:
        if active:
            self.setIcon(get_icon(self._svg_path, _ACCENT))
            self.setStyleSheet(f"""
                QToolButton {{
                    background: {_ACTIVE_BG}; color: {_ACCENT};
                    border: none; border-radius: 8px;
                    font-size: 9px; font-weight: 600; padding: 2px;
                }}
                QToolButton:hover {{ background: #dbeafe; }}
            """)
        else:
            self.setIcon(get_icon(self._svg_path, _TEXT2))
            self.setStyleSheet(f"""
                QToolButton {{
                    background: transparent; color: {_TEXT2};
                    border: none; border-radius: 8px;
                    font-size: 9px; font-weight: 500; padding: 2px;
                }}
                QToolButton:hover {{ background: #f3f4f6; color: {_TEXT}; }}
            """)


class Sidebar(QWidget):
    """アプリケーションサイドバー（75px 幅、2ページ）。

    Signals:
        page_changed (str): ページが変更された時に page_id を送出。
    """

    page_changed = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(75)
        self.setObjectName("frame_sidebar")
        self.setAutoFillBackground(True)
        self._buttons: dict[str, _NavButton] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(0, 10, 0, 10)
        vl.setSpacing(2)

        for page_id, (name, svg_path) in PAGE_INFO.items():
            btn = _NavButton(page_id, name, svg_path, parent=self)
            btn.clicked.connect(
                lambda _checked=False, pid=page_id: self._on_click(pid)
            )
            vl.addWidget(btn, alignment=Qt.AlignmentFlag.AlignHCenter)
            self._buttons[page_id] = btn

        vl.addStretch()
        self.set_active("editor")

    def _on_click(self, page_id: str) -> None:
        self.set_active(page_id)
        self.page_changed.emit(page_id)

    def set_active(self, page_id: str) -> None:
        for pid, btn in self._buttons.items():
            btn.set_active(pid == page_id)
