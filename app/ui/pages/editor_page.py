"""メインエディタページ（ツリー + エディタの統合ビュー）。"""
from __future__ import annotations

from typing import Any, Optional

from PySide6.QtWidgets import (
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from app.services.schema_service import SchemaService
from app.ui.editors.holder_group_editor import HolderGroupEditor
from app.ui.editors.valid_holder_editor import ValidHolderEditor
from app.ui.editors.valid_sample_editor import ValidSampleEditor
from app.ui.editors.valid_test_editor import ValidTestEditor
from app.ui.editors.welcome_panel import WelcomePanel
from app.ui.widgets.schema_tree import SchemaTreeWidget

# エディタのインデックス
_IDX_WELCOME = 0
_IDX_HOLDER_GROUP = 1
_IDX_VALID_HOLDER = 2
_IDX_VALID_TEST = 3
_IDX_VALID_SAMPLE = 4

_EDITOR_INDEX: dict[str, int] = {
    "holder_groups": _IDX_HOLDER_GROUP,
    "valid_holders": _IDX_VALID_HOLDER,
    "valid_tests": _IDX_VALID_TEST,
    "valid_samples": _IDX_VALID_SAMPLE,
}


class EditorPage(QWidget):
    """メインエディタページ。

    左: SchemaTreeWidget, 右: エディタスタック
    """

    def __init__(self, service: SchemaService,
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._service = service
        self._current_file_key: str = ""
        self._current_index: int = -1
        self._updating = False
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)

        splitter = QSplitter()
        splitter.setHandleWidth(1)

        # 左: ツリー
        self._tree = SchemaTreeWidget()
        self._tree.setMinimumWidth(250)
        splitter.addWidget(self._tree)

        # 右: エディタスタック
        self._editor_stack = QStackedWidget()
        self._welcome = WelcomePanel()
        self._hg_editor = HolderGroupEditor()
        self._vh_editor = ValidHolderEditor()
        self._vt_editor = ValidTestEditor()
        self._vs_editor = ValidSampleEditor()

        self._editor_stack.addWidget(self._welcome)       # 0
        self._editor_stack.addWidget(self._hg_editor)      # 1
        self._editor_stack.addWidget(self._vh_editor)      # 2
        self._editor_stack.addWidget(self._vt_editor)      # 3
        self._editor_stack.addWidget(self._vs_editor)      # 4

        splitter.addWidget(self._editor_stack)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)
        splitter.setSizes([300, 600])

        vl.addWidget(splitter)

    def _connect_signals(self) -> None:
        self._tree.item_selected.connect(self._on_item_selected)
        self._tree.add_requested.connect(self._on_add)
        self._tree.remove_requested.connect(self._on_remove)
        self._tree.reference_jumped.connect(self._on_reference_jump)

        self._hg_editor.data_changed.connect(
            lambda: self._on_editor_changed("holder_groups")
        )
        self._vh_editor.data_changed.connect(
            lambda: self._on_editor_changed("valid_holders")
        )
        self._vt_editor.data_changed.connect(
            lambda: self._on_editor_changed("valid_tests")
        )
        self._vs_editor.data_changed.connect(
            lambda: self._on_editor_changed("valid_samples")
        )

    # ── 公開 API ──────────────────────────────────────────────────────────

    def refresh(self) -> None:
        """データを再読み込みしてツリーを更新する。"""
        self._service.load_all()
        self._refresh_tree()
        self._editor_stack.setCurrentIndex(_IDX_WELCOME)
        self._current_file_key = ""
        self._current_index = -1

    def _refresh_tree(self) -> None:
        """ツリーを現在のデータで再構築する。"""
        self._tree.set_data({
            "holder_groups": self._service.holder_groups,
            "valid_holders": self._service.valid_holders,
            "valid_tests": self._service.valid_tests,
            "valid_samples": self._service.valid_samples,
        })

    # ── スロット ──────────────────────────────────────────────────────────

    def _on_item_selected(self, file_key: str, index: int) -> None:
        """ツリーでアイテムが選択された。"""
        # 前の編集内容を保存
        self._save_current_editor()

        self._current_file_key = file_key
        self._current_index = index

        items = self._service.get_list(file_key)
        if 0 <= index < len(items):
            item = items[index]
            editor_idx = _EDITOR_INDEX.get(file_key, _IDX_WELCOME)
            self._editor_stack.setCurrentIndex(editor_idx)
            self._updating = True
            if file_key == "holder_groups":
                self._hg_editor.set_item(item)
            elif file_key == "valid_holders":
                self._vh_editor.set_item(item)
            elif file_key == "valid_tests":
                self._vt_editor.set_item(item)
            elif file_key == "valid_samples":
                self._vs_editor.set_item(item)
            self._updating = False

    def _on_editor_changed(self, file_key: str) -> None:
        """エディタのフィールドが変更された。"""
        if self._updating:
            return
        self._save_current_editor()
        self._refresh_tree()

    def _save_current_editor(self) -> None:
        """現在表示中のエディタの内容をサービスに反映する。"""
        if not self._current_file_key or self._current_index < 0:
            return

        items = self._service.get_list(self._current_file_key)
        if self._current_index >= len(items):
            return

        if self._current_file_key == "holder_groups":
            new_data = self._hg_editor.get_item()
        elif self._current_file_key == "valid_holders":
            new_data = self._vh_editor.get_item()
        elif self._current_file_key == "valid_tests":
            new_data = self._vt_editor.get_item()
        elif self._current_file_key == "valid_samples":
            new_data = self._vs_editor.get_item()
        else:
            return

        self._service.update_item(
            self._current_file_key, self._current_index, new_data
        )

    def _on_add(self, file_key: str) -> None:
        """追加がリクエストされた。"""
        templates = {
            "holder_groups": self._service.new_holder_group,
            "valid_holders": self._service.new_valid_holder,
            "valid_tests": self._service.new_valid_test,
            "valid_samples": self._service.new_valid_sample,
        }
        factory = templates.get(file_key)
        if factory:
            self._service.add_item(file_key, factory())
            self._refresh_tree()

    def _on_remove(self, file_key: str, index: int) -> None:
        """削除がリクエストされた。"""
        items = self._service.get_list(file_key)
        if 0 <= index < len(items):
            item = items[index]
            name = (item.get("holder_group_code") or item.get("set_code")
                    or item.get("display_name") or "(不明)")
            reply = QMessageBox.question(
                self, "確認",
                f"「{name}」を削除しますか？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self._service.remove_item(file_key, index)
                self._editor_stack.setCurrentIndex(_IDX_WELCOME)
                self._current_file_key = ""
                self._current_index = -1
                self._refresh_tree()

    def _on_reference_jump(self, set_code: str) -> None:
        """参照ノードからのジャンプ。"""
        self._save_current_editor()
        self._tree.select_by_set_code("valid_holders", set_code)
