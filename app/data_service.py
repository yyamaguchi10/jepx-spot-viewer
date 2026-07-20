"""JEPX CSVの取得・整形を担当するモジュール。

Step1-1では、保存先を変えずに重複コードを除去します。
次の段階で、このモジュール内部だけを
オブジェクトストレージ／PostgreSQL参照へ置き換えられます。
"""

from __future__ import annotations

from threading import Lock
from time import monotonic

import pandas as pd

from .config import (
    ALL_PRICE_COLUMNS,
    CSV_ENCODING,
    CSV_URL_TEMPLATE,
    CURRENT_YEARS,
    RENAME_COLUMNS,
    SOURCE_COLUMNS,
)

_CACHE_TTL_SECONDS = 30 * 60
_cache_lock = Lock()
_cache_data: pd.DataFrame | None = None
_cache_created_at = 0.0

_fiscal_cache: dict[int, tuple[float, pd.DataFrame]] = {}


class DataLoadError(RuntimeError):
    """JEPXデータの取得・変換に失敗した場合。"""


def _csv_url(year: int) -> str:
    return CSV_URL_TEMPLATE.format(year=year)


def _read_year(year: int, usecols: list[str]) -> pd.DataFrame:
    try:
        return pd.read_csv(
            _csv_url(year),
            encoding=CSV_ENCODING,
            usecols=usecols,
        )
    except Exception as exc:
        raise DataLoadError(
            f"{year}年のJEPX CSVを取得できませんでした。"
        ) from exc


def _normalize_market_data(data: pd.DataFrame) -> pd.DataFrame:
    normalized = data.copy()
    normalized["年月日"] = pd.to_datetime(
        normalized["年月日"],
        errors="raise",
    ).dt.date

    normalized = normalized.rename(columns=RENAME_COLUMNS)

    normalized["時刻コード"] = pd.to_numeric(
        normalized["時刻コード"],
        errors="raise",
    )
    normalized["時刻コード"] = normalized["時刻コード"] / 2 - 0.5

    normalized[ALL_PRICE_COLUMNS] = normalized[
        ALL_PRICE_COLUMNS
    ].apply(pd.to_numeric, errors="coerce")

    normalized = normalized.sort_values(
        ["年月日", "時刻コード"]
    ).reset_index(drop=True)

    return normalized


def load_market_data(*, force_refresh: bool = False) -> pd.DataFrame:
    """現在表示に必要な年次CSVを読み込み、30分間メモリキャッシュする。"""
    global _cache_data, _cache_created_at

    now = monotonic()

    with _cache_lock:
        cache_valid = (
            _cache_data is not None
            and now - _cache_created_at < _CACHE_TTL_SECONDS
        )
        if cache_valid and not force_refresh:
            return _cache_data.copy()

        frames = [
            _read_year(year, SOURCE_COLUMNS)
            for year in CURRENT_YEARS
        ]
        data = _normalize_market_data(
            pd.concat(frames, ignore_index=True)
        )

        if data.empty:
            raise DataLoadError("JEPX CSVにデータがありません。")

        _cache_data = data
        _cache_created_at = now
        return data.copy()


def load_fiscal_year_data(
    year: int,
    *,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """年度比較用に、指定年の北陸価格だけを取得する。"""
    now = monotonic()

    with _cache_lock:
        cached = _fiscal_cache.get(year)
        if (
            cached is not None
            and now - cached[0] < _CACHE_TTL_SECONDS
            and not force_refresh
        ):
            return cached[1].copy()

        data = _read_year(
            year,
            ["年月日", "エリアプライス北陸(円/kWh)"],
        )
        data["年月日"] = pd.to_datetime(
            data["年月日"],
            errors="raise",
        ).dt.date
        data = data.rename(
            columns={"エリアプライス北陸(円/kWh)": "北陸"}
        )
        data["北陸"] = pd.to_numeric(
            data["北陸"],
            errors="coerce",
        )
        data = data.dropna(subset=["北陸"]).reset_index(drop=True)
        data["No"] = range(1, len(data) + 1)

        _fiscal_cache[year] = (now, data)
        return data.copy()


def get_date_information(
    data: pd.DataFrame,
) -> tuple[object, object, object]:
    """最新日・1日前・2日前を返す。"""
    latest_date = data["年月日"].max()
    day_ago1 = latest_date - pd.Timedelta(days=1)
    day_ago2 = latest_date - pd.Timedelta(days=2)
    return latest_date, day_ago1, day_ago2


def get_day_data(
    data: pd.DataFrame,
    target_date: object,
) -> pd.DataFrame:
    """指定日だけを抽出する。"""
    return data.loc[data["年月日"] == target_date].copy()


def get_recent_data(
    data: pd.DataFrame,
    *,
    latest_date: object,
    days: int,
) -> pd.DataFrame:
    """最新日を含む指定日数分を抽出し、連番列Noを付ける。"""
    first_date = latest_date - pd.Timedelta(days=days - 1)
    selected = data.loc[
        (data["年月日"] >= first_date)
        & (data["年月日"] <= latest_date)
    ].copy()
    selected["No"] = range(1, len(selected) + 1)
    return selected
