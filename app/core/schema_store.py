"""4つのJSONファイルの読み書きを担当するデータアクセス層。

各ファイルは {"items": [...]} 形式で保存される。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from app import config


def _read_json(path: Path) -> list[dict[str, Any]]:
    """JSONファイルを読み込み items リストを返す。

    ファイルが存在しない場合は空リストを返す。
    """
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data.get("items", [])
    except (json.JSONDecodeError, OSError):
        return []


def _write_json(path: Path, items: list[dict[str, Any]]) -> None:
    """items リストを {"items": [...]} 形式でJSONファイルに保存する。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {"items": items}
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ── Holder Groups ────────────────────────────────────────────────────────────

def load_holder_groups() -> list[dict[str, Any]]:
    """holder_groups.json を読み込む。"""
    return _read_json(config.get_file_path("holder_groups"))


def save_holder_groups(items: list[dict[str, Any]]) -> None:
    """holder_groups.json を保存する。"""
    _write_json(config.get_file_path("holder_groups"), items)


# ── Valid Holders ────────────────────────────────────────────────────────────

def load_valid_holders() -> list[dict[str, Any]]:
    """valid_holders.json を読み込む。"""
    return _read_json(config.get_file_path("valid_holders"))


def save_valid_holders(items: list[dict[str, Any]]) -> None:
    """valid_holders.json を保存する。"""
    _write_json(config.get_file_path("valid_holders"), items)


# ── Valid Tests ──────────────────────────────────────────────────────────────

def load_valid_tests() -> list[dict[str, Any]]:
    """valid_tests.json を読み込む。"""
    return _read_json(config.get_file_path("valid_tests"))


def save_valid_tests(items: list[dict[str, Any]]) -> None:
    """valid_tests.json を保存する。"""
    _write_json(config.get_file_path("valid_tests"), items)


# ── Valid Samples ────────────────────────────────────────────────────────────

def load_valid_samples() -> list[dict[str, Any]]:
    """valid_samples.json を読み込む。"""
    return _read_json(config.get_file_path("valid_samples"))


def save_valid_samples(items: list[dict[str, Any]]) -> None:
    """valid_samples.json を保存する。"""
    _write_json(config.get_file_path("valid_samples"), items)
