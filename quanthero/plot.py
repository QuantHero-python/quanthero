import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def plot_klines(ohlcv,overlaps={},figures={},entries=None,exits=None,start_date=None,end_date=None,title=None,theme='dark'):

    start_date = start_date or pd.Timestamp.now() - pd.DateOffset(months=8)
    template,bg_color,colors = ('plotly_dark','#1a1b20',['#ed3844','#079a82']) if theme == 'dark' else ('plotly_white','#fff',['#f05351','#27a69a'])

    s = ohlcv.copy().loc[start_date:end_date]

    fig = make_subplots(
        rows=3, cols=1, 
        shared_xaxes=True, 
        vertical_spacing=0.03,
        row_heights=[0.8, 0.2,0.2]
    )

    fig.add_trace(
        go.Candlestick(
            x=s.index, open=s['open'], high=s['high'], low=s['low'], close=s['close'],
            increasing_line_color=colors[0], decreasing_line_color=colors[1],#line=dict(width=1,),
            name='kline'
        ),
        row=1, col=1
    )

    for key,value in overlaps.items():

        fig.add_trace(
            go.Scatter(x=s.index,y=value.reindex(s.index),mode='lines',name=key,),
            row=1,col=1
        )

    # entries
    if entries is not None:
        fig.add_trace(
            go.Scatter(
                x=s.index,y=ohlcv.low[entries].reindex(s.index) * .95,mode='markers',name='entries',
                marker=dict(symbol="triangle-up",size=14,color="#ea4336",opacity=.6)
            ),
            row=1,col=1
        )
    # exits
    if exits is not None:
        fig.add_trace(
            go.Scatter(
                x=s.index,y=ohlcv.high[exits].reindex(s.index) * 1.05,mode='markers',name='exits',
                marker=dict(symbol="triangle-down",size=14,color="#37b13f",opacity=.6)
            ),
            row=1,col=1
        )

    vol_colors = np.where(s['close'] >= s['open'], colors[0], colors[1])
    fig.add_trace(
        go.Bar(x=s.index, y=s['volume'], marker_color=vol_colors, name='volume',opacity=.5),
        row=2, col=1
    )

    for key,value in figures.items():

        fig.add_trace(
            go.Scatter(x=s.index,y=value.reindex(s.index),mode='lines',name=key,line=dict(width=1)),
            row=3,col=1
        )

    breaks = dict(values=s.reindex(pd.date_range(s.index[0], s.index[-1])).pipe(lambda df: df[df['close'].isna()]).index)
    fig.update_xaxes(rangebreaks=[breaks])

    fig.update_layout(
        width=1040, 
        height=600, 
        title=title,
        template=template,
        plot_bgcolor=bg_color, 
        paper_bgcolor=bg_color,
        xaxis_rangeslider_visible=False,
        margin=dict(l=50, r=50, t=50, b=50)
    )

    fig.data[0].increasing.fillcolor = colors[0]
    fig.data[0].increasing.line.color = colors[0]
    fig.data[0].decreasing.fillcolor = colors[1]
    fig.data[0].decreasing.line.color = colors[1]

    fig.show()