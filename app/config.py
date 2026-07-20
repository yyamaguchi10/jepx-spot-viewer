"""アプリ全体で利用する設定値。"""

from __future__ import annotations

CURRENT_YEARS = (2025, 2026)
FISCAL_YEARS = tuple(range(2020, 2027))

CSV_URL_TEMPLATE = "http://www.jepx.jp/market/excel/spot_{year}.csv"
CSV_ENCODING = "Shift-JIS"

SOURCE_COLUMNS = [
    "年月日",
    "時刻コード",
    "システムプライス(円/kWh)",
    "エリアプライス北海道(円/kWh)",
    "エリアプライス東北(円/kWh)",
    "エリアプライス東京(円/kWh)",
    "エリアプライス中部(円/kWh)",
    "エリアプライス北陸(円/kWh)",
    "エリアプライス関西(円/kWh)",
    "エリアプライス中国(円/kWh)",
    "エリアプライス四国(円/kWh)",
    "エリアプライス九州(円/kWh)",
]

RENAME_COLUMNS = {
    "システムプライス(円/kWh)": "システムプライス",
    "エリアプライス北海道(円/kWh)": "北海道",
    "エリアプライス東北(円/kWh)": "東北",
    "エリアプライス東京(円/kWh)": "東京",
    "エリアプライス中部(円/kWh)": "中部",
    "エリアプライス北陸(円/kWh)": "北陸",
    "エリアプライス関西(円/kWh)": "関西",
    "エリアプライス中国(円/kWh)": "中国",
    "エリアプライス四国(円/kWh)": "四国",
    "エリアプライス九州(円/kWh)": "九州",
}

PRICE_COLUMNS = [
    "北海道",
    "東北",
    "東京",
    "中部",
    "北陸",
    "関西",
    "中国",
    "四国",
    "九州",
]

ALL_PRICE_COLUMNS = ["システムプライス", *PRICE_COLUMNS]

TIME_LABELS = [
    f"{hour}:{minute:02d}-"
    for hour in range(24)
    for minute in (0, 30)
]

LINE_SETTINGS = {
    "システムプライス": {
        "lw": 1,
        "ls": "dashed",
        "color": "red",
        "zorder": 1,
    },
    "北海道": {"lw": 1, "color": "green", "zorder": 1},
    "東北": {"lw": 1, "color": "brown", "zorder": 1},
    "東京": {"lw": 1.3, "color": "red", "zorder": 2},
    "中部": {"lw": 1, "color": "lime", "zorder": 1},
    "北陸": {"lw": 2, "color": "blue", "zorder": 3},
    "関西": {"lw": 1, "color": "orange", "zorder": 1},
    "中国": {"lw": 1, "color": "olive", "zorder": 1},
    "四国": {"lw": 1, "color": "pink", "zorder": 1},
    "九州": {"lw": 1, "color": "magenta", "zorder": 1},
}

FISCAL_YEAR_COLORS = {
    2026: "blue",
    2025: "orange",
    2024: "violet",
    2023: "skyblue",
    2022: "red",
    2021: "darkgreen",
    2020: "black",
}
