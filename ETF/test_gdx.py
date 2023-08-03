import pandas as pd
import numpy as np
import os
import requests
import time
import pickle
import gspread as gd
from ib_insync import *
from scipy import stats
from sklearn import mixture as mix
import yfinance as yf
import pandas_ta as pta
import datetime
from dateutil.relativedelta import relativedelta
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange, SecType, StockReqType
from datetime import date
import asyncio
import aiohttp

ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=12)  # 7497

except:
    ib.connect('127.0.0.1', 7497, clientId=12)

IV_list = []
hist_list = []
iv_hist_list = []
vega_risk_list = []

ticker = 'IWM'

try:
    print('==========================================   ', ticker,
          '  =============================================')

    #  ========================================  получение волатильности
    contract = Stock(ticker, 'SMART', 'USD')
    bars = ib.reqHistoricalData(
        contract, endDateTime='', durationStr='365 D',
        barSizeSetting='1 day', whatToShow='OPTION_IMPLIED_VOLATILITY', useRTH=True)

    print(bars)
    df = util.df(bars)

    print('df')
    print(df)

    # IV_list.append(round(df_iv.close.iloc[-1], 2) * 100)

    vega_risk = round(df.close.iloc[-1] - df[-22:].close.min(), 2)
    # vega_risk_list.append(vega_risk * 100)

except:
    df = pd.DataFrame()