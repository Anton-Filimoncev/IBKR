import requests
import numpy as np
import pandas as pd
import yfinance as yf
import datetime
import time
import sys, os
import pickle
import aiohttp
import asyncio
from dateutil.relativedelta import relativedelta
from sklearn.linear_model import LinearRegression
from arch import arch_model
from numpy import trapz
from multiprocessing import Pool
from scipy.optimize import Bounds
from scipy.optimize import minimize
from sklearn.metrics import mean_squared_error
import math
import mibian
import calendar
import statistics
import scipy.stats
import matplotlib.pyplot as plt

# KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"
KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"


#
#
async def get_market_data(session, url):
    async with session.get(url) as resp:
        try:
            market_data = await resp.json(content_type=None)
            quote_df = pd.DataFrame(market_data)
            quote_df['updated'] = pd.to_datetime(quote_df['updated'], unit='s').dt.strftime('%Y-%m-%d')
            quote_df['weighted'] = quote_df['mid'] * quote_df['volume']
            return quote_df[['updated', 'weighted']]
        except:
            pass


async def get_prime(contracts):
    return_df = pd.DataFrame()

    async with aiohttp.ClientSession() as session:

        tasks = []
        for contract in contracts:
            url = f"https://api.marketdata.app/v1/options/quotes/{contract}/?from={start_date}&token={KEY}"
            tasks.append(asyncio.create_task(get_market_data(session, url)))

        original_primes = await asyncio.gather(*tasks)

        for prime in original_primes:
            return_df = pd.concat([return_df, prime], axis=0)

    return_df = return_df.reset_index(drop=True)

    return return_df


def m_d_func(ticker, start_date):
    start_date_request = start_date.strftime('%Y-%m-%d')

    # ==========================================================

    url_exp = f"https://api.marketdata.app/v1/options/expirations/{ticker}/?date={start_date_request}&token={KEY}"
    response_exp = requests.request("GET", url_exp).json()
    try:
        req_result_exp = pd.DataFrame(response_exp)
    except:
        print('exceptus')
        req_result_exp = pd.DataFrame(response_exp, index=[0])

    if len(req_result_exp) <= 1:
        print('except')
        unix_date = req_result_exp['prevTime'][0]
        url = f"https://api.marketdata.app/v1/options/expirations/{ticker}/?date={unix_date}&token={KEY}"
        response_exp = requests.request("GET", url).json()
        req_result_exp = pd.DataFrame(response_exp)


    all_chains = pd.DataFrame()

    for exp_date in req_result_exp.expirations.values.tolist():
        date_exp_date = datetime.datetime.strptime(exp_date, '%Y-%m-%d') - relativedelta(days=+30)
        date_exp_date = date_exp_date.strftime('%Y-%m-%d')

        url = f"https://api.marketdata.app/v1/options/chain/{ticker}/?date={date_exp_date}&expiration={exp_date}&token={KEY}"

        response_put = requests.request("GET", url).json()


        try:
            req_result = pd.DataFrame(response_put)
        except:
            print('exceptus')
            req_result = pd.DataFrame(response_put, index=[0])

        if len(req_result) <= 1:
            print('except')
            unix_date = req_result['prevTime'][0]
            print('unix_date')
            print(unix_date)
            url = f"https://api.marketdata.app/v1/options/chain/{ticker}/?date={unix_date}&token={KEY}"
            response = requests.request("GET", url).json()
            req_result = pd.DataFrame(response)

        req_result['expiration'] = pd.to_datetime(req_result['expiration'], unit='s').dt.strftime('%Y-%m-%d')

        all_chains = pd.concat([all_chains, req_result])


    req_result_put = all_chains[all_chains['side'] == 'put'].reset_index(drop=True)
    req_result_call = all_chains[all_chains['side'] == 'call'].reset_index(drop=True)

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    finish_put = asyncio.run(get_prime(req_result_put['optionSymbol'].values.tolist()))
    finish_put = finish_put.groupby('updated').sum()

    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    finish_call = asyncio.run(get_prime(req_result_call['optionSymbol'].values.tolist()))
    finish_call = finish_call.groupby('updated').sum()

    finish_put['Date'] = finish_put.index.tolist()
    finish_call['Date'] = finish_call.index.tolist()
    finish_put['weighted_put'] = finish_put['weighted']
    finish_call['weighted_call'] = finish_call['weighted']

    pcr_df = finish_call.merge(finish_put, how='right', on=['Date'])

    pcr_df['pcr'] = pcr_df['weighted_put']/pcr_df['weighted_call']
    pcr_df = pcr_df.set_index('Date')
    pcr_df = pcr_df.dropna().rolling(window=21).mean()

    return pcr_df

    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("ETF")
    worksheet_spark = gc.open("IBKR").worksheet("sparkline")

    worksheet_df_len = pd.DataFrame(worksheet.get_all_records())[:-1]

    print(worksheet_df_len)

    for i in range(len(worksheet_df_len))[7:8]:

        # # ================ раббота с таблицей============================================
        gc = gd.service_account(filename='Seetus.json')
        worksheet = gc.open("IBKR").worksheet("ETF")
        worksheet_spark = gc.open("IBKR").worksheet("sparkline")

        worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]

        # заполняем столбцы с формулами
        for k in range(len(worksheet_df_len)):
            worksheet_df['CURRENT PRICE'].iloc[k] = f'=GOOGLEFINANCE(A{k + 2},"price")'
            worksheet_df['WEIGHT PCR sparkline'].iloc[k] = f'=sparkline(sparkline!B{k + 1}:W{k + 1})'
            worksheet_df['% BETA DELTA'].iloc[k] = f'=C{k + 2}/$C$27'

        print(worksheet_df)

        tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]

        print(f'-----------  {tick} -----------------')

        yahoo_data = yf.download(tick)

        # -----------  PCR -----------------
        # start_date = '2022-01-01'
        start_date = datetime.datetime.now() - relativedelta(months=+6)

        # print(tickers_list)
        tickers_list = ['EWZ']
        pcr_df = m_d_func(tick, start_date)


        pcr_df['pcr_SMA_20'] = pcr_df['pcr'].rolling(window=20).mean()

        pcr_signal = 'UP'
        if pcr_df['pcr_SMA_20'].iloc[-1] < pcr_df['pcr'].iloc[-1]:
            pcr_signal = 'DOWN'

        print('pcr')
        print(pcr_df)

        worksheet_spark.update(f'A{i + 1}', [[tick] + pcr_df['pcr'].dropna()[-22:].values.tolist()])

        # -------

        sma_20, sma_100, rsi = get_tech_data(yahoo_data)

        worksheet_df['RSI 14'].iloc[i] = rsi
        worksheet_df['CURRENT PRICE'].iloc[i] = f'=GOOGLEFINANCE(A{i + 2},"price")'
        worksheet_df['WEIGHT PCR SIGNAL'].iloc[i] = pcr_signal
        worksheet_df['WEIGHT PCR sparkline'].iloc[i] = f'=sparkline(sparkline!B{i + 1}:W{i + 1})'
        worksheet_df['SMA 20'].iloc[i] = sma_20
        worksheet_df['SMA 100'].iloc[i] = sma_100

        worksheet_df = worksheet_df.fillna(0)
        worksheet_df.to_csv('worksheet_df.csv', index=False)
        worksheet_df = pd.read_csv('worksheet_df.csv')
        worksheet_df = worksheet_df.fillna(0)
        # # ===================================  запись в таблицу ================================================
        worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(),
                         value_input_option='USER_ENTERED')





