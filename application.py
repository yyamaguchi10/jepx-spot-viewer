from flask import Flask,render_template,url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
#pyplotがimportされる前に[matplotlib.use('Agg')]でグラフ表示可能に
import matplotlib.pyplot as plt
import base64
import os
import io

#flaskアプリ作成時に冒頭で記載するコード
app = Flask(__name__,static_folder='./static')

#@app.context_processorはテンプレートで共通で使いたい変数や関数を定義
@app.context_processor
#以下は開発中にブラウザ画面が更新されない状態を解決するため
def override_url_for():
    return dict(url_for=dated_url_for)
def dated_url_for(endpoint, **values):
    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path,
                                endpoint, filename)
            values['q'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)

#最初のページ / が表示された際の処理
@app.route("/")
def index():
    #Matplotlibで描画領域Figureオブジェクトを作成(定番の書き方)
    fig = plt.figure()
    # jepxホームページからCSVデータを読み込む usecolsで指定の列のみ
    data = pd.read_csv('http://www.jepx.jp/market/excel/spot_2022.csv',encoding="Shift-JIS",usecols=['年月日','時刻コード','システムプライス(円/kWh)','エリアプライス北海道(円/kWh)','エリアプライス東北(円/kWh)','エリアプライス東京(円/kWh)','エリアプライス中部(円/kWh)','エリアプライス北陸(円/kWh)','エリアプライス関西(円/kWh)','エリアプライス中国(円/kWh)','エリアプライス四国(円/kWh)','エリアプライス九州(円/kWh)'])
    #年月日データを日付データ型に変換
    data['年月日'] = pd.to_datetime(data['年月日']).dt.date
    #時刻コードを数値型(float 小数点型）に変換し、48コマを÷2−0.5で0時開始の24時間に
    data['時刻コード'] = data['時刻コード'].astype(float)
    data['時刻コード'] = data['時刻コード']/2-0.5
    #matplotlibでは日本語が文字化けするので列名を変換
    #日本語対応策はあるが安全のため使用せず
    data = data.rename(columns={'システムプライス(円/kWh)': 'System_Price', 'エリアプライス北海道(円/kWh)': 'Hokkaido', 'エリアプライス東北(円/kWh)': 'Tohoku', 'エリアプライス東京(円/kWh)': 'Tokyo', 'エリアプライス中部(円/kWh)': 'Chubu', 'エリアプライス北陸(円/kWh)': 'Hokuriku', 'エリアプライス関西(円/kWh)': 'Kansai', 'エリアプライス中国(円/kWh)': 'Chugoku', 'エリアプライス四国(円/kWh)': 'Sikoku', 'エリアプライス九州(円/kWh)': 'Kyushu'})

    #各データを数値型(float 小数点型）に変換
    data['System_Price'] = data['System_Price'].astype(float)
    data['Hokkaido'] = data['Hokkaido'].astype(float)
    data['Tohoku'] = data['Tohoku'].astype(float)
    data['Tokyo'] = data['Tokyo'].astype(float)
    data['Chubu'] = data['Chubu'].astype(float)
    data['Hokuriku'] = data['Hokuriku'].astype(float)
    data['Kansai'] = data['Kansai'].astype(float)
    data['Chugoku'] = data['Chugoku'].astype(float)
    data['Sikoku'] = data['Sikoku'].astype(float)
    data['Kyushu'] = data['Kyushu'].astype(float)

    # メモ 現在の日付を取得し、昨日や明日のデータを取得する場合
    #today = pd.to_datetime('today').date()
    #yesterday = (today - pd.Timedelta(days=1))
    #tomorrow = (today + pd.Timedelta(days=1))

    #年月日の一番下（最新）の日付を取得
    latest_date = data.tail(1).iloc[0]['年月日']
    #最新日からの前日,前々日の日付を取得
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))
    ################################
    # 最新日latest_dateのグラフ作成
    # 最新日latest_dateのデータ（48コマ）だけをdataに代入
    data = data[data['年月日'] == latest_date]

    # 現在の日付に一致する行だけを選択する場合
    # data = data[data['年月日'] == today]

    # 列名からグラフに使う x軸,y軸 データを選択する
    x = data['時刻コード']
    y_sys = data['System_Price']
    y_hok = data['Hokkaido']
    y_toh = data['Tohoku']
    y_tok = data['Tokyo']
    y_chu = data['Chubu']
    y_riku = data['Hokuriku']
    y_kan = data['Kansai']
    y_chg = data['Chugoku']
    y_sik = data['Sikoku']
    y_kyu = data['Kyushu']
    # グラフを描く  tight_layout=Trueはグラフサイズ自動調整
    fig, ax = plt.subplots(tight_layout=True)

    # 同じグラフに折れ線グラフを複数作成
    # ax.plotでx,yを指定
    # lwは線の太さ、ls=dashedで点線に、colorで色指定、zorderで数値の大きい線が前に、labelは凡例表示に使う文字を指定
    ax.plot(x, y_sys, lw = 1,ls="dashed",color="red", zorder=1, label = "System_Price")
    ax.plot(x, y_hok, lw = 1,color="green", zorder=1, label = "Hokkaido")
    ax.plot(x, y_toh, lw = 1,color="brown", zorder=1, label = "Tohoku")
    ax.plot(x, y_tok, lw = 1.3,color="red", zorder=2, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=3,label = "Hokuriku")
    ax.plot(x, y_kan, lw = 1,color="orange", zorder=1, label = "Kansai")
    ax.plot(x, y_chg, lw = 1,color="olive", zorder=1, label = "Chugoku")
    ax.plot(x, y_sik, lw = 1,color="pink", zorder=1, label = "Sikoku")
    ax.plot(x, y_kyu, lw = 1,color="magenta", zorder=1, label = "Kyushu")

    # グラフタイトルに使う文字を変数title_nameに代入
    # 日付データの変数latest_dateをstr関数で文字データ化
    title_name = str(latest_date) + "  price"
    # グラフタイトルをセット。フォントサイズ指定可
    ax.set_title(title_name,fontsize=18)
    # グリッド表示
    ax.grid(True)
    # x軸ラベル名を指定
    ax.set_xlabel("Times of Day(48 frames)")
    # y軸ラベル名を指定
    ax.set_ylabel("Price (¥/kWh)")
    # x軸のメモリ幅を0から24+1(24時間表示に見えるように)、２ずつ目盛表示
    plt.xticks(range(0, 24+1, 2))
    ax.set_xlim(0, 24)
    # グリッド線が折れ線の後ろに（折れ線を前に表示するため）
    ax.set_axisbelow(True)

    # グラフ上に北陸の数値y_rikuを表示する  xytext=(+1, +3)で少しずらして表記し見やすく
    for i, j in zip(x, y_riku):
        ax.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
            textcoords='offset points', fontsize=5)

    # 凡例を表示
    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

    # 変数newdayを宣言
    global newday
    # グラフ画像を変数newdayに代入
    newday = io.BytesIO()
    # png画像に変換
    fig.savefig(newday, format="png")
    newday.seek(0)
    # 変数imgに代入
    img = base64.b64encode(newday.read()).decode()

    ###全国と北陸の最大最小値平均を取り出す
    # 全国変数text_max（最大）,text_min（最小）,tezt_mean（平均）に空のデータを入れておく
    # 北陸変数text_max_riku（最大）,text_min_riku（最小）,tezt_mean_riku（平均）に空のデータを入れておく
    text_max = ""
    text_min = ""
    text_mean = ""
    text_max_riku = ""
    text_min_riku = ""
    text_mean_riku = ""

    # 最大最小平均を抽出する列名を変数price_columnsに代入
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    # データのうち日付データ等を除くエリアデータのみ変数today_pricesに代入
    today_prices = data[price_columns]

    # 全体の最大値を取り出す際は.max().max()
    max_price = today_prices.max().max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_maxに代入
    text_max = str(round(max_price,2))

    # 全体の最小値を取り出す際は.min().min()
    min_price = today_prices.min().min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_minに代入
    text_min = str(round(min_price,2))

    # 全体の平均を取り出す際は.mean().mean()
    mean_price = today_prices.mean().mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_meanに代入
    text_mean = str(round(mean_price,2))

    # 北陸の最大値を取り出す際は.max()
    max_price_riku = today_prices['Hokuriku'].max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max_rikuに代入
    text_max_riku = str(round(max_price_riku,2))

    # 北陸の最小値を取り出す際は.min()
    min_price_riku = today_prices['Hokuriku'].min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min_rikuに代入
    text_min_riku = str(round(min_price_riku,2))

    # 北陸の平均を取り出す際は.mean()
    mean_price_riku = today_prices['Hokuriku'].mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean_rikuに代入
    text_mean_riku = str(round(mean_price_riku,2))

    # indexを48コマに変更する
    today_prices.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)
    # グラフ等のデータをindex.htmlテンプレートに渡す
    return render_template('index.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img=img,text_max=text_max,text_min=text_min,text_mean=text_mean,text_max_riku=text_max_riku,text_min_riku=text_min_riku,text_mean_riku=text_mean_riku,today_prices=today_prices.to_html(classes='data', header="true"))

@app.route("/dayago1")
def dayago1():
    fig1 = plt.figure()
    # CSVデータを読み込む
    data = pd.read_csv('http://www.jepx.jp/market/excel/spot_2022.csv',encoding="Shift-JIS",usecols=['年月日','時刻コード','システムプライス(円/kWh)','エリアプライス北海道(円/kWh)','エリアプライス東北(円/kWh)','エリアプライス東京(円/kWh)','エリアプライス中部(円/kWh)','エリアプライス北陸(円/kWh)','エリアプライス関西(円/kWh)','エリアプライス中国(円/kWh)','エリアプライス四国(円/kWh)','エリアプライス九州(円/kWh)'])
    data['年月日'] = pd.to_datetime(data['年月日']).dt.date
    data['時刻コード'] = data['時刻コード'].astype(float)
    data['時刻コード'] = data['時刻コード']/2-0.5
    data = data.rename(columns={'システムプライス(円/kWh)': 'System_Price', 'エリアプライス北海道(円/kWh)': 'Hokkaido', 'エリアプライス東北(円/kWh)': 'Tohoku', 'エリアプライス東京(円/kWh)': 'Tokyo', 'エリアプライス中部(円/kWh)': 'Chubu', 'エリアプライス北陸(円/kWh)': 'Hokuriku', 'エリアプライス関西(円/kWh)': 'Kansai', 'エリアプライス中国(円/kWh)': 'Chugoku', 'エリアプライス四国(円/kWh)': 'Sikoku', 'エリアプライス九州(円/kWh)': 'Kyushu'})

    data['System_Price'] = data['System_Price'].astype(float)
    data['Hokkaido'] = data['Hokkaido'].astype(float)
    data['Tohoku'] = data['Tohoku'].astype(float)
    data['Tokyo'] = data['Tokyo'].astype(float)
    data['Chubu'] = data['Chubu'].astype(float)
    data['Hokuriku'] = data['Hokuriku'].astype(float)
    data['Kansai'] = data['Kansai'].astype(float)
    data['Chugoku'] = data['Chugoku'].astype(float)
    data['Sikoku'] = data['Sikoku'].astype(float)
    data['Kyushu'] = data['Kyushu'].astype(float)

    # 現在の日付を取得し、明日のデータを取得
    #today = pd.to_datetime('today').date()
    #yesterday = (today - pd.Timedelta(days=1))
    #tomorrow = (today + pd.Timedelta(days=1))
    latest_date = data.tail(1).iloc[0]['年月日']
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))

    data = data[data['年月日'] == day_ago1]

    # 現在の日付に一致する行だけを選択する場合
    # data = data[data['年月日'] == today]

    # 列名から必要なデータを選択する
    x = data['時刻コード']
    y_sys = data['System_Price']
    y_hok = data['Hokkaido']
    y_toh = data['Tohoku']
    y_tok = data['Tokyo']
    y_chu = data['Chubu']
    y_riku = data['Hokuriku']
    y_kan = data['Kansai']
    y_chg = data['Chugoku']
    y_sik = data['Sikoku']
    y_kyu = data['Kyushu']

    fig1, ax1 = plt.subplots(tight_layout=True)

    ax1.plot(x, y_sys, lw = 1,ls="dashed",color="red", zorder=1, label = "System_Price")
    ax1.plot(x, y_hok, lw = 1,color="green", zorder=1, label = "Hokkaido")
    ax1.plot(x, y_toh, lw = 1,color="brown", zorder=1, label = "Tohoku")
    ax1.plot(x, y_tok, lw = 1.3,color="red", zorder=2, label = "Tokyo")
    ax1.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax1.plot(x, y_riku, lw = 2,color="blue", zorder=3,label = "Hokuriku")
    ax1.plot(x, y_kan, lw = 1,color="orange", zorder=1, label = "Kansai")
    ax1.plot(x, y_chg, lw = 1,color="olive", zorder=1, label = "Chugoku")
    ax1.plot(x, y_sik, lw = 1,color="pink", zorder=1, label = "Sikoku")
    ax1.plot(x, y_kyu, lw = 1,color="magenta", zorder=1, label = "Kyushu")


    title_name = str(day_ago1) + "  price"
    ax1.set_title(title_name,fontsize=18)
    ax1.grid(True)
    ax1.set_xlabel("Times of Day(48 frames)")
    ax1.set_ylabel("Price (¥/kWh)")
    plt.xticks(range(0, 24+1, 2))
    ax1.set_xlim(0, 24)
    ax1.set_axisbelow(True)

# グラフ上に数値を表示する
    for i, j in zip(x, y_riku):
        ax1.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
            textcoords='offset points', fontsize=5)

    ax1.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    global day1
    day1 = io.BytesIO()
    fig1.savefig(day1, format="png")
    day1.seek(0)
    img1 = base64.b64encode(day1.read()).decode()

    ###全国と北陸の最大最小値平均を取り出す
    # 全国変数text_max1（最大）,text_min1（最小）,tezt_mean1（平均）に空のデータを入れておく
    # 北陸変数text_max_riku1（最大）,text_min_riku1（最小）,tezt_mean_riku1（平均）に空のデータを入れておく
    text_max1 = ""
    text_min1 = ""
    text_mean1 = ""
    text_max_riku1 = ""
    text_min_riku1 = ""
    text_mean_riku1 = ""

    # 最大最小平均を抽出する列名を変数price_columnsに代入
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    # データのうち日付データ等を除くエリアデータのみ変数today_prices1に代入
    today_prices1 = data[price_columns]

    # 全体の最大値を取り出す際は.max().max()
    max_price1 = today_prices1.max().max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max1に代入
    text_max1 = str(round(max_price1,2))

    # 全体の最小値を取り出す際は.min().min()
    min_price1 = today_prices1.min().min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min1に代入
    text_min1 = str(round(min_price1,2))

    # 全体の平均を取り出す際は.mean().mean()
    mean_price1 = today_prices1.mean().mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean1に代入
    text_mean1 = str(round(mean_price1,2))

    # 北陸の最大値を取り出す際は.max()
    max_price_riku1 = today_prices1['Hokuriku'].max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max_riku1に代入
    text_max_riku1 = str(round(max_price_riku1,2))

    # 北陸の最小値を取り出す際は.min()
    min_price_riku1 = today_prices1['Hokuriku'].min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min_riku1に代入
    text_min_riku1 = str(round(min_price_riku1,2))

    # 北陸の平均を取り出す際は.mean()
    mean_price_riku1 = today_prices1['Hokuriku'].mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean_riku1に代入
    text_mean_riku1 = str(round(mean_price_riku1,2))


    today_prices1.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)
    # グラフをテンプレートに渡す
    return render_template('dayago1.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img1=img1,text_max1=text_max1,text_min1=text_min1,text_mean1=text_mean1,text_max_riku1=text_max_riku1,text_min_riku1=text_min_riku1,text_mean_riku1=text_mean_riku1,today_prices1=today_prices1.to_html(classes='data', header="true"))

@app.route("/dayago2")
def dayago2():
    fig2 = plt.figure()
    # CSVデータを読み込む
    data = pd.read_csv('http://www.jepx.jp/market/excel/spot_2022.csv',encoding="Shift-JIS",usecols=['年月日','時刻コード','システムプライス(円/kWh)','エリアプライス北海道(円/kWh)','エリアプライス東北(円/kWh)','エリアプライス東京(円/kWh)','エリアプライス中部(円/kWh)','エリアプライス北陸(円/kWh)','エリアプライス関西(円/kWh)','エリアプライス中国(円/kWh)','エリアプライス四国(円/kWh)','エリアプライス九州(円/kWh)'])
    data['年月日'] = pd.to_datetime(data['年月日']).dt.date
    data['時刻コード'] = data['時刻コード'].astype(float)
    data['時刻コード'] = data['時刻コード']/2-0.5
    data = data.rename(columns={'システムプライス(円/kWh)': 'System_Price', 'エリアプライス北海道(円/kWh)': 'Hokkaido', 'エリアプライス東北(円/kWh)': 'Tohoku', 'エリアプライス東京(円/kWh)': 'Tokyo', 'エリアプライス中部(円/kWh)': 'Chubu', 'エリアプライス北陸(円/kWh)': 'Hokuriku', 'エリアプライス関西(円/kWh)': 'Kansai', 'エリアプライス中国(円/kWh)': 'Chugoku', 'エリアプライス四国(円/kWh)': 'Sikoku', 'エリアプライス九州(円/kWh)': 'Kyushu'})

    data['System_Price'] = data['System_Price'].astype(float)
    data['Hokkaido'] = data['Hokkaido'].astype(float)
    data['Tohoku'] = data['Tohoku'].astype(float)
    data['Tokyo'] = data['Tokyo'].astype(float)
    data['Chubu'] = data['Chubu'].astype(float)
    data['Hokuriku'] = data['Hokuriku'].astype(float)
    data['Kansai'] = data['Kansai'].astype(float)
    data['Chugoku'] = data['Chugoku'].astype(float)
    data['Sikoku'] = data['Sikoku'].astype(float)
    data['Kyushu'] = data['Kyushu'].astype(float)

    # 現在の日付を取得し、明日のデータを取得
    #today = pd.to_datetime('today').date()
    #yesterday = (today - pd.Timedelta(days=1))
    #tomorrow = (today + pd.Timedelta(days=1))
    latest_date = data.tail(1).iloc[0]['年月日']
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))

    data = data[data['年月日'] == day_ago2]

    # 現在の日付に一致する行だけを選択する場合
    # data = data[data['年月日'] == today]

    # 列名から必要なデータを選択する
    x = data['時刻コード']
    y_sys = data['System_Price']
    y_hok = data['Hokkaido']
    y_toh = data['Tohoku']
    y_tok = data['Tokyo']
    y_chu = data['Chubu']
    y_riku = data['Hokuriku']
    y_kan = data['Kansai']
    y_chg = data['Chugoku']
    y_sik = data['Sikoku']
    y_kyu = data['Kyushu']

    fig2, ax = plt.subplots(tight_layout=True)

    ax.plot(x, y_sys, lw = 1,ls="dashed",color="red", zorder=1, label = "System_Price")
    ax.plot(x, y_hok, lw = 1,color="green", zorder=1, label = "Hokkaido")
    ax.plot(x, y_toh, lw = 1,color="brown", zorder=1, label = "Tohoku")
    ax.plot(x, y_tok, lw = 1.3,color="red", zorder=2, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=3,label = "Hokuriku")
    ax.plot(x, y_kan, lw = 1,color="orange", zorder=1, label = "Kansai")
    ax.plot(x, y_chg, lw = 1,color="olive", zorder=1, label = "Chugoku")
    ax.plot(x, y_sik, lw = 1,color="pink", zorder=1, label = "Sikoku")
    ax.plot(x, y_kyu, lw = 1,color="magenta", zorder=1, label = "Kyushu")


    title_name = str(day_ago2) + "  price"
    ax.set_title(title_name,fontsize=18)
    ax.grid(True)
    ax.set_xlabel("Times of Day(48 frames)")
    ax.set_ylabel("Price (¥/kWh)")
    plt.xticks(range(0, 24+1, 2))
    ax.set_xlim(0, 24)
    ax.set_axisbelow(True)

# グラフ上に数値を表示する
    for i, j in zip(x, y_riku):
        ax.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
            textcoords='offset points', fontsize=5)

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')
    global day2
    day2 = io.BytesIO()
    fig2.savefig(day2, format="png")
    day2.seek(0)
    img2 = base64.b64encode(day2.read()).decode()

    ###全国と北陸の最大最小値平均を取り出す
    # 全国変数text_max2（最大）,text_min2（最小）,tezt_mean2（平均）に空のデータを入れておく
    # 北陸変数text_max_riku2（最大）,text_min_riku2（最小）,tezt_mean_riku2（平均）に空のデータを入れておく
    text_max2 = ""
    text_min2 = ""
    text_mean2 = ""
    text_max_riku2 = ""
    text_min_riku2 = ""
    text_mean_riku2 = ""

    # 最大最小平均を抽出する列名を変数price_columnsに代入
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    # データのうち日付データ等を除くエリアデータのみ変数today_prices2に代入
    today_prices2 = data[price_columns]

    # 全体の最大値を取り出す際は.max().max()
    max_price2 = today_prices2.max().max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max2に代入
    text_max2 = str(round(max_price2,2))

    # 全体の最小値を取り出す際は.min().min()
    min_price2 = today_prices2.min().min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min2に代入
    text_min2 = str(round(min_price2,2))

    # 全体の平均を取り出す際は.mean().mean()
    mean_price2 = today_prices2.mean().mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean2に代入
    text_mean2 = str(round(mean_price2,2))

    # 北陸の最大値を取り出す際は.max()
    max_price_riku2 = today_prices2['Hokuriku'].max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max_riku2に代入
    text_max_riku2 = str(round(max_price_riku2,2))

    # 北陸の最小値を取り出す際は.min()
    min_price_riku2 = today_prices2['Hokuriku'].min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min_riku2に代入
    text_min_riku2 = str(round(min_price_riku2,2))

    # 北陸の平均を取り出す際は.mean()
    mean_price_riku2 = today_prices2['Hokuriku'].mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean_riku2に代入
    text_mean_riku2 = str(round(mean_price_riku2,2))

    today_prices2.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)

    # グラフをテンプレートに渡す
    return render_template('dayago2.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img2=img2,text_max2=text_max2,text_min2=text_min2,text_mean2=text_mean2,text_max_riku2=text_max_riku2,text_min_riku2=text_min_riku2,text_mean_riku2=text_mean_riku2,today_prices2=today_prices2.to_html(classes='data', header="true"))

@app.route("/lastweek")
def lastweek():
    fig3 = plt.figure()
    # CSVデータを読み込む
    data = pd.read_csv('http://www.jepx.jp/market/excel/spot_2022.csv',encoding="Shift-JIS",usecols=['年月日','時刻コード','システムプライス(円/kWh)','エリアプライス北海道(円/kWh)','エリアプライス東北(円/kWh)','エリアプライス東京(円/kWh)','エリアプライス中部(円/kWh)','エリアプライス北陸(円/kWh)','エリアプライス関西(円/kWh)','エリアプライス中国(円/kWh)','エリアプライス四国(円/kWh)','エリアプライス九州(円/kWh)'])
    data['年月日'] = pd.to_datetime(data['年月日']).dt.date
    data['時刻コード'] = data['時刻コード'].astype(float)
    data['時刻コード'] = data['時刻コード']/2-0.5
    data = data.rename(columns={'システムプライス(円/kWh)': 'System_Price', 'エリアプライス北海道(円/kWh)': 'Hokkaido', 'エリアプライス東北(円/kWh)': 'Tohoku', 'エリアプライス東京(円/kWh)': 'Tokyo', 'エリアプライス中部(円/kWh)': 'Chubu', 'エリアプライス北陸(円/kWh)': 'Hokuriku', 'エリアプライス関西(円/kWh)': 'Kansai', 'エリアプライス中国(円/kWh)': 'Chugoku', 'エリアプライス四国(円/kWh)': 'Sikoku', 'エリアプライス九州(円/kWh)': 'Kyushu'})

    data['System_Price'] = data['System_Price'].astype(float)
    data['Hokkaido'] = data['Hokkaido'].astype(float)
    data['Tohoku'] = data['Tohoku'].astype(float)
    data['Tokyo'] = data['Tokyo'].astype(float)
    data['Chubu'] = data['Chubu'].astype(float)
    data['Hokuriku'] = data['Hokuriku'].astype(float)
    data['Kansai'] = data['Kansai'].astype(float)
    data['Chugoku'] = data['Chugoku'].astype(float)
    data['Sikoku'] = data['Sikoku'].astype(float)
    data['Kyushu'] = data['Kyushu'].astype(float)

    # 現在の日付を取得し、明日のデータを取得
    #today = pd.to_datetime('today').date()
    #yesterday = (today - pd.Timedelta(days=1))
    #tomorrow = (today + pd.Timedelta(days=1))
    latest_date = data.tail(1).iloc[0]['年月日']

    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))
    day_ago3 = (latest_date - pd.Timedelta(days=3))
    day_ago4 = (latest_date - pd.Timedelta(days=4))
    day_ago5 = (latest_date - pd.Timedelta(days=5))
    day_ago6 = (latest_date - pd.Timedelta(days=6))

    data =data[(data['年月日'] >= day_ago6) & (data['年月日'] <= latest_date)]

    #data.reset_index()
    data['No'] = range(1, len(data.index) + 1)

    # 現在の日付に一致する行だけを選択する場合
    # data = data[data['年月日'] == today]

    # 列名から必要なデータを選択する
    x = data['No']
    y_sys = data['System_Price']
    y_hok = data['Hokkaido']
    y_toh = data['Tohoku']
    y_tok = data['Tokyo']
    y_chu = data['Chubu']
    y_riku = data['Hokuriku']
    y_kan = data['Kansai']
    y_chg = data['Chugoku']
    y_sik = data['Sikoku']
    y_kyu = data['Kyushu']

    fig3, ax = plt.subplots(tight_layout=True)

    ax.plot(x, y_sys, lw = 1,ls="dashed",color="red", zorder=1, label = "System_Price")
    ax.plot(x, y_hok, lw = 1,color="green", zorder=1, label = "Hokkaido")
    ax.plot(x, y_toh, lw = 1,color="brown", zorder=1, label = "Tohoku")
    ax.plot(x, y_tok, lw = 1.3,color="red", zorder=2, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=3,label = "Hokuriku")
    ax.plot(x, y_kan, lw = 1,color="orange", zorder=1, label = "Kansai")
    ax.plot(x, y_chg, lw = 1,color="olive", zorder=1, label = "Chugoku")
    ax.plot(x, y_sik, lw = 1,color="pink", zorder=1, label = "Sikoku")
    ax.plot(x, y_kyu, lw = 1,color="magenta", zorder=1, label = "Kyushu")


    title_name = str(day_ago6) + "--->" +  str(latest_date)  +"  price"
    ax.set_title(title_name,fontsize=15)
    ax.grid(which='major')
    ax.set_xlabel("Last Week(7days)")
    ax.set_ylabel("Price (¥/kWh)")
    ax.set_xlim(0, 336)
    ax.set_xticks([0,48,96,144,192,240,288,336])
    ax.set_xticklabels(["","","","","","","",""])
    ax.set_xticks([24,72,120,168,216,264,312],minor=True)
    ax.set_xticklabels([day_ago6,day_ago5,day_ago4,day_ago3,day_ago2,day_ago1,latest_date],rotation = "vertical",minor=True)
    ax.set_axisbelow(True)

# グラフ上に数値を表示する
    #for i, j in zip(x, y_riku):
       # ax.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
         #   textcoords='offset points', fontsize=5)

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left',fontsize=10)
    global week
    week = io.BytesIO()
    fig3.savefig(week, format="png")
    week.seek(0)
    img3 = base64.b64encode(week.read()).decode()


    ###全国と北陸の最大最小値平均を取り出す
    # 全国変数text_max3（最大）,text_min3（最小）,tezt_mean3（平均）に空のデータを入れておく
    # 北陸変数text_max_riku3（最大）,text_min_riku3（最小）,tezt_mean_riku3（平均）に空のデータを入れておく
    text_max3 = ""
    text_min3 = ""
    text_mean3 = ""
    text_max_riku3 = ""
    text_min_riku3 = ""
    text_mean_riku3 = ""

    # 最大最小平均を抽出する列名を変数price_columnsに代入
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    # データのうち日付データ等を除くエリアデータのみ変数today_prices3に代入
    today_prices3 = data[price_columns]

    # 全体の最大値を取り出す際は.max().max()
    max_price3 = today_prices3.max().max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max3に代入
    text_max3 = str(round(max_price3,2))

    # 全体の最小値を取り出す際は.min().min()
    min_price3 = today_prices3.min().min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min3に代入
    text_min3 = str(round(min_price3,2))

    # 全体の平均を取り出す際は.mean().mean()
    mean_price3 = today_prices3.mean().mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean3に代入
    text_mean3 = str(round(mean_price3,2))

    # 北陸の最大値を取り出す際は.max()
    max_price_riku3 = today_prices3['Hokuriku'].max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max_riku3に代入
    text_max_riku3 = str(round(max_price_riku3,2))

    # 北陸の最小値を取り出す際は.min()
    min_price_riku3 = today_prices3['Hokuriku'].min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min_riku3に代入
    text_min_riku3 = str(round(min_price_riku3,2))

    # 北陸の平均を取り出す際は.mean()
    mean_price_riku3 = today_prices3['Hokuriku'].mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean_riku3に代入
    text_mean_riku3 = str(round(mean_price_riku3,2))

    # グラフをテンプレートに渡す
    return render_template('lastweek.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img3=img3,text_max3=text_max3,text_min3=text_min3,text_mean3=text_mean3,text_max_riku3=text_max_riku3,text_min_riku3=text_min_riku3,text_mean_riku3=text_mean_riku3)

@app.route("/lastmonth")
def lastmonth():
    fig4 = plt.figure()
    # CSVデータを読み込む
    data = pd.read_csv('http://www.jepx.jp/market/excel/spot_2022.csv',encoding="Shift-JIS",usecols=['年月日','時刻コード','システムプライス(円/kWh)','エリアプライス北海道(円/kWh)','エリアプライス東北(円/kWh)','エリアプライス東京(円/kWh)','エリアプライス中部(円/kWh)','エリアプライス北陸(円/kWh)','エリアプライス関西(円/kWh)','エリアプライス中国(円/kWh)','エリアプライス四国(円/kWh)','エリアプライス九州(円/kWh)'])
    data['年月日'] = pd.to_datetime(data['年月日']).dt.date
    data['時刻コード'] = data['時刻コード'].astype(float)
    data['時刻コード'] = data['時刻コード']/2-0.5
    data = data.rename(columns={'システムプライス(円/kWh)': 'System_Price', 'エリアプライス北海道(円/kWh)': 'Hokkaido', 'エリアプライス東北(円/kWh)': 'Tohoku', 'エリアプライス東京(円/kWh)': 'Tokyo', 'エリアプライス中部(円/kWh)': 'Chubu', 'エリアプライス北陸(円/kWh)': 'Hokuriku', 'エリアプライス関西(円/kWh)': 'Kansai', 'エリアプライス中国(円/kWh)': 'Chugoku', 'エリアプライス四国(円/kWh)': 'Sikoku', 'エリアプライス九州(円/kWh)': 'Kyushu'})

    data['System_Price'] = data['System_Price'].astype(float)
    data['Hokkaido'] = data['Hokkaido'].astype(float)
    data['Tohoku'] = data['Tohoku'].astype(float)
    data['Tokyo'] = data['Tokyo'].astype(float)
    data['Chubu'] = data['Chubu'].astype(float)
    data['Hokuriku'] = data['Hokuriku'].astype(float)
    data['Kansai'] = data['Kansai'].astype(float)
    data['Chugoku'] = data['Chugoku'].astype(float)
    data['Sikoku'] = data['Sikoku'].astype(float)
    data['Kyushu'] = data['Kyushu'].astype(float)

    # 現在の日付を取得し、明日のデータを取得
    #today = pd.to_datetime('today').date()
    #yesterday = (today - pd.Timedelta(days=1))
    #tomorrow = (today + pd.Timedelta(days=1))
    latest_date = data.tail(1).iloc[0]['年月日']

    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))
    day_ago5 = (latest_date - pd.Timedelta(days=5))
    day_ago10 = (latest_date - pd.Timedelta(days=10))
    day_ago15 = (latest_date - pd.Timedelta(days=15))
    day_ago20 = (latest_date - pd.Timedelta(days=25))
    day_ago25 = (latest_date - pd.Timedelta(days=25))
    day_ago30 = (latest_date - pd.Timedelta(days=30))

    data =data[(data['年月日'] >= day_ago30) & (data['年月日'] <= latest_date)]

    #data.reset_index()
    data['No'] = range(1, len(data.index) + 1)

    # 現在の日付に一致する行だけを選択する場合
    # data = data[data['年月日'] == today]

    # 列名から必要なデータを選択する
    x = data['No']
    y_sys = data['System_Price']
    y_hok = data['Hokkaido']
    y_toh = data['Tohoku']
    y_tok = data['Tokyo']
    y_chu = data['Chubu']
    y_riku = data['Hokuriku']
    y_kan = data['Kansai']
    y_chg = data['Chugoku']
    y_sik = data['Sikoku']
    y_kyu = data['Kyushu']

    fig4, ax = plt.subplots(tight_layout=True)

    ax.plot(x, y_sys, lw = 1,ls="dashed",color="red", zorder=1, label = "System_Price")
    ax.plot(x, y_hok, lw = 1,color="green", zorder=1, label = "Hokkaido")
    ax.plot(x, y_toh, lw = 1,color="brown", zorder=1, label = "Tohoku")
    ax.plot(x, y_tok, lw = 1.3,color="red", zorder=2, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=3,label = "Hokuriku")
    ax.plot(x, y_kan, lw = 1,color="orange", zorder=1, label = "Kansai")
    ax.plot(x, y_chg, lw = 1,color="olive", zorder=1, label = "Chugoku")
    ax.plot(x, y_sik, lw = 1,color="pink", zorder=1, label = "Sikoku")
    ax.plot(x, y_kyu, lw = 1,color="magenta", zorder=1, label = "Kyushu")


    title_name = str(day_ago30) + "--->" +  str(latest_date)  +"  price"
    ax.set_title(title_name,fontsize=15)
    ax.grid(which='major')
    ax.set_xlabel("Last Month(30days)")
    ax.set_ylabel("Price (¥/kWh)")
    ax.set_xlim(0, 1440+1)
    ax.set_xticks([0,240,480,720,960,1200,1440])
    ax.set_xticklabels([day_ago30,day_ago25,day_ago20,day_ago15,day_ago10,day_ago5,latest_date],rotation = "vertical")
    ax.set_axisbelow(True)

# グラフ上に数値を表示する
    #for i, j in zip(x, y_riku):
       # ax.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
         #   textcoords='offset points', fontsize=5)

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left',fontsize=10)
    global month
    month = io.BytesIO()
    fig4.savefig(month, format="png")
    month.seek(0)
    img4 = base64.b64encode(month.read()).decode()


    ###全国と北陸の最大最小値平均を取り出す
    # 全国変数text_max4（最大）,text_min4（最小）,tezt_mean4（平均）に空のデータを入れておく
    # 北陸変数text_max_riku4（最大）,text_min_riku4（最小）,tezt_mean_riku4（平均）に空のデータを入れておく
    text_max4 = ""
    text_min4 = ""
    text_mean4 = ""
    text_max_riku4 = ""
    text_min_riku4 = ""
    text_mean_riku4 = ""

    # 最大最小平均を抽出する列名を変数price_columnsに代入
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    # データのうち日付データ等を除くエリアデータのみ変数today_prices4に代入
    today_prices4 = data[price_columns]

    # 全体の最大値を取り出す際は.max().max()
    max_price4 = today_prices4.max().max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max4に代入
    text_max4 = str(round(max_price4,2))

    # 全体の最小値を取り出す際は.min().min()
    min_price4 = today_prices4.min().min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min4に代入
    text_min4 = str(round(min_price4,2))

    # 全体の平均を取り出す際は.mean().mean()
    mean_price4 = today_prices4.mean().mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean4に代入
    text_mean4 = str(round(mean_price4,2))

    # 北陸の最大値を取り出す際は.max()
    max_price_riku4 = today_prices4['Hokuriku'].max()
    # 最大値を小数点第2位で四捨五入してstrで文字列に変換しtext_max_riku4に代入
    text_max_riku4 = str(round(max_price_riku4,2))

    # 北陸の最小値を取り出す際は.min()
    min_price_riku4 = today_prices4['Hokuriku'].min()
    # 最小値を小数点第2位で四捨五入してstrで文字列に変換しtext_min_riku4に代入
    text_min_riku4 = str(round(min_price_riku4,2))

    # 北陸の平均を取り出す際は.mean()
    mean_price_riku4 = today_prices4['Hokuriku'].mean()
    # 平均値を小数点第2位で四捨五入してstrで文字列に変換しtext_mean_riku4に代入
    text_mean_riku4 = str(round(mean_price_riku4,2))


    # グラフをテンプレートに渡す
    return render_template('lastmonth.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img4=img4,text_max4=text_max4,text_min4=text_min4,text_mean4=text_mean4,text_max_riku4=text_max_riku4,text_min_riku4=text_min_riku4,text_mean_riku4=text_mean_riku4)

@app.route("/QR")
def QR():

    # CSVデータを読み込む
    data = pd.read_csv('http://www.jepx.jp/market/excel/spot_2022.csv',encoding="Shift-JIS",usecols=['年月日'])
    data['年月日'] = pd.to_datetime(data['年月日']).dt.date

    latest_date = data.tail(1).iloc[0]['年月日']
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))

    # グラフをテンプレートに渡す
    return render_template('QR.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2)


@app.route("/FY2019to2022")
def FY2019to2022():
    fig5 = plt.figure()
    # 2022CSVデータを読み込む
    data2022 = pd.read_csv('http://www.jepx.jp/market/excel/spot_2022.csv',encoding="Shift-JIS",usecols=['年月日','エリアプライス北陸(円/kWh)'])
    data2022['年月日'] = pd.to_datetime(data2022['年月日']).dt.date
    data2022 = data2022.rename(columns={ 'エリアプライス北陸(円/kWh)': 'Hokuriku'})
    data2022['Hokuriku'] = data2022['Hokuriku'].astype(float)
    latest_date = data2022.tail(1).iloc[0]['年月日']
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))
    #data.reset_index()
    data2022['No'] = range(1, len(data2022.index) + 1)
    # 2021CSVデータを読み込む
  
    data2021 =  pd.read_csv('http://www.jepx.jp/market/excel/spot_2021.csv',encoding="Shift-JIS",usecols=['年月日','エリアプライス北陸(円/kWh)'])
    data2021['年月日'] = pd.to_datetime(data2021['年月日']).dt.date
    data2021 = data2021.rename(columns={ 'エリアプライス北陸(円/kWh)': 'Hokuriku'})
    data2021['Hokuriku'] = data2021['Hokuriku'].astype(float)
    #data.reset_index()
    data2021['No'] = range(1, len(data2021.index) + 1)
    # 2020CSVデータを読み込む
    data2020 = pd.read_csv('http://www.jepx.jp/market/excel/spot_2020.csv',encoding="Shift-JIS",usecols=['年月日','エリアプライス北陸(円/kWh)'])
    data2020['年月日'] = pd.to_datetime(data2020['年月日']).dt.date
    data2020 = data2020.rename(columns={ 'エリアプライス北陸(円/kWh)': 'Hokuriku'})
    data2020['Hokuriku'] = data2020['Hokuriku'].astype(float)
    #data.reset_index()
    data2020['No'] = range(1, len(data2020.index) + 1)
    # 2019CSVデータを読み込む
    data2019 = pd.read_csv('http://www.jepx.jp/market/excel/spot_2019.csv',encoding="Shift-JIS",usecols=['年月日','エリアプライス北陸(円/kWh)'])
    data2019['年月日'] = pd.to_datetime(data2019['年月日']).dt.date
    data2019 = data2019.rename(columns={ 'エリアプライス北陸(円/kWh)': 'Hokuriku'})
    data2019['Hokuriku'] = data2019['Hokuriku'].astype(float)
    #data.reset_index()
    data2019['No'] = range(1, len(data2019.index) + 1)

    # 列名から必要なデータを選択する
    x22 = data2022['No']
    y_riku22 = data2022['Hokuriku']
    x21 = data2021['No']
    y_riku21 = data2021['Hokuriku']
    x20 = data2020['No']
    y_riku20 = data2020['Hokuriku']
    x19 = data2019['No']
    y_riku19 = data2019['Hokuriku']

    fig5, ax = plt.subplots(tight_layout=True)

    ax.plot(x22, y_riku22, lw = 0.4,color="blue", zorder=2,label = "FY2022")
    ax.plot(x21, y_riku21, lw = 0.2,color="red", zorder=1,label = "FY2021")
    ax.plot(x20, y_riku20, lw = 0.2,color="darkgreen", zorder=1,label = "FY2020")
    ax.plot(x19, y_riku19, lw = 0.2,color="black", zorder=1,label = "FY2019")

    title_name = "Hokuriku  FY2019 -> FY2022  price"
    ax.set_title(title_name,fontsize=15)
    ax.grid(which='major')
    ax.set_xlabel(" Month(FY)")
    ax.set_ylabel("Price (¥/kWh)")
    ax.set_xlim(0, 17521+1)
    ax.set_xticks([0,1440,2928,4368,5856,7344,8784,10272,11712,13200,14688,16032,17520])
    ax.set_xticklabels(["","","","","","","","","","","","",""])
    ax.set_xticks([720,2184,3648,5112,6600,8064,9528,10992,12456,13944,15360,16776],minor=True)
    ax.set_xticklabels(["4","5","6","7","8","9","10","11","12","1","2","3",],minor=True)
    ax.set_axisbelow(True)

# グラフ上に数値を表示する
    #for i, j in zip(x, y_riku):
       # ax.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
         #   textcoords='offset points', fontsize=5)

    ax.legend(loc='upper left',fontsize=10,framealpha=1,labelcolor='linecolor')
    global fy
    fy = io.BytesIO()
    fig5.savefig(fy, format="png")
    fy.seek(0)
    img5 = base64.b64encode(fy.read()).decode()

    #2022最大最小平均を取り出す
    text_max2022 = ""
    text_min2022 = ""
    text_mean2022 = ""
    max_price2022 = data2022['Hokuriku'].max()
    text_max2022 = str(round(max_price2022,2))
    min_price2022 = data2022['Hokuriku'].min()
    text_min2022 = str(round(min_price2022,2))
    mean_price2022 = data2022['Hokuriku'].mean()
    text_mean2022 = str(round(mean_price2022,2))
    #2021最大最小平均を取り出す
    text_max2021 = ""
    text_min2021 = ""
    text_mean2021 = ""
    max_price2021 = data2021['Hokuriku'].max()
    text_max2021 = str(round(max_price2021,2))
    min_price2021 = data2021['Hokuriku'].min()
    text_min2021 = str(round(min_price2021,2))
    mean_price2021 = data2021['Hokuriku'].mean()
    text_mean2021 = str(round(mean_price2021,2))
    #2020最大最小平均を取り出す
    text_max2020 = ""
    text_min2020 = ""
    text_mean2020 = ""
    max_price2020 = data2020['Hokuriku'].max()
    text_max2020 = str(round(max_price2020,2))
    min_price2020 = data2020['Hokuriku'].min()
    text_min2020 = str(round(min_price2020,2))
    mean_price2020 = data2020['Hokuriku'].mean()
    text_mean2020 = str(round(mean_price2020,2))
    #2019最大最小平均を取り出す
    text_max2019 = ""
    text_min2019 = ""
    text_mean2019 = ""
    max_price2019 = data2019['Hokuriku'].max()
    text_max2019 = str(round(max_price2019,2))
    min_price2019 = data2019['Hokuriku'].min()
    text_min2019 = str(round(min_price2019,2))
    mean_price2019 = data2019['Hokuriku'].mean()
    text_mean2019 = str(round(mean_price2019,2))

    #参考に年度別グラフを作成 2022
    fig22, ax22 = plt.subplots(tight_layout=True)

    ax22.plot(x22, y_riku22, lw = 0.4,color="blue", zorder=2,label = "FY2022")
   
    title_name = "Hokuriku  FY2022  price"
    ax22.set_title(title_name,fontsize=15)
    ax22.grid(which='major')
    ax22.set_xlabel(" Month(FY)")
    ax22.set_ylabel("Price (¥/kWh)")
    ax22.set_xlim(0, 17521+1)
    ax22.set_xticks([0,1440,2928,4368,5856,7344,8784,10272,11712,13200,14688,16032,17520])
    ax22.set_xticklabels(["","","","","","","","","","","","",""])
    ax22.set_xticks([720,2184,3648,5112,6600,8064,9528,10992,12456,13944,15360,16776],minor=True)
    ax22.set_xticklabels(["4","5","6","7","8","9","10","11","12","1","2","3",],minor=True)
    ax22.set_axisbelow(True)
    
    global fy22
    fy22 = io.BytesIO()
    fig22.savefig(fy22, format="png")
    fy22.seek(0)
    img22 = base64.b64encode(fy22.read()).decode()

    #参考に年度別グラフを作成 2021
    fig21, ax21 = plt.subplots(tight_layout=True)

    ax21.plot(x21, y_riku21, lw = 0.4,color="red", zorder=2,label = "FY2021")
   
    title_name = "Hokuriku  FY2021  price"
    ax21.set_title(title_name,fontsize=15)
    ax21.grid(which='major')
    ax21.set_xlabel(" Month(FY)")
    ax21.set_ylabel("Price (¥/kWh)")
    ax21.set_xlim(0, 17521+1)
    ax21.set_xticks([0,1440,2928,4368,5856,7344,8784,10272,11712,13200,14688,16032,17520])
    ax21.set_xticklabels(["","","","","","","","","","","","",""])
    ax21.set_xticks([720,2184,3648,5112,6600,8064,9528,10992,12456,13944,15360,16776],minor=True)
    ax21.set_xticklabels(["4","5","6","7","8","9","10","11","12","1","2","3",],minor=True)
    ax21.set_axisbelow(True)
    
    global fy21
    fy21 = io.BytesIO()
    fig21.savefig(fy21, format="png")
    fy21.seek(0)
    img21 = base64.b64encode(fy21.read()).decode()

    #参考に年度別グラフを作成 2020
    fig20, ax20 = plt.subplots(tight_layout=True)

    ax20.plot(x20, y_riku20, lw = 0.4,color="darkgreen", zorder=2,label = "FY2020")
   
    title_name = "Hokuriku  FY2020  price"
    ax20.set_title(title_name,fontsize=15)
    ax20.grid(which='major')
    ax20.set_xlabel(" Month(FY)")
    ax20.set_ylabel("Price (¥/kWh)")
    ax20.set_xlim(0, 17521+1)
    ax20.set_xticks([0,1440,2928,4368,5856,7344,8784,10272,11712,13200,14688,16032,17520])
    ax20.set_xticklabels(["","","","","","","","","","","","",""])
    ax20.set_xticks([720,2184,3648,5112,6600,8064,9528,10992,12456,13944,15360,16776],minor=True)
    ax20.set_xticklabels(["4","5","6","7","8","9","10","11","12","1","2","3",],minor=True)
    ax20.set_axisbelow(True)
    
    global fy20
    fy20 = io.BytesIO()
    fig20.savefig(fy20, format="png")
    fy20.seek(0)
    img20 = base64.b64encode(fy20.read()).decode()

    #参考に年度別グラフを作成 2019
    fig19, ax19 = plt.subplots(tight_layout=True)

    ax19.plot(x19, y_riku19, lw = 0.4,color="black", zorder=2,label = "FY2019")
   
    title_name = "Hokuriku  FY2019  price"
    ax19.set_title(title_name,fontsize=15)
    ax19.grid(which='major')
    ax19.set_xlabel(" Month(FY)")
    ax19.set_ylabel("Price (¥/kWh)")
    ax19.set_xlim(0, 17521+1)
    ax19.set_xticks([0,1440,2928,4368,5856,7344,8784,10272,11712,13200,14688,16032,17520])
    ax19.set_xticklabels(["","","","","","","","","","","","",""])
    ax19.set_xticks([720,2184,3648,5112,6600,8064,9528,10992,12456,13944,15360,16776],minor=True)
    ax19.set_xticklabels(["4","5","6","7","8","9","10","11","12","1","2","3",],minor=True)
    ax19.set_axisbelow(True)
    
    global fy19
    fy19 = io.BytesIO()
    fig19.savefig(fy19, format="png")
    fy19.seek(0)
    img19 = base64.b64encode(fy19.read()).decode()


    # グラフをテンプレートに渡す
    return render_template('FY2019to2022.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img5=img5,img22=img22,img21=img21,img20=img20,img19=img19,text_max2022=text_max2022,text_min2022=text_min2022,text_mean2022=text_mean2022,text_max2021=text_max2021,text_min2021=text_min2021,text_mean2021=text_mean2021,text_max2020=text_max2020,text_min2020=text_min2020,text_mean2020=text_mean2020,text_max2019=text_max2019,text_min2019=text_min2019,text_mean2019=text_mean2019)

## 実行
if __name__ == "__main__":
    app.run(debug=True)
