"""Matplotlibグラフを生成し、Base64文字列として返す。"""

from __future__ import annotations

import base64
import io
from typing import Mapping

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import japanize_matplotlib  # noqa: F401

from .config import (
    ALL_PRICE_COLUMNS,
    LINE_SETTINGS,
    get_fiscal_comparison_line_settings,
    get_single_fiscal_line_settings,
)


def _figure_to_base64(fig: plt.Figure) -> str:
    buffer = io.BytesIO()
    try:
        fig.savefig(buffer, format="png")
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode("ascii")
    finally:
        buffer.close()
        plt.close(fig)


def _plot_all_prices(ax: plt.Axes, data: pd.DataFrame, x_column: str) -> None:
    for column in ALL_PRICE_COLUMNS:
        settings = LINE_SETTINGS[column]
        ax.plot(
            data[x_column],
            data[column],
            label=column,
            **settings,
        )


def create_daily_chart(data: pd.DataFrame, target_date: object) -> str:
    fig, ax = plt.subplots(tight_layout=True)
    _plot_all_prices(ax, data, "時刻コード")

    ax.set_title(f"{target_date}  price", fontsize=18)
    ax.grid(True)
    ax.set_xlabel("Times of Day(48 frames)")
    ax.set_ylabel("Price (¥/kWh)")
    ax.set_xticks(range(0, 25, 2))
    ax.set_xlim(0, 24)
    ax.set_axisbelow(True)
    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=6,
        fontsize=9,
    )
    fig.subplots_adjust(bottom=0.2)
    return _figure_to_base64(fig)


def create_period_chart(
    data: pd.DataFrame,
    *,
    first_date: object,
    latest_date: object,
    days: int,
) -> str:
    fig, ax = plt.subplots(tight_layout=True)
    _plot_all_prices(ax, data, "No")

    title = f"{first_date}--->{latest_date}  price"
    ax.set_title(title, fontsize=15)
    ax.grid(which="major")
    ax.set_xlabel(
        "Last Week(7days)" if days == 7 else "Last Month(30days)"
    )
    ax.set_ylabel("Price (¥/kWh)")
    ax.set_axisbelow(True)

    if days == 7:
        major_ticks = list(range(0, 337, 48))
        minor_ticks = list(range(24, 313, 48))
        date_labels = [
            first_date + pd.Timedelta(days=i)
            for i in range(7)
        ]
        ax.set_xlim(0, 336)
        ax.set_xticks(major_ticks)
        ax.set_xticklabels([""] * len(major_ticks))
        ax.set_xticks(minor_ticks, minor=True)
        ax.set_xticklabels(
            date_labels,
            rotation="vertical",
            minor=True,
        )
    else:
        ax.set_xlim(0, 1441)
        offsets = [30, 25, 20, 15, 10, 5, 0]
        ax.set_xticks([0, 240, 480, 720, 960, 1200, 1440])
        ax.set_xticklabels(
            [
                latest_date - pd.Timedelta(days=offset)
                for offset in offsets
            ],
            rotation="vertical",
        )

    ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        ncol=6,
        fontsize=9,
    )
    fig.subplots_adjust(bottom=0.2)
    return _figure_to_base64(fig)


def _configure_fiscal_axis(ax: plt.Axes) -> None:
    major_ticks = [
        0, 1440, 2928, 4368, 5856, 7344, 8784,
        10272, 11712, 13200, 14688, 16032, 17520,
    ]
    minor_ticks = [
        720, 2184, 3648, 5112, 6600, 8064,
        9528, 10992, 12456, 13944, 15360, 16776,
    ]

    ax.grid(which="major")
    ax.set_xlabel(" Month(FY)")
    ax.set_ylabel("Price (¥/kWh)")
    ax.set_xlim(0, 17522)
    ax.set_xticks(major_ticks)
    ax.set_xticklabels([""] * len(major_ticks))
    ax.set_xticks(minor_ticks, minor=True)
    ax.set_xticklabels(
        ["4", "5", "6", "7", "8", "9", "10", "11", "12", "1", "2", "3"],
        minor=True,
    )
    ax.set_axisbelow(True)


def create_fiscal_comparison_chart(
    yearly_data: Mapping[int, pd.DataFrame],
) -> str:
    fig, ax = plt.subplots(tight_layout=True)

    for year in sorted(yearly_data, reverse=True):
        frame = yearly_data[year]
        ax.plot(
            frame["No"],
            frame["北陸"],
            label=f"FY{year}",
            **get_fiscal_comparison_line_settings(year),
        )

    first_year = min(yearly_data)
    last_year = max(yearly_data)

    ax.set_title(
        f"北陸  FY{first_year} -> FY{last_year}  price",
        fontsize=15,
    )

    _configure_fiscal_axis(ax)

    ax.legend(
        loc="upper left",
        fontsize=10,
        framealpha=1,
        labelcolor="linecolor",
    )

    return _figure_to_base64(fig)


def create_single_fiscal_chart(
    year: int,
    data: pd.DataFrame,
) -> str:
    fig, ax = plt.subplots(tight_layout=True)

    ax.plot(
        data["No"],
        data["北陸"],
        label=f"FY{year}",
        **get_single_fiscal_line_settings(year),
    )

    ax.set_title(
        f"北陸  FY{year}  price",
        fontsize=15,
    )

    _configure_fiscal_axis(ax)

    return _figure_to_base64(fig)
