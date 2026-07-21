"""ローカルCSVの取得元を隠蔽するRepository層。"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pandas as pd

from .config import (
    CSV_ENCODING,
    CSV_FILE_TEMPLATE,
    DATA_DIR,
)


class SourceLoadError(RuntimeError):
    """元データの取得に失敗した場合。"""


def get_source_path(year: int) -> Path:
    """指定年のローカルCSVパスを返す。"""
    return DATA_DIR / CSV_FILE_TEMPLATE.format(year=year)


def read_source_csv(
    year: int,
    usecols: Sequence[str],
) -> pd.DataFrame:
    """指定年のローカルCSVを読み込む。"""
    csv_path = get_source_path(year)

    if not csv_path.exists():
        raise SourceLoadError(
            f"{year}年のローカルCSVがありません。"
            "先に python3 update_data.py を実行してください。"
        )

    try:
        return pd.read_csv(
            csv_path,
            encoding=CSV_ENCODING,
            usecols=list(usecols),
        )
    except Exception as exc:
        raise SourceLoadError(
            f"{year}年のローカルCSVを読み込めませんでした: "
            f"{csv_path}"
        ) from exc