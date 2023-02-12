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
    data['時刻コード'] = data['時刻コード']/2
    data['エリアプライス北陸(円/kWh)'] = data['エリアプライス北陸(円/kWh)'].astype(float)

    # 現在の日付を取得し、明日のデータを取得
    today = pd.to_datetime('today').date()
    yesterday = (today - pd.Timedelta(days=1))
    tomorrow = (today + pd.Timedelta(days=1))
    data = data[data['年月日'] == tomorrow]

    # 現在の日付に一致する行だけを選択する場合
    # data = data[data['年月日'] == today]

    # 列名から必要なデータを選択する
    x = data['時刻コード']
    y_sys = data['システムプライス(円/kWh)']
    y_hok = data['エリアプライス北海道(円/kWh)']
    y_toh = data['エリアプライス東北(円/kWh)']
    y_tok = data['エリアプライス東京(円/kWh)']
    y_chu = data['エリアプライス中部(円/kWh)']
    y_riku = data['エリアプライス北陸(円/kWh)']
    y_kan = data['エリアプライス関西(円/kWh)']
    y_chg = data['エリアプライス中国(円/kWh)']
    y_sik = data['エリアプライス四国(円/kWh)']
    y_kyu = data['エリアプライス九州(円/kWh)']

    fig, ax = plt.subplots(tight_layout=True)
    
    ax.plot(x, y_sys, lw = 1,ls="dashed",color="red", label = "system")
    ax.plot(x, y_hok, lw = 1,color="green", label = "Hokkaido")
    ax.plot(x, y_toh, lw = 1,color="brown", label = "Tohoku")
    ax.plot(x, y_tok, lw = 1,color="cyan", label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="magenta", label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", label = "Hokuriku")
    ax.plot(x, y_kan, lw = 1,color="orange", label = "Kansai")
    ax.plot(x, y_chg, lw = 1,color="olive", label = "Chugoku")
    ax.plot(x, y_sik, lw = 1,color="pink", label = "Sikoku")
    ax.plot(x, y_kyu, lw = 1,color="gray", label = "Kyushu")


    title_name = str(tomorrow) + "  price"
    ax.set_title(title_name,fontsize=18)
    ax.grid(True)
    ax.set_xlabel("Times of Day(48 frames)")
    ax.set_ylabel("Price (¥/kWh)")
    plt.xticks(range(0, 24+1, 2))
    ax.set_xlim(0, 24)

# グラフ上に数値を表示する
    for i, j in zip(x, y_riku):
        ax.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
            textcoords='offset points', fontsize=5)

    ax.legend(bbox_to_anchor=(1.05, 1.0), loc='upper left')

    img = fig_to_base64_img(fig)


    # グラフをテンプレートに渡す
    return render_template('index.html', img=img)


## 実行
if __name__ == "__main__":
    app.run(debug=True)
