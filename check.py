
import pandas as pd

import matplotlib.pyplot as plt
import os
import io

io = io.BytesIO()

data = pd.read_csv('http://www.jepx.org/market/excel/spot_2022.csv',encoding="Shift-JIS")
data['年月日'] = pd.to_datetime(data['年月日']).dt.date
today = pd.to_datetime('today').date()
yesterday = (today - pd.Timedelta(days=1))
data = data[data['年月日'] == (today - pd.Timedelta(days=1))]
print(data)
print(today)
print(yesterday)
print(today - pd.Timedelta(days=1))

x = data['時刻コード']
y = data['システムプライス(円/kWh)']

fig, ax = plt.subplots(tight_layout=True)
ax.plot(x, y,color="blue")
ax.set_xlabel("Year")
ax.set_ylabel("Price")
title_name = str(yesterday) + "  price"
ax.set_title(title_name)
ax.grid(True)
ax.set_xlabel("Times of Day(48 frames)")
ax.set_ylabel("Price")
plt.xticks(range(0, 48+1, 2))
ax.set_xlim(0, 48)

# グラフ上に数値を表示する
for i, j in zip(x, y):
    ax.annotate(str(round(j,2)), xy=(i, j), xycoords='data', xytext=(+1, +3),
            textcoords='offset points', fontsize=5)

plt.show()

