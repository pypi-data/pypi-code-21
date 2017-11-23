# coding=utf-8
#

import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import miceshare.db.sqlite_util as sql_util
import matplotlib.ticker as ticker


def build_df(r):
    s = json.loads(r)
    bsentrust = s['bsentrust']
    day = s['day']
    code = s['code']

    df = pd.DataFrame(bsentrust)
    cols = ['time', 'u1', 'u2', 'buy', 'sell']
    df.columns = cols
    df['std_sell'] = df['sell'].rolling(5).std()
    df['std_buy'] = df['buy'].rolling(5).std()
    # df['mean_sell'] = df['std_sell'].rolling(5).mean()
    # df['mean_buy'] = df['std_buy'].rolling(5).mean()
    return df


def plot_bs(code):
    data_type = 'bs'
    conn = sql_util.login(sql_util.get_db_name('bs'))
    table_name = 'bs_20171110'
    r = sql_util.query(conn, table_name, [code])
    df = build_df(r[1])
    N = len(df)
    ind = np.arange(N)
    print(N)

    def format_date(x, pos=None):
        thisind = np.clip(int(x + 0.5), 0, N - 1)
        return df['time'][thisind]

    fig, axes = plt.subplots(ncols=2, figsize=(8, 4))
    ax = axes[0]
    ax.plot(ind, df['sell'], label='sell')
    ax.plot(ind, df['buy'], label='buy')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    fig.autofmt_xdate()
    ax.legend(loc='best')
    ax.set_xlim(10, 230)
    plt.title(code)

    ax = axes[1]
    ax.plot(ind, df['std_sell'], label='std_sell')
    # ax.plot(ind, df['mean_sell'], label='mean_sell')
    ax.plot(ind, df['std_buy'], label='std_buy')
    # ax.plot(ind, df['mean_buy'], label='mean_buy')
    ax.xaxis.set_major_formatter(ticker.FuncFormatter(format_date))
    fig.autofmt_xdate()
    # ax.set_xlim(10, 230)
    # ax.set_ylim(-1000, 1500000)
    ax.legend(loc='best')
    plt.savefig('d:/tmp/' + table_name)
    plt.show()


if __name__ == '__main__':
    plot_bs('601108')
