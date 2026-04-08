"""設定ページ — USERPROFILE + 4ファイル個別パス設定。"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app import config


class SettingsPage(QWidget):
    """設定ページ。

    Signals:
        paths_changed: パス設定が変更された。
    """

    paths_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui()
        self._load_current()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(20, 16, 20, 16)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        vl = QVBoxLayout(content)
        vl.setSpacing(16)

        # ── USERPROFILE ──────────────────────────────────────────────────
        grp_profile = QGroupBox("USERPROFILE")
        form_profile = QFormLayout(grp_profile)

        self._lbl_profile = QLineEdit()
        self._lbl_profile.setReadOnly(True)
        self._lbl_profile.setStyleSheet("background: #f3f4f6;")
        form_profile.addRow("現在のパス", self._lbl_profile)

        btn_change = QPushButton("変更")
        btn_change.setFixedWidth(80)
        btn_change.clicked.connect(self._change_profile)
        form_profile.addRow("", btn_change)

        # 派生パスプレビュー
        self._lbl_sync = QLabel()
        self._lbl_sync.setStyleSheet("color: #6b7280; font-size: 11px;")
        form_profile.addRow("Sync Root", self._lbl_sync)

        self._lbl_data = QLabel()
        self._lbl_data.setStyleSheet("color: #6b7280; font-size: 11px;")
        form_profile.addRow("Data Path", self._lbl_data)

        vl.addWidget(grp_profile)

        # ── ファイルパス設定 ──────────────────────────────────────────────
        grp_files = QGroupBox("ファイルパス設定")
        form_files = QFormLayout(grp_files)

        self._path_edits: dict[str, QLineEdit] = {}
        labels = {
            "holder_groups": "holder_groups.json",
            "valid_holders": "valid_holders.json",
            "valid_tests": "valid_tests.json",
            "valid_samples": "valid_samples.json",
        }
        for key, label in labels.items():
            row = QHBoxLayout()
            edit = QLineEdit()
            edit.setPlaceholderText(f"デフォルト: {config.DEFAULT_SOURCE_DIR / label}")
            row.addWidget(edit)
            btn = QPushButton("参照")
            btn.setFixedWidth(60)
            btn.clicked.connect(lambda _=False, k=key: self._browse_file(k))
            row.addWidget(btn)
            form_files.addRow(label, row)
            self._path_edits[key] = edit

        btn_save = QPushButton("パス設定を保存")
        btn_save.setStyleSheet(
            "QPushButton { background: #3b82f6; color: white; border: none; "
            "border-radius: 6px; padding: 8px 16px; font-weight: 600; }"
            "QPushButton:hover { background: #2563eb; }"
        )
        btn_save.clicked.connect(self._save_paths)
        form_files.addRow("", btn_save)

        vl.addWidget(grp_files)
        vl.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def _load_current(self) -> None:
        """現在の設定値をUIに反映する。"""
        self._lbl_profile.setText(str(config.USER_PROFILE))
        self._lbl_sync.setText(str(config.SYNC_ROOT))
        self._lbl_data.setText(str(config.DATA_PATH))

        paths = config.load_file_paths()
        for key, edit in self._path_edits.items():
            edit.setText(paths.get(key, ""))

    def _change_profile(self) -> None:
        """USERPROFILEフォルダを変更する。"""
        folder = QFileDialog.getExistingDirectory(
            self, "ユーザープロファイルフォルダを選択",
            str(config.USER_PROFILE),
        )
        if not folder:
            return
        p = Path(folder)
        if not p.exists() or not p.is_dir():
            return
        config.save_user_profile(p)
        config.reload_user_profile(p)
        self._load_current()
        self.paths_changed.emit()

    def _browse_file(self, key: str) -> None:
        """ファイル選択ダイアログを開く。"""
        path, _ = QFileDialog.getOpenFileName(
            self, f"{key}.json を選択",
            str(config.DEFAULT_SOURCE_DIR),
            "JSON Files (*.json);;All Files (*)",
        )
        if path:
            self._path_edits[key].setText(path)

    def _save_paths(self) -> None:
        """ファイルパス設定を保存する。"""
        paths: dict[str, str] = {}
        for key, edit in self._path_edits.items():
            text = edit.text().strip()
            if text:
                paths[key] = text
        config.save_file_paths(paths)
        QMessageBox.information(self, "保存完了", "ファイルパス設定を保存しました。")
        self.paths_changed.emit()
