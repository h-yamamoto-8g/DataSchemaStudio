"""Valid Holder 編集フォーム。"""
from __future__ import annotations

from typing import Any, Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QLabel,
    QLineEdit,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from app.ui.widgets.code_list_widget import CodeListWidget


class ValidHolderEditor(QWidget):
    """Valid Holder のフォームエディタ。

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

        title = QLabel("Valid Holder 編集")
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
        form.addRow("セットコード", self._edit_code)

        self._edit_name = QLineEdit()
        self._edit_name.editingFinished.connect(self.data_changed)
        form.addRow("表示名", self._edit_name)

        self._combo_domain = QComboBox()
        self._combo_domain.addItems(["WH", "TA"])
        self._combo_domain.currentTextChanged.connect(lambda _: self.data_changed.emit())
        form.addRow("ドメイン", self._combo_domain)

        self._check_active = QCheckBox("有効")
        self._check_active.toggled.connect(lambda _: self.data_changed.emit())
        form.addRow("", self._check_active)

        self._code_list = CodeListWidget("ホルダコード")
        self._code_list.changed.connect(self.data_changed)
        form.addRow("Holder Codes", self._code_list)

        scroll.setWidget(content)
        outer.addWidget(scroll)

    def set_item(self, item: dict[str, Any]) -> None:
        self._item = item
        self._edit_code.setText(item.get("set_code", ""))
        self._edit_name.setText(item.get("display_name", ""))
        idx = self._combo_domain.findText(item.get("domain_code", "WH"))
        self._combo_domain.setCurrentIndex(max(0, idx))
        self._check_active.setChecked(item.get("is_active", True))
        self._code_list.set_codes(item.get("holder_codes", []))

    def get_item(self) -> dict[str, Any]:
        return {
            "set_code": self._edit_code.text().strip(),
            "display_name": self._edit_name.text().strip(),
            "domain_code": self._combo_domain.currentText(),
            "holder_codes": self._code_list.get_codes(),
            "is_active": self._check_active.isChecked(),
        }
