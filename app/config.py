"""DataSchemaStudio アプリケーション設定。

パス解決: USERPROFILE → SYNC_ROOT → DATA_PATH → 各JSONファイル
ローカル設定: ~/.dataschema/settings.json
"""
import json
import os
import platform
from pathlib import Path

APP_VERSION = "1.0"

# ─── ユーザーローカル設定 ───────────────────────────────────────────────────
LOCAL_SETTINGS_DIR = Path.home() / ".dataschema"
LOCAL_SETTINGS_PATH = LOCAL_SETTINGS_DIR / "settings.json"

# ─── USERPROFILE ベースのパス導出 ─────────────────────────────────────────────
_SYNC_ROOT_SUFFIX = "トクヤマグループ"
_DATA_PATH_SUFFIX = os.path.join(
    "トクヤマグループ", "環境分析課 - ドキュメント", "app_data"
)

# ─── デフォルトJSONファイル名 ─────────────────────────────────────────────────
DEFAULT_FILE_NAMES: dict[str, str] = {
    "holder_groups": "holder_groups.json",
    "valid_holders": "valid_holders.json",
    "valid_tests": "valid_tests.json",
    "valid_samples": "valid_samples.json",
}


def _load_settings() -> dict:
    """ローカル設定ファイルを読み込む。"""
    if LOCAL_SETTINGS_PATH.exists():
        try:
            return json.loads(LOCAL_SETTINGS_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_settings(settings: dict) -> None:
    """ローカル設定ファイルを保存する。"""
    LOCAL_SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    LOCAL_SETTINGS_PATH.write_text(
        json.dumps(settings, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


# ── USERPROFILE ──────────────────────────────────────────────────────────────

def load_user_profile() -> Path | None:
    """ローカル設定から USERPROFILE を読み込む。未設定なら None。"""
    raw = _load_settings().get("user_profile_path", "")
    if raw:
        p = Path(raw)
        if p.exists() and p.is_dir():
            return p
    return None


def save_user_profile(path: Path) -> None:
    """USERPROFILE をローカル設定に保存する。"""
    settings = _load_settings()
    settings["user_profile_path"] = str(path)
    _save_settings(settings)


def _resolve_user_profile() -> Path:
    saved = load_user_profile()
    if saved is not None:
        return saved
    return Path.home()


USER_PROFILE = _resolve_user_profile()


def reload_user_profile(new_path: Path) -> None:
    """USERPROFILE と派生パスをすべて更新する。"""
    global USER_PROFILE
    USER_PROFILE = new_path
    reload_sync_root(new_path / _SYNC_ROOT_SUFFIX)
    reload_paths(new_path / _DATA_PATH_SUFFIX)


# ── DATA_PATH ────────────────────────────────────────────────────────────────

def load_data_path() -> Path | None:
    """ローカル設定から DATA_PATH を読み込む。"""
    up = load_user_profile()
    if up is not None:
        derived = up / _DATA_PATH_SUFFIX
        if derived.exists() and derived.is_dir():
            return derived
    raw = _load_settings().get("app_data_path", "")
    if raw:
        p = Path(raw)
        if p.exists() and p.is_dir():
            return p
    return None


def save_data_path(path: Path) -> None:
    """DATA_PATH をローカル設定に保存する。"""
    settings = _load_settings()
    settings["app_data_path"] = str(path)
    _save_settings(settings)


def _resolve_data_path() -> Path:
    saved = load_data_path()
    if saved is not None:
        return saved
    if platform.system() == "Windows":
        return Path.home() / _DATA_PATH_SUFFIX
    return Path.home() / "app_data"


DATA_PATH = _resolve_data_path()

DEFAULT_SOURCE_DIR = DATA_PATH / "_common" / "master_data" / "source"


def reload_paths(new_data_path: Path) -> None:
    """DATA_PATH と派生パスをモジュールレベルで更新する。"""
    global DATA_PATH, DEFAULT_SOURCE_DIR
    DATA_PATH = new_data_path
    DEFAULT_SOURCE_DIR = DATA_PATH / "_common" / "master_data" / "source"


# ── SYNC_ROOT ────────────────────────────────────────────────────────────────

def load_sync_root() -> Path | None:
    """USERPROFILE から同期ルートを導出する。"""
    up = load_user_profile()
    if up is not None:
        derived = up / _SYNC_ROOT_SUFFIX
        if derived.exists() and derived.is_dir():
            return derived
    raw = _load_settings().get("sync_root_path", "")
    if raw:
        p = Path(raw)
        if p.exists() and p.is_dir():
            return p
    return None


def save_sync_root(path: Path) -> None:
    """同期ルートをローカル設定に保存する。"""
    settings = _load_settings()
    settings["sync_root_path"] = str(path)
    _save_settings(settings)


def _resolve_sync_root() -> Path:
    saved = load_sync_root()
    if saved is not None:
        return saved
    if platform.system() == "Windows":
        return Path.home() / _SYNC_ROOT_SUFFIX
    return Path.home()


SYNC_ROOT = _resolve_sync_root()


def reload_sync_root(new_path: Path) -> None:
    """同期ルートをモジュールレベルで更新する。"""
    global SYNC_ROOT
    SYNC_ROOT = new_path


def get_sync_root() -> Path:
    """SharePoint 同期フォルダのルートを返す。"""
    return SYNC_ROOT


# ── 個別ファイルパス設定 ─────────────────────────────────────────────────────

def load_file_paths() -> dict[str, str]:
    """4ファイルの個別パス設定を読み込む。未設定のキーは含まない。"""
    return _load_settings().get("file_paths", {})


def save_file_paths(paths: dict[str, str]) -> None:
    """4ファイルの個別パス設定を保存する。"""
    settings = _load_settings()
    settings["file_paths"] = paths
    _save_settings(settings)


def get_file_path(file_key: str) -> Path:
    """指定キーのJSONファイルパスを返す。

    個別設定があればそれを使い、なければデフォルト（DEFAULT_SOURCE_DIR/ファイル名）。

    Args:
        file_key: "holder_groups", "valid_holders", "valid_tests", "valid_samples"

    Returns:
        JSONファイルの絶対パス。
    """
    custom = load_file_paths().get(file_key, "")
    if custom:
        return Path(custom)
    return DEFAULT_SOURCE_DIR / DEFAULT_FILE_NAMES[file_key]


# ── サイドバーページ ─────────────────────────────────────────────────────────

SIDEBAR_PAGES = [
    ("editor",   "≡", "エディタ"),
    ("settings", "✦", "設定"),
]
