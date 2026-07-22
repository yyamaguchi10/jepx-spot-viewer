"""アプリケーション内で受け渡すデータモデル。"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class DateInformation:
    """画面表示で使用する基準日情報。"""

    latest_date: date
    day_ago1: date
    day_ago2: date


@dataclass(frozen=True)
class PriceStatistics:
    """市場価格の統計情報。"""

    maximum: str
    minimum: str
    mean: str
    hokuriku_maximum: str
    hokuriku_minimum: str
    hokuriku_mean: str


@dataclass(frozen=True)
class FiscalYearStatistics:
    """単年度の北陸価格統計。"""

    year: int
    maximum: str
    minimum: str
    mean: str