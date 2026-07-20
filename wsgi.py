"""Gunicorn用のWSGI入口。"""

from application import app

__all__ = ["app"]
