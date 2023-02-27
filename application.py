from flask import Flask,render_template,request, url_for
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
import os
import io

app = Flask(__name__,static_folder='./static')

newday = io.BytesIO()
day1 = io.BytesIO()
day2 = io.BytesIO()
week = io.BytesIO()
month = io.BytesIO()
fy = io.BytesIO()
fy22 = io.BytesIO()
fy21 = io.BytesIO()
fy20 = io.BytesIO()
fy19 = io.BytesIO()



def fig_to_base64_img(fig):
    global io
    
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
    #today = pd.to_datetime('today').date()
    #yesterday = (today - pd.Timedelta(days=1))
    #tomorrow = (today + pd.Timedelta(days=1))
    latest_date = data.tail(1).iloc[0]['年月日']
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))

    data = data[data['年月日'] == latest_date]

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


    title_name = str(latest_date) + "  price"
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

    global newday
    fig.savefig(newday, format="png")
    newday.seek(0)
    img = base64.b64encode(newday.read()).decode()

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
    #today_prices.insert(1,'time', ["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"])
    #today_prices = today_prices.set_index('time')
    today_prices.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)
    # グラフをテンプレートに渡す
    return render_template('index.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img=img,text_max=text_max,text_min=text_min,today_prices=today_prices.to_html(classes='data', header="true"))

@app.route("/dayago1")
def dayago1():
    fig1 = plt.figure()
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
    ax1.plot(x, y_tok, lw = 1,color="darkturquoise", zorder=1, label = "Tokyo")
    ax1.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax1.plot(x, y_riku, lw = 2,color="blue", zorder=2,label = "Hokuriku")
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

    fig1.savefig(day1, format="png")
    day1.seek(0)
    img1 = base64.b64encode(day1.read()).decode()


    #最大最小値を取り出す
    text_max1 = ""
    text_min1 = ""
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    today_prices1 = data[price_columns]

    max_price1 = today_prices1.max().max()
    #max_prices = data[data[today_prices] == data[today_prices].max()]
    text_max1 = str(round(max_price1,2))

    min_price1 = today_prices1.min().min()
    #min_prices = data[data['today_prices'] == data['today_prices'].min()]
    text_min1 = str(round(min_price1,2))

    #style = today_prices.style.highlight_min(color="yellow")
    #style = today_prices.style.highlight_max(color="red")
    #today_prices1.insert(1,'time', ["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"])
    #today_prices1 = today_prices1.set_index('time')
    today_prices1.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)
    # グラフをテンプレートに渡す
    return render_template('dayago1.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img1=img1,text_max1=text_max1,text_min1=text_min1,today_prices1=today_prices1.to_html(classes='data', header="true"))

@app.route("/dayago2")
def dayago2():
    fig2 = plt.figure()
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
    ax.plot(x, y_tok, lw = 1,color="darkturquoise", zorder=1, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=2,label = "Hokuriku")
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

    fig2.savefig(day2, format="png")
    day2.seek(0)
    img2 = base64.b64encode(day2.read()).decode()

    #最大最小値を取り出す
    text_max2 = ""
    text_min2 = ""
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    today_prices2 = data[price_columns]

    max_price2 = today_prices2.max().max()
    #max_prices = data[data[today_prices] == data[today_prices].max()]
    text_max2 = str(round(max_price2,2))

    min_price2 = today_prices2.min().min()
    #min_prices = data[data['today_prices'] == data['today_prices'].min()]
    text_min2 = str(round(min_price2,2))

    #style = today_prices.style.highlight_min(color="yellow")
    #style = today_prices.style.highlight_max(color="red")
    #today_prices2.insert(1,'time', ["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"])
    #today_prices2 = today_prices2.set_index('time')
    today_prices2.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)

    # グラフをテンプレートに渡す
    return render_template('dayago2.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img2=img2,text_max2=text_max2,text_min2=text_min2,today_prices2=today_prices2.to_html(classes='data', header="true"))

@app.route("/lastweek")
def lastweek():
    fig3 = plt.figure()
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
    ax.plot(x, y_tok, lw = 1,color="darkturquoise", zorder=1, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=2,label = "Hokuriku")
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

    fig3.savefig(week, format="png")
    week.seek(0)
    img3 = base64.b64encode(week.read()).decode()

    #最大最小値を取り出す
    text_max3 = ""
    text_min3 = ""
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    today_prices3 = data[price_columns]

    max_price3 = today_prices3.max().max()
    #max_prices = data[data[today_prices] == data[today_prices].max()]
    text_max3 = str(round(max_price3,2))

    min_price3 = today_prices3.min().min()
    #min_prices = data[data['today_prices'] == data['today_prices'].min()]
    text_min3 = str(round(min_price3,2))

    #style = today_prices.style.highlight_min(color="yellow")
    #style = today_prices.style.highlight_max(color="red")
    #today_prices2.insert(1,'time', ["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"])
    #today_prices2 = today_prices2.set_index('time')
    #today_prices2.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)

    # グラフをテンプレートに渡す
    return render_template('lastweek.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img3=img3,text_max3=text_max3,text_min3=text_min3)

@app.route("/lastmonth")
def lastmonth():
    fig4 = plt.figure()
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
    ax.plot(x, y_tok, lw = 1,color="darkturquoise", zorder=1, label = "Tokyo")
    ax.plot(x, y_chu, lw = 1,color="lime", zorder=1, label = "Chubu")
    ax.plot(x, y_riku, lw = 2,color="blue", zorder=2,label = "Hokuriku")
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

    fig4.savefig(month, format="png")
    month.seek(0)
    img4 = base64.b64encode(month.read()).decode()

    #最大最小値を取り出す
    text_max4 = ""
    text_min4 = ""
    price_columns = ['Hokkaido', 'Tohoku', 'Tokyo', 'Chubu', 'Hokuriku', 'Kansai', 'Chugoku', 'Sikoku', 'Kyushu']
    today_prices4 = data[price_columns]

    max_price4 = today_prices4.max().max()
    #max_prices = data[data[today_prices] == data[today_prices].max()]
    text_max4 = str(round(max_price4,2))

    min_price4 = today_prices4.min().min()
    #min_prices = data[data['today_prices'] == data['today_prices'].min()]
    text_min4 = str(round(min_price4,2))

    #style = today_prices.style.highlight_min(color="yellow")
    #style = today_prices.style.highlight_max(color="red")
    #today_prices2.insert(1,'time', ["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"])
    #today_prices2 = today_prices2.set_index('time')
    #today_prices2.set_axis(["0:00-","0:30-","1:00-","1:30-","2:00-","2:30-","3:00-","3:30-","4:00-","4:30-","5:00-","5:30-","6:00-","6:30-","7:00-","7:30-","8:00-","8:30-","9:00-","9:30-","10:00-","10:30-","11:00-","11:30-","12:00-","12:30-","13:00-","13:30-","14:00-","14:30-","15:00-","15:30-","16:00-","16:30-","17:00-","17:30-","18:00-","18:30-","19:00-","19:30-","20:00-","20:30-","21:00-","21:30-","22:00-","22:30-","23:00-","23:30-"],axis=0,inplace=True)

    # グラフをテンプレートに渡す
    return render_template('lastmonth.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img4=img4,text_max4=text_max4,text_min4=text_min4)

@app.route("/QR")
def QR():

    # CSVデータを読み込む
    data = pd.read_csv('http://www.jepx.org/market/excel/spot_2022.csv',encoding="Shift-JIS")
    data['年月日'] = pd.to_datetime(data['年月日']).dt.date

    latest_date = data.tail(1).iloc[0]['年月日']
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))
    day_ago5 = (latest_date - pd.Timedelta(days=5))
    day_ago10 = (latest_date - pd.Timedelta(days=10))
    day_ago15 = (latest_date - pd.Timedelta(days=15))
    day_ago20 = (latest_date - pd.Timedelta(days=25))
    day_ago25 = (latest_date - pd.Timedelta(days=25))
    day_ago30 = (latest_date - pd.Timedelta(days=30))


    # グラフをテンプレートに渡す
    return render_template('QR.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2)


@app.route("/FY2019to2022")
def FY2019to2022():
    fig5 = plt.figure()
    # 2022CSVデータを読み込む
    data2022 = pd.read_csv('http://www.jepx.org/market/excel/spot_2022.csv',encoding="Shift-JIS")
    data2022['年月日'] = pd.to_datetime(data2022['年月日']).dt.date
    data2022 = data2022.rename(columns={ 'エリアプライス北陸(円/kWh)': 'Hokuriku'})
    data2022['Hokuriku'] = data2022['Hokuriku'].astype(float)
    latest_date = data2022.tail(1).iloc[0]['年月日']
    day_ago1 = (latest_date - pd.Timedelta(days=1))
    day_ago2 = (latest_date - pd.Timedelta(days=2))
    #data.reset_index()
    data2022['No'] = range(1, len(data2022.index) + 1)
    # 2021CSVデータを読み込む
  
    data2021 =  pd.read_csv('http://www.jepx.org/market/excel/spot_2021.csv',encoding="Shift-JIS")
    data2021['年月日'] = pd.to_datetime(data2021['年月日']).dt.date
    data2021 = data2021.rename(columns={ 'エリアプライス北陸(円/kWh)': 'Hokuriku'})
    data2021['Hokuriku'] = data2021['Hokuriku'].astype(float)
    #data.reset_index()
    data2021['No'] = range(1, len(data2021.index) + 1)
    # 2020CSVデータを読み込む
    data2020 = pd.read_csv('http://www.jepx.org/market/excel/spot_2020.csv',encoding="Shift-JIS")
    data2020['年月日'] = pd.to_datetime(data2020['年月日']).dt.date
    data2020 = data2020.rename(columns={ 'エリアプライス北陸(円/kWh)': 'Hokuriku'})
    data2020['Hokuriku'] = data2020['Hokuriku'].astype(float)
    #data.reset_index()
    data2020['No'] = range(1, len(data2020.index) + 1)
    # 2019CSVデータを読み込む
    data2019 = pd.read_csv('http://www.jepx.org/market/excel/spot_2019.csv',encoding="Shift-JIS")
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

    fig5.savefig(fy, format="png")
    fy.seek(0)
    img5 = base64.b64encode(fy.read()).decode()

    #2022最大最小値を取り出す
    text_max2022 = ""
    text_min2022 = ""
    max_price2022 = data2022['Hokuriku'].max()
    text_max2022 = str(round(max_price2022,2))
    min_price2022 = data2022['Hokuriku'].min()
    text_min2022 = str(round(min_price2022,2))
    #2021最大最小値を取り出す
    text_max2021 = ""
    text_min2021 = ""
    max_price2021 = data2021['Hokuriku'].max()
    text_max2021 = str(round(max_price2021,2))
    min_price2021 = data2021['Hokuriku'].min()
    text_min2021 = str(round(min_price2021,2))
    #2020最大最小値を取り出す
    text_max2020 = ""
    text_min2020 = ""
    max_price2020 = data2020['Hokuriku'].max()
    text_max2020 = str(round(max_price2020,2))
    min_price2020 = data2020['Hokuriku'].min()
    text_min2020 = str(round(min_price2020,2))
    #2019最大最小値を取り出す
    text_max2019 = ""
    text_min2019 = ""
    max_price2019 = data2019['Hokuriku'].max()
    text_max2019 = str(round(max_price2019,2))
    min_price2019 = data2019['Hokuriku'].min()
    text_min2019 = str(round(min_price2019,2))

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
    
    fig19.savefig(fy19, format="png")
    fy19.seek(0)
    img19 = base64.b64encode(fy19.read()).decode()


    # グラフをテンプレートに渡す
    return render_template('FY2019to2022.html',latest_date=latest_date,day_ago1=day_ago1,day_ago2=day_ago2,img5=img5,img22=img22,img21=img21,img20=img20,img19=img19,text_max2022=text_max2022,text_min2022=text_min2022,text_max2021=text_max2021,text_min2021=text_min2021,text_max2020=text_max2020,text_min2020=text_min2020,text_max2019=text_max2019,text_min2019=text_min2019)

## 実行
if __name__ == "__main__":
    app.run(debug=True)
