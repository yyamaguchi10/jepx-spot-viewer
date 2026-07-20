# Step1-1 リファクタリング案

## 配置

既存の `templates/` と `static/` はそのまま利用します。

```text
YAMA15(SAKURA)/
├── app/
│   ├── __init__.py
│   ├── chart_service.py
│   ├── config.py
│   ├── data_service.py
│   ├── routes.py
│   └── view_service.py
├── static/                 # 既存フォルダー
├── templates/              # 既存フォルダー
├── application.py
├── wsgi.py
└── requirements.txt
```

## ローカル実行

```bash
python application.py
```

## Gunicorn

```bash
gunicorn --workers 1 --threads 2 --bind 127.0.0.1:8000 "application:app"
```

## 主な変更

- `application.py` は起動処理だけ（10行程度）
- URL処理は `routes.py`
- CSV取得と整形は `data_service.py`
- Matplotlib処理は `chart_service.py`
- テンプレート用データは `view_service.py`
- 現在年のCSVは30分メモリキャッシュ
- `plt.close(fig)` を必ず実行し、メモリ解放漏れを防止
- 既存テンプレートの変数名を維持

## 注意

Step1-1では現行画面との互換性を優先し、
画像は引き続きBase64でテンプレートに渡します。
次の段階で、画像の事前生成とオブジェクトストレージ保存へ変更します。
