import pandas as pd
import numpy as np
import os
import time
import pickle
import gspread as gd
from ib_insync import *
from scipy import stats
import yfinance as yf
import pandas_ta as pta
import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from concurrent.futures.thread import ThreadPoolExecutor
import os
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
import pickle

def get_tech_data(df):
    df['RSI'] = pta.rsi(df['Close'])
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_100'] = df['Close'].rolling(window=100).mean()

    sma_20 = df['SMA_20'].dropna().iloc[-1]
    sma_100 = df['SMA_100'].dropna().iloc[-1]
    rsi = df['RSI'].dropna().iloc[-1]

    return sma_20, sma_100, rsi

def trend(price_df):
    trend = ''
    current_price = price_df['Close'].iloc[-1]
    SMA_20 = price_df['Close'].rolling(window=20).mean().iloc[-1]
    SMA_100 = price_df['Close'].rolling(window=100).mean().iloc[-1]

    if current_price > SMA_100 and current_price > SMA_20 and SMA_20 > SMA_100:
        trend = 'Strong Uptrend'
    if current_price > SMA_100 and current_price > SMA_20 and SMA_20 < SMA_100:
        trend = 'Uptrend'
    if current_price > SMA_100 and current_price < SMA_20 and SMA_20:
        trend = 'Weak Uptrend'
    if current_price < SMA_100 and current_price < SMA_20 and SMA_20 < SMA_100:
        trend = 'Strong Downtrend'
    if current_price < SMA_100 and current_price < SMA_20 and SMA_20 > SMA_100:
        trend = 'Downtrend'
    if current_price < SMA_100 and current_price > SMA_20:
        trend = 'Weak downtrend'

    return trend

def run_tech():
    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("ETF")
    worksheet_df_len = pd.DataFrame(worksheet.get_all_records())[:-1]
    worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]

    for i in range(len(worksheet_df_len)):

        # заполняем столбцы с формулами
        for k in range(len(worksheet_df_len)):
            worksheet_df['CURRENT PRICE'].iloc[k] = f'=GOOGLEFINANCE(A{k + 2},"price")'
            worksheet_df['WEIGHT PCR sparkline'].iloc[k] = f'=sparkline(sparkline!B{k + 1}:W{k + 1})'
            # worksheet_df['% BETA DELTA'].iloc[k] = f'=C{k + 2}/$C$27'

        print(worksheet_df)

        tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]
        print(f'---------    {tick}')
        yahoo_data = yf.download(tick)
        trend_signal = trend(yahoo_data)
        sma_20, sma_100, rsi = get_tech_data(yahoo_data)

        worksheet_df['TREND'].iloc[i] = trend_signal
        worksheet_df['RSI 14'].iloc[i] = rsi
        worksheet_df['SMA 20'].iloc[i] = sma_20
        worksheet_df['SMA 100'].iloc[i] = sma_100

    worksheet_df = worksheet_df.fillna(0)
    worksheet_df.to_csv('worksheet_df.csv', index=False)
    worksheet_df = pd.read_csv('worksheet_df.csv')
    worksheet_df = worksheet_df.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(),
                     value_input_option='USER_ENTERED')

