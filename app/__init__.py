"""Flaskアプリケーションファクトリー。"""

from flask import Flask

from .routes import web


def create_app() -> Flask:
    """Flaskアプリを生成してBlueprintを登録する。"""
    app = Flask(
        __name__,
        static_folder="../static",
        template_folder="../templates",
    )
    app.register_blueprint(web)
    return app
