"""Flaskアプリケーションの起動入口。

Gunicorn:
    gunicorn --workers 1 --threads 2 "application:app"

ローカル開発:
    python application.py
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
