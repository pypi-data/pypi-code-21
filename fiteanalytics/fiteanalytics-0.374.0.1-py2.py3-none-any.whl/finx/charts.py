#! python
"""
author: Dick Mule
purpose: Chart stock option positions
"""
import plotly.graph_objs as go
from plotly.offline import init_notebook_mode, iplot
import pandas as pd
import numpy as np
import random
import requests
from IPython.display import display, HTML
from sklearn import linear_model
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose
import inspect

def option_position(options_df):
    init_notebook_mode(connected=True)
    r = lambda: random.randint(0, 255)
    random_line_color = lambda: '#{}02X{}02X{}02X'.format(r(), r(), r())
    trace_data = []
    xmin = options_df['strike_price'].min()*.9
    xmax = options_df['strike_price'].max()*1.1
    x = np.arange(xmin, xmax, (xmax-xmin)/200)
    y_cumulative = np.zeros(len(x))
    for index, option in options_df.iterrows():
        strike_price = option['strike_price']
        option_side = option['option_side']
        transaction_side = option['transaction_side']
        ticker = option['ticker']
        if option_side is 'call':
            y = [max(0, xi - strike_price) for xi in x]
        else:
            y = [max(0, strike_price - xi) for xi in x]
        if transaction_side is 'short':
            y = np.zeros(len(y))-y
        y_cumulative += y
        trace = go.Scatter(
                    x=x,
                    y=y,
                    name=transaction_side+' '+option_side+' with strike: '+str(strike_price),
                    mode='markers',
                    opacity=0.3,
                    marker=dict(
                        size=4,
                        line=dict(color=random_line_color())))
        trace_data.append(trace)
    cum_trace = go.Scatter(
                    x=x,
                    y=y_cumulative,
                    name='cumulative position',
                    mode='markers',
                    marker=dict(
                        size=8,
                        line=dict(color=random_line_color())))
    trace_data.append(cum_trace)
    layout = dict(title="Option Position for ticker: "+ticker,
                  xaxis=dict(title='stock price'),
                  yaxis=dict(title='profit'))
    fig = dict(data=trace_data, layout=layout)
    iplot(fig,
          show_link=False,
          config=dict(displaylogo=False, modeBarButtonsToRemove=['sendDataToCloud']))
    return None

def max_pain_vs_close_price(finx_key, ticker, expiry_date):
    url = 'http://finx.io/rest/stock/observations/maxpain/chart/'
    payload = dict(ticker=str(ticker),
                   expiry_date=str(expiry_date),
                   finx_key=finx_key)
    response = requests.get(url, params=payload)
    if not response.ok:
        return response.text
    try:
        df = pd.read_json(response.text)
        if df.empty:
            return 'no data: ticker is valid, however, there is currently no data matching the ticker'
        df = df.sort_index().loc[df.max_pain_price != 0.5]
        init_notebook_mode(connected=True)
        r = lambda: random.randint(0, 255)
        random_line_color = lambda: '#{}02X{}02X{}02X'.format(r(), r(), r())
        trace1 = go.Scatter(x=df.index,
                            y=df.max_pain_price,
                            name='max_pain_price',
                            mode='line',
                            opacity=1,
                            marker=dict(
                                size=6,
                                line=dict(color=random_line_color()))
                            )
        trace2 = go.Scatter(x=df.index,
                            y=df.close_price,
                            name='close_price',
                            mode='line',
                            opacity=1,
                            marker=dict(
                                size=6,
                                line=dict(color=random_line_color()))
                            )
        trace3 = go.Bar(x=df.index,
                        y=df.open_interest,
                        yaxis='y3',
                        name='open_interest',
                        opacity=0.6)
        trace4 = go.Bar(x=df.index,
                        y=df.volume,
                        yaxis='y3',
                        name='volume',
                        opacity=0.6)
        trace_data = [trace1, trace2, trace3, trace4]
        layout = go.Layout(
            title='Max Pain vs. Close Price',
            xaxis=dict(
                title='Observation Date',
                domain=[.10, .9],
            ),
            yaxis=dict(
                title='Price'
            ),
            yaxis3=dict(
                title='Open Interest',
                anchor='x',
                overlaying='y',
                side='right',
            ),
        )
        fig = go.Figure(data=trace_data, layout=layout)
        iplot(fig, show_link=False, config=dict(displaylogo=False,
                                                modeBarButtonsToRemove=['sendDataToCloud']))
        return None
    except:
        return 'can not make chart: data not aligned properly'
