"""テンプレートに渡す値を組み立てる。"""

from __future__ import annotations

from typing import Any

import pandas as pd

from .chart_service import (
    create_daily_chart,
    create_fiscal_comparison_chart,
    create_period_chart,
    create_single_fiscal_chart,
)
from .config import FISCAL_YEARS, PRICE_COLUMNS, TIME_LABELS
from .data_service import (
    get_date_information,
    get_day_data,
    get_recent_data,
)
from .repository import (
    get_fiscal_year_data,
    get_market_data,
)


def _format_number(value: float) -> str:
    return str(round(float(value), 2))


def _price_statistics(data: pd.DataFrame) -> dict[str, str]:
    prices = data[PRICE_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce",
    )
    return {
        "max": _format_number(prices.max().max()),
        "min": _format_number(prices.min().min()),
        "mean": _format_number(prices.mean().mean()),
        "hokuriku_max": _format_number(prices["北陸"].max()),
        "hokuriku_min": _format_number(prices["北陸"].min()),
        "hokuriku_mean": _format_number(prices["北陸"].mean()),
    }


def _common_dates(data: pd.DataFrame) -> dict[str, Any]:
    latest_date, day_ago1, day_ago2 = get_date_information(data)
    return {
        "latest_date": latest_date,
        "day_ago1": day_ago1,
        "day_ago2": day_ago2,
    }


def build_daily_context(offset_days: int) -> dict[str, Any]:
    """最新日、前日、前々日の画面用データを生成する。"""
    all_data = get_market_data()
    dates = _common_dates(all_data)
    target_date = dates["latest_date"] - pd.Timedelta(days=offset_days)
    day_data = get_day_data(all_data, target_date)

    if day_data.empty:
        raise ValueError(f"{target_date}のデータがありません。")

    stats = _price_statistics(day_data)

    table = day_data[PRICE_COLUMNS].copy()
    if len(table) == len(TIME_LABELS):
        table.index = TIME_LABELS

    image = create_daily_chart(day_data, target_date)

    suffix = "" if offset_days == 0 else str(offset_days)
    context = {
        **dates,
        f"img{suffix}": image,
        f"text_max{suffix}": stats["max"],
        f"text_min{suffix}": stats["min"],
        f"text_mean{suffix}": stats["mean"],
        f"text_max_riku{suffix}": stats["hokuriku_max"],
        f"text_min_riku{suffix}": stats["hokuriku_min"],
        f"text_mean_riku{suffix}": stats["hokuriku_mean"],
        f"today_prices{suffix}": table.to_html(
            classes="data",
            header=True,
        ),
    }

    # index.htmlだけは元コードの変数名がimg、today_prices。
    if offset_days == 0:
        context["img"] = context.pop("img")
        context["today_prices"] = context.pop("today_prices")

    return context


def build_period_context(days: int) -> dict[str, Any]:
    all_data = get_market_data()
    dates = _common_dates(all_data)
    latest_date = dates["latest_date"]
    first_date = latest_date - pd.Timedelta(days=days - 1)
    period_data = get_recent_data(
        all_data,
        latest_date=latest_date,
        days=days,
    )

    stats = _price_statistics(period_data)
    image = create_period_chart(
        period_data,
        first_date=first_date,
        latest_date=latest_date,
        days=days,
    )

    suffix = "3" if days == 7 else "4"
    return {
        **dates,
        f"img{suffix}": image,
        f"text_max{suffix}": stats["max"],
        f"text_min{suffix}": stats["min"],
        f"text_mean{suffix}": stats["mean"],
        f"text_max_riku{suffix}": stats["hokuriku_max"],
        f"text_min_riku{suffix}": stats["hokuriku_min"],
        f"text_mean_riku{suffix}": stats["hokuriku_mean"],
    }


def build_qr_context() -> dict[str, Any]:
    return _common_dates(get_market_data())


def _year_statistics(data: pd.DataFrame) -> dict[str, str]:
    return {
        "max": _format_number(data["北陸"].max()),
        "min": _format_number(data["北陸"].min()),
        "mean": _format_number(data["北陸"].mean()),
    }


def build_fiscal_context() -> dict[str, Any]:
    current_data = get_market_data()
    context: dict[str, Any] = _common_dates(current_data)

    yearly_data = {
        year: get_fiscal_year_data(year)
        for year in FISCAL_YEARS
    }

    context["img5"] = create_fiscal_comparison_chart(yearly_data)

    summary_rows: list[dict[str, str]] = []
    for year in sorted(FISCAL_YEARS, reverse=True):
        stats = _year_statistics(yearly_data[year])

        context[f"img{str(year)[-2:]}"] = create_single_fiscal_chart(
            year,
            yearly_data[year],
        )
        context[f"text_max{year}"] = stats["max"]
        context[f"text_min{year}"] = stats["min"]
        context[f"text_mean{year}"] = stats["mean"]

        summary_rows.append(
            {
                "年度": str(year),
                "最高": stats["max"],
                "最安": stats["min"],
                "平均": stats["mean"],
            }
        )

    summary = pd.DataFrame(summary_rows).set_index("年度")
    context["maxminmeandf"] = summary.to_html(
        classes="data",
        header=True,
    )
    return context
