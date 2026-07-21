"""グラフ取得方法を隠蔽するRepository層。"""

from __future__ import annotations

from collections.abc import Mapping

import pandas as pd

from .chart_service import (
    create_daily_chart,
    create_fiscal_comparison_chart,
    create_period_chart,
    create_single_fiscal_chart,
)


def get_daily_chart(
    data: pd.DataFrame,
    target_date: pd.Timestamp,
) -> str:
    """指定日の価格グラフを取得する。"""
    return create_daily_chart(
        data,
        target_date,
    )


def get_period_chart(
    data: pd.DataFrame,
    first_date: pd.Timestamp,
    latest_date: pd.Timestamp,
    days: int,
) -> str:
    """指定期間の価格グラフを取得する。"""
    return create_period_chart(
        data,
        first_date=first_date,
        latest_date=latest_date,
        days=days,
    )


def get_fiscal_comparison_chart(
    yearly_data: Mapping[int, pd.DataFrame],
) -> str:
    """複数年度の比較グラフを取得する。"""
    return create_fiscal_comparison_chart(
        dict(yearly_data),
    )


def get_single_fiscal_chart(
    year: int,
    data: pd.DataFrame,
) -> str:
    """指定年度の価格グラフを取得する。"""
    return create_single_fiscal_chart(
        year,
        data,
    )