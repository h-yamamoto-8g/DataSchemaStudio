"""コード一覧の編集ウィジェット（リスト + 追加/削除ボタン）。

holder_codes, test_codes, sample_codes, valid_holder_set_codes などの
配列フィールド編集に汎用的に使用する。
"""
from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class CodeListWidget(QWidget):
    """文字列リストを編集するウィジェット。

    Signals:
        changed: リストの内容が変更された。
    """

    changed = Signal()

    def __init__(self, label: str = "コード一覧",
                 parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._setup_ui(label)

    def _setup_ui(self, label: str) -> None:
        vl = QVBoxLayout(self)
        vl.setContentsMargins(0, 0, 0, 0)
        vl.setSpacing(4)

        self._list = QListWidget()
        self._list.setMaximumHeight(150)
        vl.addWidget(self._list)

        row = QHBoxLayout()
        row.setSpacing(4)
        self._input = QLineEdit()
        self._input.setPlaceholderText(f"{label}を入力")
        self._input.returnPressed.connect(self._add)
        row.addWidget(self._input)

        btn_add = QPushButton("追加")
        btn_add.setFixedWidth(60)
        btn_add.clicked.connect(self._add)
        row.addWidget(btn_add)

        btn_del = QPushButton("削除")
        btn_del.setFixedWidth(60)
        btn_del.clicked.connect(self._remove)
        row.addWidget(btn_del)

        vl.addLayout(row)

    def _add(self) -> None:
        text = self._input.text().strip()
        if text:
            self._list.addItem(text)
            self._input.clear()
            self.changed.emit()

    def _remove(self) -> None:
        row = self._list.currentRow()
        if row >= 0:
            self._list.takeItem(row)
            self.changed.emit()

    def get_codes(self) -> list[str]:
        """現在のコード一覧を返す。"""
        return [self._list.item(i).text() for i in range(self._list.count())]

    def set_codes(self, codes: list[str]) -> None:
        """コード一覧を設定する。"""
        self._list.clear()
        for code in codes:
            self._list.addItem(code)
