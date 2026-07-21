"""JEPX CSVをダウンロードしてローカルへ保存する。"""

from __future__ import annotations

import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

import pandas as pd

from app.config import (
    CSV_ENCODING,
    CSV_FILE_TEMPLATE,
    CSV_URL_TEMPLATE,
    DATA_DIR,
    FISCAL_YEARS,
)


class DataUpdateError(RuntimeError):
    """JEPX CSVの更新に失敗した場合。"""


def _csv_url(year: int) -> str:
    """指定年のJEPX CSV URLを返す。"""
    return CSV_URL_TEMPLATE.format(year=year)


def _destination_path(year: int) -> Path:
    """指定年の保存先を返す。"""
    return DATA_DIR / CSV_FILE_TEMPLATE.format(year=year)


def _validate_csv(csv_path: Path, year: int) -> None:
    """保存前のCSVが読み込めることを確認する。"""
    try:
        data = pd.read_csv(
            csv_path,
            encoding=CSV_ENCODING,
            nrows=5,
        )
    except Exception as exc:
        raise DataUpdateError(
            f"{year}年のダウンロードデータをCSVとして読めません。"
        ) from exc

    if data.empty:
        raise DataUpdateError(
            f"{year}年のダウンロードデータが空です。"
        )

    if "年月日" not in data.columns:
        raise DataUpdateError(
            f"{year}年のCSVに「年月日」列がありません。"
        )


def download_year(year: int) -> Path:
    """指定年のCSVを安全に更新する。"""
    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    destination = _destination_path(year)
    temporary = destination.with_suffix(".csv.tmp")
    url = _csv_url(year)

    try:
        print(f"Downloading: {url}")

        with urlopen(url, timeout=60) as response:
            temporary.write_bytes(response.read())

        _validate_csv(
            temporary,
            year,
        )

        os.replace(
            temporary,
            destination,
        )

    except (HTTPError, URLError, TimeoutError) as exc:
        raise DataUpdateError(
            f"{year}年のJEPX CSVを取得できませんでした。"
        ) from exc
    except OSError as exc:
        raise DataUpdateError(
            f"{year}年のCSVを保存できませんでした。"
        ) from exc
    finally:
        if temporary.exists():
            temporary.unlink()

    print(f"Saved: {destination}")
    return destination


def update_all() -> None:
    """表示と年度比較に必要な全CSVを更新する。"""
    failed_years: list[int] = []

    for year in FISCAL_YEARS:
        try:
            download_year(year)
        except DataUpdateError as exc:
            failed_years.append(year)
            print(f"ERROR: {exc}")

    if failed_years:
        years = ", ".join(str(year) for year in failed_years)
        raise DataUpdateError(
            f"更新に失敗した年度: {years}"
        )

    print("All JEPX CSV files were updated successfully.")


if __name__ == "__main__":
    try:
        update_all()
    except DataUpdateError as exc:
        print(f"Update failed: {exc}")
        raise SystemExit(1) from exc