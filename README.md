# JEPX Spot Price Viewer

JEPX（日本卸電力取引所）のスポット市場価格を、日別・週別・月別・年度別に表示するFlaskアプリケーションです。

ローカルCSVファイルを読み込み、価格統計とグラフをWeb画面に表示します。

## 主な機能

- 最新日のスポット価格表示
- 1日前、2日前の価格表示
- 直近1週間の価格表示
- 直近1か月の価格表示
- 年度別の価格統計表示
- 全国価格と北陸エリア価格の比較
- CSVデータの更新

## 動作環境

現在、以下の環境で動作確認しています。

- Python 3.9.6
- Flask 2.1.3
- pandas 1.5.2
- matplotlib 3.6.2
- gunicorn 23.0.0

## プロジェクト構成

```text
.
├── app/
│   ├── __init__.py
│   ├── chart_repository.py
│   ├── chart_service.py
│   ├── config.py
│   ├── data_service.py
│   ├── models.py
│   ├── repository.py
│   ├── routes.py
│   ├── source_repository.py
│   └── view_service.py
├── data/
│   └── .gitkeep
├── static/
│   ├── img/
│   └── style.css
├── templates/
├── application.py
├── requirements.txt
├── update_data.py
└── wsgi.py
 
```markdown
## セットアップ

### 1. リポジトリを取得

```bash
git clone https://github.com/yyamaguchi10/jepx-spot-viewer.git
cd jepx-spot-viewer