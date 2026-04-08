"""Holder Group 編集フォーム。"""
from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.code_list_widget import CodeListWidget


class HolderGroupEditor(QWidget):
    """Holder Group のフォームエディタ。

    Signals:
        data_changed: フィールドが変更された。
    """

    data_changed = Signal()

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._item: dict[str, Any] = {}
        self._setup_ui()

    def _setup_ui(self) -> None:
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        title = QLabel("Holder Group 編集")
        title.setStyleSheet("font-size: 15px; font-weight: 600; color: #333333; padding: 8px;")
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        content = QWidget()
        form = QFormLayout(content)
        form.setContentsMargins(12, 8, 12, 8)
        form.setSpacing(10)

        self._edit_code = QLineEdit()
        self._edit_code.editingFinished.connect(self.data_changed)
        form.addRow("グループコード", self._edit_code)

        self._edit_name = QLineEdit()
        self._edit_name.editingFinished.connect(self.data_changed)
        form.addRow("グループ名", self._edit_name)

        self._spin_order = QSpinBox()
        self._spin_order.setRange(0, 9999)
        self._spin_order.valueChanged.connect(lambda _: self.data_changed.emit())
        form.addRow("表示順", self._spin_order)

        self._check_active = QCheckBox("有効")
        self._check_active.toggled.connect(lambda _: self.data_changed.emit())
        form.addRow("", self._check_active)

        self._code_list = CodeListWidget("Valid Holder Set Code")
        self._code_list.changed.connect(self.data_changed)
        form.addRow("Valid Holder\nSet Codes", self._code_list)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def set_item(self, item: dict[str, Any]) -> None:
        """表示するアイテムを設定する。"""
        self._item = item
        self._edit_code.setText(item.get("holder_group_code", ""))
        self._edit_name.setText(item.get("holder_group_name", ""))
        self._spin_order.setValue(item.get("sort_order", 999))
        self._check_active.setChecked(item.get("is_active", True))
        self._code_list.set_codes(item.get("valid_holder_set_codes", []))

    def get_item(self) -> dict[str, Any]:
        """現在の編集内容を辞書で返す。"""
        return {
            "holder_group_code": self._edit_code.text().strip(),
            "holder_group_name": self._edit_name.text().strip(),
            "valid_holder_set_codes": self._code_list.get_codes(),
            "is_active": self._check_active.isChecked(),
            "sort_order": self._spin_order.value(),
        }
