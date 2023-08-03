import pandas as pd
import numpy as np
import os
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
import aiohttp
import asyncio
import requests

KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"


# ----------------------------------   MAX PAIN ----------------------------------

def total_loss_on_strike(chain, expiry_price, opt_type):
    '''
    Get's the total loss at the given strike price
    '''
    # call options with strike price below the expiry price -> loss for option writers
    if opt_type == 'call':
        in_money = chain[chain['strike'] < expiry_price][["openInterest", "strike"]]
        in_money["Loss"] = (expiry_price - in_money['strike']) * in_money["openInterest"]

    if opt_type == 'put':
        in_money = chain[chain['strike'] > expiry_price][["openInterest", "strike"]]
        in_money["Loss"] = (in_money['strike'] - expiry_price) * in_money["openInterest"]

    return in_money["Loss"].sum()


def get_max_pain(ticker):
    current_price = yf.download(ticker)['Close'].iloc[-1]

    KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"

    unix_date_start_limit = datetime.datetime.now().timetuple()

    url = f"https://api.marketdata.app/v1/options/chain/{ticker}/?dte=30&token={KEY}"

    response_put_check = 0
    while (response_put_check != 200) and (response_put_check != 404):
        try:
            response_put = requests.request("GET", url)  # .json()
            response_put_check = response_put.status_code
            response_put = response_put.json()
        except:
            pass

    try:
        req_result = pd.DataFrame(response_put)
    except:
        req_result = pd.DataFrame(response_put, index=[0])

    if len(req_result) <= 1:
        unix_date = req_result['nextTime'][0]
        url = f"https://api.marketdata.app/v1/options/chain/{ticker}?&token={KEY}"
        response = requests.request("GET", url).json()
        req_result = pd.DataFrame(response)

    req_result['expiration'] = pd.to_datetime(req_result['expiration'], unit='s').dt.strftime('%Y-%m-%d')
    req_result['updated'] = pd.to_datetime(req_result['updated'], unit='s').dt.strftime('%Y-%m-%d')

    # ===========================================================================

    req_result['current_price'] = [current_price] * len(req_result)

    # call
    full_call = req_result[req_result['side'] == 'call'].reset_index(drop=True)

    # put
    full_put = req_result[req_result['side'] == 'put'].reset_index(drop=True)

    call_max_pain_list = []
    put_max_pain_list = []
    strike_list = []

    for i in range(len(full_put)):
        put_max_pain_list.append(total_loss_on_strike(full_put, full_put['strike'][i], 'put'))
        call_max_pain_list.append(total_loss_on_strike(full_call, full_put['strike'][i], 'call'))
        strike_list.append(full_put['strike'][i])

    max_pain = pd.DataFrame({'PUT': put_max_pain_list,
                             'CALL': call_max_pain_list,
                             'Strike': strike_list
                             })

    max_pain_value = (max_pain['PUT'] + max_pain['CALL']).min()

    max_pain['Sum'] = max_pain['PUT'] + max_pain['CALL']
    max_pain[max_pain['Sum'] == max_pain_value]
    max_pain_strike = max_pain[max_pain['Sum'] == max_pain_value]['Strike']

    print('max_pain_strike', ticker)
    print(max_pain_strike.values[0])

    return max_pain_strike.values[0]


# -=------------------------------  PCR ------------------------

async def get_market_data(session, url):
    async with session.get(url) as resp:
        try:
            market_data = await resp.json(content_type=None)
            print(market_data)
            quote_df = pd.DataFrame(market_data)
            quote_df['updated'] = pd.to_datetime(quote_df['updated'], unit='s').dt.strftime('%Y-%m-%d')
            quote_df['weighted'] = quote_df['mid'] * quote_df['volume']
            return quote_df[['updated', 'weighted']]
        except:
            pass


async def get_prime(contracts, start_date):
    return_df = pd.DataFrame()
    connector = aiohttp.TCPConnector(limit=10)
    # connector = aiohttp.TCPConnector(force_close=True)
    async with aiohttp.ClientSession(connector=connector) as session:

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

    finish_put_concat = pd.DataFrame()
    finish_call_concat = pd.DataFrame()

    for exp_date in req_result_exp.expirations.values.tolist():
        print(exp_date)
        date_exp_date = datetime.datetime.strptime(exp_date, '%Y-%m-%d') - relativedelta(days=+30)
        date_exp_date = date_exp_date.strftime('%Y-%m-%d')

        url = f"https://api.marketdata.app/v1/options/chain/{ticker}/?date={date_exp_date}&expiration={exp_date}&token={KEY}"

        response_put = requests.request("GET", url).json()

        try:
            req_result = pd.DataFrame(response_put)
        except:

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

        # all_chains = pd.concat([all_chains, req_result])

        req_result_put = req_result[req_result['side'] == 'put'].reset_index(drop=True)
        req_result_call = req_result[req_result['side'] == 'call'].reset_index(drop=True)

        print('req_result_put')
        print(req_result_put)

        print('event_loop')

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        print('req_result_put.values.tolist()')
        print(req_result_put['optionSymbol'].values.tolist())

        finish_put = asyncio.run(get_prime(req_result_put['optionSymbol'].values.tolist(), start_date))
        print('finish_put')
        print(finish_put)
        # finish_put = finish_put.groupby('updated').sum()

        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        finish_call = asyncio.run(get_prime(req_result_call['optionSymbol'].values.tolist(), start_date))
        # finish_call = finish_call.groupby('updated').sum()

        finish_put_concat = pd.concat([finish_put_concat, finish_put])
        finish_call_concat = pd.concat([finish_call_concat, finish_call])

    finish_put_concat = finish_put_concat.groupby('updated').sum()
    finish_call_concat = finish_call_concat.groupby('updated').sum()

    finish_put_concat['Date'] = finish_put_concat.index.tolist()
    finish_call_concat['Date'] = finish_call_concat.index.tolist()
    finish_put_concat['weighted_put'] = finish_put_concat['weighted']
    finish_call_concat['weighted_call'] = finish_call_concat['weighted']

    pcr_df = finish_call_concat.merge(finish_put_concat, how='right', on=['Date'])

    pcr_df['pcr'] = pcr_df['weighted_put'] / pcr_df['weighted_call']
    pcr_df = pcr_df.set_index('Date')
    pcr_df = pcr_df.dropna().rolling(window=21).mean()

    return pcr_df


def run_market_data(start_row):
    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("ETF")
    worksheet_spark = gc.open("IBKR").worksheet("sparkline")

    worksheet_df_len = pd.DataFrame(worksheet.get_all_records())[:-1]

    for i in range(len(worksheet_df_len))[start_row:]:  # указать с какой строки начать сбор [2:]

        # # ================ раббота с таблицей============================================
        gc = gd.service_account(filename='Seetus.json')
        worksheet = gc.open("IBKR").worksheet("ETF")
        worksheet_spark = gc.open("IBKR").worksheet("sparkline")

        worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]

        # заполняем столбцы с формулами
        for k in range(len(worksheet_df_len)):
            worksheet_df['CURRENT PRICE'].iloc[k] = f'=GOOGLEFINANCE(A{k + 2},"price")'
            worksheet_df['WEIGHT PCR sparkline'].iloc[k] = f'=sparkline(sparkline!B{k + 1}:W{k + 1})'
            # worksheet_df['% BETA DELTA'].iloc[k] = f'=C{k + 2}/$C$27'

        print(worksheet_df)

        tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]
        print(f'---------    {tick}')

        # ----------- MAX PAIN -----------------

        print('max_pain_START')
        max_pain_value = get_max_pain(tick)

        # worksheet_df['WEIGHT PCR SIGNAL'].iloc[i] = pcr_signal
        worksheet_df['MAX PAIN month'].iloc[i] = max_pain_value
        # worksheet_df['WEIGHT PCR SIGNAL'].iloc[i] = pcr_signal
        # worksheet_df['WEIGHT PCR sparkline'].iloc[i] = f'=sparkline(sparkline!B{i + 1}:W{i + 1})'

        worksheet_df = worksheet_df.fillna(0)
        worksheet_df.to_csv('worksheet_df.csv', index=False)
        worksheet_df = pd.read_csv('worksheet_df.csv')
        worksheet_df = worksheet_df.fillna(0)
        # # ===================================  запись в таблицу ================================================
        worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(),
                         value_input_option='USER_ENTERED')

    for i in range(len(worksheet_df_len)):  # указать с какой строки начать сбор [2:]

        # # ================ раббота с таблицей============================================
        gc = gd.service_account(filename='Seetus.json')
        worksheet = gc.open("IBKR").worksheet("ETF")
        worksheet_spark = gc.open("IBKR").worksheet("sparkline")

        worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]

        # заполняем столбцы с формулами
        for k in range(len(worksheet_df_len)):
            worksheet_df['CURRENT PRICE'].iloc[k] = f'=GOOGLEFINANCE(A{k + 2},"price")'
            worksheet_df['WEIGHT PCR sparkline'].iloc[k] = f'=sparkline(sparkline!B{k + 1}:W{k + 1})'
            # worksheet_df['% BETA DELTA'].iloc[k] = f'=C{k + 2}/$C$27'

        print(worksheet_df)

        have_strategist = worksheet_df[worksheet_df['O_S Plot Link'] != 'Empty']

        print('have_strategist')
        print(have_strategist)

        tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]

        if tick not in have_strategist['ETF COMPLEX POSITION'].values.tolist():
            print('AAAAAAAA')
            print(tick)

            print(f'---------    {tick}')
            # -----------  PCR -----------------
            start_date = datetime.datetime.now() - relativedelta(months=+3)
            pcr_df = m_d_func(tick, start_date)
            pcr_df['pcr_SMA_20'] = pcr_df['pcr'].rolling(window=20).mean()

            pcr_signal = 'UP'
            if pcr_df['pcr_SMA_20'].iloc[-1] < pcr_df['pcr'].iloc[-1]:
                pcr_signal = 'DOWN'

            print('pcr')
            print(pcr_df)

            worksheet_spark.update(f'A{i + 1}', [[tick] + pcr_df['pcr'].dropna()[-22:].values.tolist()])

            # worksheet_df['WEIGHT PCR SIGNAL'].iloc[i] = pcr_signal
            # worksheet_df['MAX PAIN month'].iloc[i] = max_pain_value
            worksheet_df['WEIGHT PCR SIGNAL'].iloc[i] = pcr_signal
            worksheet_df['WEIGHT PCR sparkline'].iloc[i] = f'=sparkline(sparkline!B{i + 1}:W{i + 1})'

            worksheet_df = worksheet_df.fillna(0)
            worksheet_df.to_csv('worksheet_df.csv', index=False)
            worksheet_df = pd.read_csv('worksheet_df.csv')
            worksheet_df = worksheet_df.fillna(0)
            # # ===================================  запись в таблицу ================================================
            worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(),
                             value_input_option='USER_ENTERED')
