"""URLとテンプレートの対応だけを担当する。"""

from __future__ import annotations

import os

from flask import Blueprint, current_app, render_template, url_for

from .data_service import DataLoadError
from .view_service import (
    build_daily_context,
    build_fiscal_context,
    build_period_context,
    build_qr_context,
)

web = Blueprint("web", __name__)


@web.app_context_processor
def override_url_for():
    """staticファイルの更新時刻をURLに付けてブラウザキャッシュを更新する。"""
    return {"url_for": dated_url_for}


def dated_url_for(endpoint: str, **values):
    """旧テンプレートのendpoint名をBlueprint形式へ変換する。"""

    if endpoint == "static":
        filename = values.get("filename")
        if filename:
            file_path = os.path.join(
                current_app.static_folder or "",
                filename,
            )
            try:
                values["q"] = int(os.stat(file_path).st_mtime)
            except OSError:
                pass

        return url_for(endpoint, **values)

    # 既存テンプレートとの互換性を保つ
    if "." not in endpoint:
        endpoint = f"web.{endpoint}"

    return url_for(endpoint, **values)

@web.app_errorhandler(DataLoadError)
def handle_data_load_error(error: DataLoadError):
    current_app.logger.exception("JEPXデータの取得に失敗しました。")
    return (
        "価格データを取得できませんでした。しばらくしてから再度お試しください。",
        503,
    )


@web.route("/")
def index():
    return render_template(
        "index.html",
        **build_daily_context(offset_days=0),
    )


@web.route("/dayago1")
def dayago1():
    return render_template(
        "dayago1.html",
        **build_daily_context(offset_days=1),
    )


@web.route("/dayago2")
def dayago2():
    return render_template(
        "dayago2.html",
        **build_daily_context(offset_days=2),
    )


@web.route("/lastweek")
def lastweek():
    return render_template(
        "lastweek.html",
        **build_period_context(days=7),
    )


@web.route("/lastmonth")
def lastmonth():
    return render_template(
        "lastmonth.html",
        **build_period_context(days=30),
    )


@web.route("/QR")
def QR():
    return render_template(
        "QR.html",
        **build_qr_context(),
    )


@web.route("/FY2020to2023")
def FY2020to2023():
    return render_template(
        "FY2020to2023.html",
        **build_fiscal_context(),
    )
