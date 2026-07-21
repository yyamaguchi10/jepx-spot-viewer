"""JEPX CSVの取得元を隠蔽するRepository層。"""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd

from .config import CSV_ENCODING, CSV_URL_TEMPLATE


class SourceLoadError(RuntimeError):
    """元データの取得に失敗した場合。"""


def _csv_url(year: int) -> str:
    """指定年のJEPX CSV URLを返す。"""
    return CSV_URL_TEMPLATE.format(year=year)


def read_source_csv(
    year: int,
    usecols: Sequence[str],
) -> pd.DataFrame:
    """指定年のJEPX CSVを取得する。"""
    try:
        return pd.read_csv(
            _csv_url(year),
            encoding=CSV_ENCODING,
            usecols=list(usecols),
        )
    except Exception as exc:
        raise SourceLoadError(
            f"{year}年のJEPX CSVを取得できませんでした。"
        ) from exc