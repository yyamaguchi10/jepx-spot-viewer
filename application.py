from flask import Flask,render_template,request, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import os
import io



app = Flask(__name__,static_folder='./static')

io = io.BytesIO()
def fig_to_base64_img(fig):
    fig.savefig(io, format="png")
    io.seek(0)
    base64_img = base64.b64encode(io.read()).decode()

    return base64_img

@app.context_processor
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



@app.route("/")
def index():
    fig = plt.figure()
    # CSVデータを読み込む
    data = pd.read_csv('http://www.jepx.org/market/excel/spot_2022.csv',encoding="Shift-JIS")
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
    today = pd.to_datetime('today').date()
    yesterday = (today - pd.Timedelta(days=1))
    tomorrow = (today + pd.Timedelta(days=1))
    data = data[data['年月日'] == tomorrow]

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

    fig, ax = plt.subplots(tight_layout=True)

    ax.plot(x, y_sys, lw = 1,ls="dashed",color="red", zorder=1, label = "System_Price")
    ax.plot(x, y_hok, lw = 1,color="green", zorder=1, label = "Hokkaido")
    ax.plot(x, y_toh, lw = 1,color="brown", zorder=1, label = "Tohoku")
    ax.plot(x, y_tok, lw = 1,color="darkturquoise", zorder=1, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=2,label = "Hokuriku")
    ax.plot(x, y_kan, lw = 1,color="orange", zorder=1, label = "Kansai")
    ax.plot(x, y_chg, lw = 1,color="olive", zorder=1, label = "Chugoku")
    ax.plot(x, y_sik, lw = 1,color="pink", zorder=1, label = "Sikoku")
    ax.plot(x, y_kyu, lw = 1,color="magenta", zorder=1, label = "Kyushu")


    title_name = str(tomorrow) + "  price"
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

    img = fig_to_base64_img(fig)

    #最大最小値を取り出す
    text_max = ""
    text_min = ""
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    today_prices = data[price_columns]

    max_price = today_prices.max().max()
    #max_prices = data[data[today_prices] == data[today_prices].max()]
    text_max = str(round(max_price,2))

    min_price = today_prices.min().min()
    #min_prices = data[data['today_prices'] == data['today_prices'].min()]
    text_min = str(round(min_price,2))

    #style = today_prices.style.highlight_min(color="yellow")
    #style = today_prices.style.highlight_max(color="red")
    today_prices.insert(0,'time', ["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"])
    today_prices = today_prices.set_index('time',inplace=True)

    # グラフをテンプレートに渡す
    return render_template('index.html', img=img,text_max=text_max,text_min=text_min,today_prices=today_prices.to_html(classes='data', header="true"))


## 実行
if __name__ == "__main__":
    app.run(debug=True)
