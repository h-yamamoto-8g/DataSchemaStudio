"""スキーマデータのツリーウィジェット。

4ファイルをトップレベルノードとして表示し、
holder_groups の子ノードに valid_holders 参照を表示する。
"""
from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QMenu,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)


# ツリーノードに格納するカスタムデータのロール
ROLE_FILE_KEY = Qt.ItemDataRole.UserRole
ROLE_ITEM_INDEX = Qt.ItemDataRole.UserRole + 1
ROLE_IS_REFERENCE = Qt.ItemDataRole.UserRole + 2
ROLE_REF_SET_CODE = Qt.ItemDataRole.UserRole + 3

_FILE_LABELS: dict[str, str] = {
    "holder_groups": "Holder Groups",
    "valid_holders": "Valid Holders",
    "valid_tests": "Valid Tests",
    "valid_samples": "Valid Samples",
}


class SchemaTreeWidget(QWidget):
    """スキーマデータをツリー表示するウィジェット。

    Signals:
        item_selected(file_key, index): アイテムが選択された。
        add_requested(file_key): 追加が要求された。
        remove_requested(file_key, index): 削除が要求された。
        reference_jumped(set_code): 参照ノードからジャンプ要求。
    """

    item_selected = Signal(str, int)
    add_requested = Signal(str)
    remove_requested = Signal(str, int)
    reference_jumped = Signal(str)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._domain_filter = ""  # "" = 全て
        self._data: dict[str, list[dict[str, Any]]] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(4)

        # ドメインフィルタ
        filter_row = QHBoxLayout()
        filter_row.setContentsMargins(4, 4, 4, 0)
        self._combo_domain = QComboBox()
        self._combo_domain.addItems(["全て", "WH", "TA"])
        self._combo_domain.setFixedHeight(28)
        self._combo_domain.currentTextChanged.connect(self._on_domain_changed)
        filter_row.addWidget(self._combo_domain)
        filter_row.addStretch()
        vl.addLayout(filter_row)

        # ツリー
        self._tree = QTreeWidget()
        self._tree.setHeaderHidden(True)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        self._tree.currentItemChanged.connect(self._on_current_changed)
        self._tree.itemDoubleClicked.connect(self._on_double_click)
        vl.addWidget(self._tree)

    def set_data(self, data: dict[str, list[dict[str, Any]]]) -> None:
        """ツリーにデータを設定する。"""
        self._data = data
        self._rebuild()

    def _rebuild(self) -> None:
        """ツリーを再構築する。"""
        self._tree.clear()

        # holder_groups → valid_holders参照付き
        self._build_holder_groups_node()
        # 残りの3ファイル
        self._build_flat_node("valid_holders")
        self._build_flat_node("valid_tests")
        self._build_flat_node("valid_samples")

        self._tree.expandAll()

    def _build_holder_groups_node(self) -> None:
        """Holder Groups ノードを構築する（参照子ノード付き）。"""
        items = self._data.get("holder_groups", [])
        holders = {h.get("set_code", ""): h for h in self._data.get("valid_holders", [])}

        root = QTreeWidgetItem(self._tree, ["Holder Groups"])
        root.setData(0, ROLE_FILE_KEY, "holder_groups")
        root.setData(0, ROLE_ITEM_INDEX, -1)
        font = root.font(0)
        font.setBold(True)
        root.setFont(0, font)

        for i, item in enumerate(items):
            code = item.get("holder_group_code", "")
            name = item.get("holder_group_name", "")
            active = item.get("is_active", True)
            label = f"{code}: {name}" if code else name or "(新規)"
            if not active:
                label += " [無効]"

            node = QTreeWidgetItem(root, [label])
            node.setData(0, ROLE_FILE_KEY, "holder_groups")
            node.setData(0, ROLE_ITEM_INDEX, i)
            node.setData(0, ROLE_IS_REFERENCE, False)

            if not active:
                node.setForeground(0, Qt.GlobalColor.gray)

            # 参照子ノード
            for ref_code in item.get("valid_holder_set_codes", []):
                holder = holders.get(ref_code)
                ref_label = f"→ {ref_code}"
                if holder:
                    ref_label += f": {holder.get('display_name', '')}"
                ref_node = QTreeWidgetItem(node, [ref_label])
                ref_node.setData(0, ROLE_FILE_KEY, "valid_holders")
                ref_node.setData(0, ROLE_ITEM_INDEX, -1)
                ref_node.setData(0, ROLE_IS_REFERENCE, True)
                ref_node.setData(0, ROLE_REF_SET_CODE, ref_code)
                ref_node.setForeground(0, Qt.GlobalColor.darkCyan)

    def _build_flat_node(self, file_key: str) -> None:
        """フラットなファイルノードを構築する。"""
        items = self._data.get(file_key, [])
        label = _FILE_LABELS.get(file_key, file_key)

        root = QTreeWidgetItem(self._tree, [label])
        root.setData(0, ROLE_FILE_KEY, file_key)
        root.setData(0, ROLE_ITEM_INDEX, -1)
        font = root.font(0)
        font.setBold(True)
        root.setFont(0, font)

        for i, item in enumerate(items):
            domain = item.get("domain_code", "")
            if self._domain_filter and domain != self._domain_filter:
                continue

            code = item.get("set_code", "")
            name = item.get("display_name", "")
            active = item.get("is_active", True)
            item_label = f"{code}: {name}" if code else name or "(新規)"
            if domain:
                item_label += f" [{domain}]"
            if not active:
                item_label += " [無効]"

            node = QTreeWidgetItem(root, [item_label])
            node.setData(0, ROLE_FILE_KEY, file_key)
            node.setData(0, ROLE_ITEM_INDEX, i)
            node.setData(0, ROLE_IS_REFERENCE, False)

            if not active:
                node.setForeground(0, Qt.GlobalColor.gray)

    def _on_domain_changed(self, text: str) -> None:
        self._domain_filter = "" if text == "全て" else text
        self._rebuild()

    def _on_current_changed(self, current: QTreeWidgetItem | None,
                            _prev: QTreeWidgetItem | None) -> None:
        if current is None:
            return
        is_ref = current.data(0, ROLE_IS_REFERENCE)
        if is_ref:
            return
        file_key = current.data(0, ROLE_FILE_KEY)
        index = current.data(0, ROLE_ITEM_INDEX)
        if file_key and index is not None and index >= 0:
            self.item_selected.emit(file_key, index)

    def _on_double_click(self, item: QTreeWidgetItem, _col: int) -> None:
        is_ref = item.data(0, ROLE_IS_REFERENCE)
        if is_ref:
            set_code = item.data(0, ROLE_REF_SET_CODE)
            if set_code:
                self.reference_jumped.emit(set_code)

    def _on_context_menu(self, pos) -> None:
        item = self._tree.itemAt(pos)
        if item is None:
            return

        file_key = item.data(0, ROLE_FILE_KEY)
        index = item.data(0, ROLE_ITEM_INDEX)
        is_ref = item.data(0, ROLE_IS_REFERENCE)
        if not file_key or is_ref:
            return

        menu = QMenu(self)
        act_add = menu.addAction("追加")
        act_del = None
        if index is not None and index >= 0:
            act_del = menu.addAction("削除")

        action = menu.exec(self._tree.viewport().mapToGlobal(pos))
        if action == act_add:
            self.add_requested.emit(file_key)
        elif act_del and action == act_del:
            self.remove_requested.emit(file_key, index)

    def select_by_set_code(self, file_key: str, set_code: str) -> None:
        """指定 file_key の set_code を持つアイテムを選択する。"""
        root = self._tree.invisibleRootItem()
        for i in range(root.childCount()):
            top = root.child(i)
            if top.data(0, ROLE_FILE_KEY) != file_key:
                continue
            for j in range(top.childCount()):
                child = top.child(j)
                idx = child.data(0, ROLE_ITEM_INDEX)
                if idx is not None and idx >= 0:
                    items = self._data.get(file_key, [])
                    if idx < len(items) and items[idx].get("set_code") == set_code:
                        self._tree.setCurrentItem(child)
                        return
