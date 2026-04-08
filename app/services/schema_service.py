"""スキーマデータのビジネスロジック層。

データの読み込み・保存・バリデーション・参照整合性チェックを提供する。
"""
from __future__ import annotations

from typing import Any

from app.core import schema_store


class SchemaService:
    """4ファイルのスキーマデータを一括管理するサービス。"""

    def __init__(self) -> None:
        self._holder_groups: list[dict[str, Any]] = []
        self._valid_holders: list[dict[str, Any]] = []
        self._valid_tests: list[dict[str, Any]] = []
        self._valid_samples: list[dict[str, Any]] = []
        self._dirty: set[str] = set()

    # ── ロード ────────────────────────────────────────────────────────────

    def load_all(self) -> None:
        """4ファイルをすべて読み込む。"""
        self._holder_groups = schema_store.load_holder_groups()
        self._valid_holders = schema_store.load_valid_holders()
        self._valid_tests = schema_store.load_valid_tests()
        self._valid_samples = schema_store.load_valid_samples()
        self._dirty.clear()

    # ── プロパティ ────────────────────────────────────────────────────────

    @property
    def holder_groups(self) -> list[dict[str, Any]]:
        return self._holder_groups

    @property
    def valid_holders(self) -> list[dict[str, Any]]:
        return self._valid_holders

    @property
    def valid_tests(self) -> list[dict[str, Any]]:
        return self._valid_tests

    @property
    def valid_samples(self) -> list[dict[str, Any]]:
        return self._valid_samples

    @property
    def is_dirty(self) -> bool:
        return len(self._dirty) > 0

    # ── 保存 ─────────────────────────────────────────────────────────────

    def save_all(self) -> None:
        """変更のあるファイルのみ保存する。"""
        if "holder_groups" in self._dirty:
            schema_store.save_holder_groups(self._holder_groups)
        if "valid_holders" in self._dirty:
            schema_store.save_valid_holders(self._valid_holders)
        if "valid_tests" in self._dirty:
            schema_store.save_valid_tests(self._valid_tests)
        if "valid_samples" in self._dirty:
            schema_store.save_valid_samples(self._valid_samples)
        self._dirty.clear()

    # ── データ取得ヘルパー ────────────────────────────────────────────────

    def get_list(self, file_key: str) -> list[dict[str, Any]]:
        """file_key に対応するデータリストを返す。"""
        mapping = {
            "holder_groups": self._holder_groups,
            "valid_holders": self._valid_holders,
            "valid_tests": self._valid_tests,
            "valid_samples": self._valid_samples,
        }
        return mapping[file_key]

    def get_valid_holder_set_codes(self) -> list[str]:
        """valid_holders の全 set_code を返す（holder_groups 編集時のコンボ用）。"""
        return [h.get("set_code", "") for h in self._valid_holders if h.get("set_code")]

    # ── CRUD ─────────────────────────────────────────────────────────────

    def add_item(self, file_key: str, item: dict[str, Any]) -> None:
        """指定ファイルにアイテムを追加する。"""
        self.get_list(file_key).append(item)
        self._dirty.add(file_key)

    def remove_item(self, file_key: str, index: int) -> None:
        """指定ファイルからインデックスでアイテムを削除する。"""
        items = self.get_list(file_key)
        if 0 <= index < len(items):
            items.pop(index)
            self._dirty.add(file_key)

    def update_item(self, file_key: str, index: int, item: dict[str, Any]) -> None:
        """指定ファイルのアイテムを更新する。"""
        items = self.get_list(file_key)
        if 0 <= index < len(items):
            items[index] = item
            self._dirty.add(file_key)

    def mark_dirty(self, file_key: str) -> None:
        """指定ファイルを変更済みとしてマークする。"""
        self._dirty.add(file_key)

    # ── バリデーション ────────────────────────────────────────────────────

    def validate_references(self) -> list[str]:
        """holder_groups → valid_holders の参照整合性をチェックする。

        Returns:
            エラーメッセージのリスト。問題なければ空。
        """
        valid_set_codes = {h.get("set_code", "") for h in self._valid_holders}
        errors: list[str] = []

        for group in self._holder_groups:
            code = group.get("holder_group_code", "?")
            refs = group.get("valid_holder_set_codes", [])
            for ref in refs:
                if ref not in valid_set_codes:
                    errors.append(
                        f"Holder Group '{code}' が参照する '{ref}' は "
                        f"valid_holders に存在しません"
                    )

        return errors

    # ── 新規アイテムテンプレート ──────────────────────────────────────────

    @staticmethod
    def new_holder_group() -> dict[str, Any]:
        """新規 Holder Group のテンプレートを返す。"""
        return {
            "holder_group_code": "",
            "holder_group_name": "",
            "valid_holder_set_codes": [],
            "is_active": True,
            "sort_order": 999,
        }

    @staticmethod
    def new_valid_holder() -> dict[str, Any]:
        """新規 Valid Holder のテンプレートを返す。"""
        return {
            "set_code": "",
            "display_name": "",
            "domain_code": "WH",
            "holder_codes": [],
            "is_active": True,
        }

    @staticmethod
    def new_valid_test() -> dict[str, Any]:
        """新規 Valid Test のテンプレートを返す。"""
        return {
            "set_code": "",
            "display_name": "",
            "domain_code": "WH",
            "trend_enabled": True,
            "report_enabled": True,
            "test_codes": [],
        }

    @staticmethod
    def new_valid_sample() -> dict[str, Any]:
        """新規 Valid Sample のテンプレートを返す。"""
        return {
            "set_code": "",
            "display_name": "",
            "domain_code": "WH",
            "sample_codes": [],
            "is_active": True,
        }
