"""DataSchemaStudio アプリケーションエントリポイント。

    QMainWindow
    └─ centralwidget (QHBoxLayout)
       ├─ sidebar (75px, 2ページ: エディタ / 設定)
       └─ widget_main (QVBoxLayout)
          ├─ header (50px, ページ名 + ツールバー)
          ├─ stack_pages (QStackedWidget, 2ページ)
          └─ statusbar (35px)
"""
from __future__ import annotations

import platform
import sys
from typing import Optional

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from app import config
from app.services.schema_service import SchemaService
from app.ui.pages.editor_page import EditorPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.styles import GLOBAL_QSS
from app.ui.widgets.icon_utils import get_icon
from app.ui.widgets.sidebar import PAGE_INFO, Sidebar

_PAGE_IDX: dict[str, int] = {
    "editor": 0,
    "settings": 1,
}


class MainWindow(QMainWindow):
    """DataSchemaStudio メインウィンドウ。"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle(f"DataSchemaStudio ver.{config.APP_VERSION}")
        self.setMinimumSize(1024, 700)
        self._service = SchemaService()
        self._setup_ui()
        self._connect_signals()
        self.showMaximized()
        # 初期データ読み込み
        self._editor_page.refresh()

    def _setup_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # サイドバー
        self.sidebar = Sidebar()
        root.addWidget(self.sidebar)

        # メインエリア
        widget_main = self._build_main()
        root.addWidget(widget_main, 1)

    def _build_main(self) -> QWidget:
        widget = QWidget()
        widget.setObjectName("widget_main")
        vl = QVBoxLayout(widget)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(0)

        vl.addWidget(self._build_header())
        vl.addWidget(self._build_stack())
        vl.addWidget(self._build_statusbar())

        return widget

    def _build_header(self) -> QWidget:
        header = QWidget()
        header.setFixedHeight(50)
        header.setObjectName("widget_header")
        hl = QHBoxLayout(header)
        hl.setContentsMargins(16, 8, 16, 8)
        hl.setSpacing(12)

        self.btn_active_page = QToolButton()
        self.btn_active_page.setObjectName("btn_active_page")
        self.btn_active_page.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.btn_active_page.setIconSize(QSize(24, 24))
        self.btn_active_page.setIcon(get_icon(":/icons/data.svg", "#333333", size=24))
        self.btn_active_page.setText("エディタ")
        self.btn_active_page.setFixedHeight(34)
        hl.addWidget(self.btn_active_page)

        hl.addStretch()

        # 保存ボタン
        self.btn_save = QToolButton()
        self.btn_save.setObjectName("btn_save")
        self.btn_save.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.btn_save.setIconSize(QSize(20, 20))
        self.btn_save.setText("保存")
        self.btn_save.setFixedHeight(34)
        hl.addWidget(self.btn_save)

        # 再読み込みボタン
        self.btn_reload = QToolButton()
        self.btn_reload.setToolButtonStyle(
            Qt.ToolButtonStyle.ToolButtonTextBesideIcon
        )
        self.btn_reload.setIconSize(QSize(20, 20))
        self.btn_reload.setText("再読み込み")
        self.btn_reload.setFixedHeight(34)
        self.btn_reload.setStyleSheet(
            "QToolButton { background: transparent; border: 1px solid #d1d5db; "
            "border-radius: 6px; padding: 4px 12px; font-size: 13px; }"
            "QToolButton:hover { border-color: #3b82f6; color: #3b82f6; }"
        )
        hl.addWidget(self.btn_reload)

        return header

    def _build_stack(self) -> QStackedWidget:
        self.stack = QStackedWidget()
        self.stack.setObjectName("stack_pages")

        self._editor_page = EditorPage(self._service)
        self._settings_page = SettingsPage()

        self.stack.addWidget(self._editor_page)    # 0: editor
        self.stack.addWidget(self._settings_page)   # 1: settings

        return self.stack

    def _build_statusbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(35)
        bar.setObjectName("widget_statusbar")
        hl = QHBoxLayout(bar)
        hl.setContentsMargins(12, 0, 12, 0)
        hl.setSpacing(8)

        self.label_status = QLabel("準備完了")
        self.label_status.setObjectName("label_status")
        hl.addWidget(self.label_status)

        hl.addStretch()
        return bar

    def _connect_signals(self) -> None:
        self.sidebar.page_changed.connect(self._on_page_change)
        self.btn_save.clicked.connect(self._on_save)
        self.btn_reload.clicked.connect(self._on_reload)
        self._settings_page.paths_changed.connect(self._on_paths_changed)

    def _on_page_change(self, page_id: str) -> None:
        idx = _PAGE_IDX.get(page_id, 0)
        self.stack.setCurrentIndex(idx)
        name, svg_path = PAGE_INFO.get(page_id, ("", ""))
        self.btn_active_page.setText(name)
        if svg_path:
            self.btn_active_page.setIcon(get_icon(svg_path, "#333333", size=24))

    def _on_save(self) -> None:
        errors = self._service.validate_references()
        if errors:
            msg = "参照整合性の警告:\n\n" + "\n".join(errors)
            reply = QMessageBox.warning(
                self, "整合性警告", msg + "\n\nそのまま保存しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        try:
            self._service.save_all()
            self.label_status.setText("保存しました")
        except Exception as e:
            QMessageBox.critical(self, "保存エラー", str(e))

    def _on_reload(self) -> None:
        if self._service.is_dirty:
            reply = QMessageBox.question(
                self, "確認",
                "未保存の変更があります。破棄して再読み込みしますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        self._editor_page.refresh()
        self.label_status.setText("再読み込みしました")

    def _on_paths_changed(self) -> None:
        self._editor_page.refresh()
        self.label_status.setText("パス設定が変更されました。データを再読み込みしました。")


def _ensure_user_profile(qapp: QApplication) -> bool:
    """USERPROFILE が有効か確認し、未設定ならフォルダ選択ダイアログで設定を促す。"""
    if config.load_user_profile() is not None:
        return True

    from app.ui.dialogs.setup_profile_dialog import SetupUserProfileDialog

    dlg = SetupUserProfileDialog()
    return dlg.exec() == SetupUserProfileDialog.DialogCode.Accepted


def main() -> None:
    """アプリケーションを起動する。"""
    qapp = QApplication(sys.argv)

    # 外観設定
    if platform.system() == "Darwin":
        qapp.setFont(QFont("Hiragino Sans", 12))
    else:
        qapp.setFont(QFont("Yu Gothic UI", 10))
    qapp.setStyle("Fusion")
    qapp.setStyleSheet(GLOBAL_QSS)

    if not _ensure_user_profile(qapp):
        sys.exit(0)

    window = MainWindow()
    sys.exit(qapp.exec())


if __name__ == "__main__":
    main()
