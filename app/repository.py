"""データ取得元を隠蔽するRepository層。"""

from __future__ import annotations

import pandas as pd

from .data_service import (
    load_fiscal_year_data,
    load_market_data,
)


def get_market_data() -> pd.DataFrame:
    """最新の市場価格データを取得する。"""
    return load_market_data()


def get_fiscal_year_data(year: int) -> pd.DataFrame:
    """指定年度の市場価格データを取得する。"""
    return load_fiscal_year_data(year)