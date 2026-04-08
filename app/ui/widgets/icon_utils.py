"""SVGアイコンのカラライズユーティリティ。

Qt リソース（resources_rc）から SVG を読み込み、
QPainter の SourceIn 合成モードで任意色に塗り替えた QIcon を返す。
"""
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

_ASSETS_DIR = Path(__file__).resolve().parents[3] / "resources" / "assets"


def get_icon(resource_path: str, color: str | QColor, size: int = 22) -> QIcon:
    """Qt リソースの SVG を指定色に塗り替えた QIcon を返す。

    Args:
        resource_path: Qt リソースパス (例: ``":/icons/home.svg"``)。
        color: 塗りつぶし色。文字列 (``"#3b82f6"``) または QColor。
        size: 正方形アイコンの一辺サイズ (px)。デフォルト 22。

    Returns:
        カラライズされた QIcon。
    """
    if isinstance(color, str):
        color = QColor(color)

    renderer = QSvgRenderer(resource_path)
    if not renderer.isValid():
        basename = resource_path.rsplit("/", 1)[-1]
        fallback = _ASSETS_DIR / basename
        if fallback.is_file():
            renderer = QSvgRenderer(str(fallback))
    if not renderer.isValid():
        return QIcon()

    pixmap = QPixmap(size, size)
    pixmap.fill(Qt.GlobalColor.transparent)

    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), color)
    painter.end()

    return QIcon(pixmap)
