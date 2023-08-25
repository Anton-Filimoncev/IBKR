import pandas as pd
import numpy as np
import yfinance as yf
import requests
import math
import datetime
import time
import datetime as dt
from scipy.signal import argrelextrema
from dateutil.relativedelta import relativedelta
import gspread as gd
pd.options.mode.chained_assignment = None  # default='warn'
from scipy import stats
import pandas_ta as pta
import os
from time import sleep
import pickle
import mibian

def get_abs_return(price_array, type_option, days_to_exp, history_vol, current_price, strike, prime, vol_opt):
    put_price_list = []
    call_price_list = []
    proba_list = []
    price_gen_list = []

    for stock_price_num in range(len(price_array)):
        try:
            P_below = stats.norm.cdf(
                (np.log(price_array[stock_price_num] / current_price) / (
                        history_vol * math.sqrt(days_to_exp / 365))))
            P_current = stats.norm.cdf(
                (np.log(price_array[stock_price_num + 1] / current_price) / (
                        history_vol * math.sqrt(days_to_exp / 365))))
            proba_list.append(P_current - P_below)
            c = mibian.BS([price_array[stock_price_num + 1], strike, 0.45, 1], volatility=vol_opt * 100)
            put_price_list.append(c.putPrice)
            call_price_list.append(c.callPrice)
            price_gen_list.append(price_array[stock_price_num + 1])
        except:
            pass

    put_df = pd.DataFrame({
        'gen_price': price_gen_list,
        'put_price': put_price_list,
        'call_price': call_price_list,
        'proba': proba_list,

    })

    put_df['return'] = (put_df['put_price'] - prime)

    if type_option == 'Short':
        return ((prime - put_df['put_price']) * put_df['proba']).sum()

    if type_option == 'Long':
        return ((put_df['put_price'] - prime) * put_df['proba']).sum()

def trend(price_df):
    trend = ''
    current_price = price_df['Close'].iloc[-1]
    SMA_20 = price_df['Close'].rolling(window=20).mean().iloc[-1]
    SMA_100 = price_df['Close'].rolling(window=100).mean().iloc[-1]
    RSI = pta.rsi(price_df['Close']).iloc[-1]

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

    return trend, RSI

def expected_return_calc(vol_put_short, vol_put_long, current_price, history_vol, days_to_exp, strike_put_long, strike_put_short, prime_put_long, prime_put_short):

    # print('expected_return CALCULATION ...')

    price_array = np.arange(current_price - current_price / 2, current_price + current_price, 0.2)
    # print('price_array', price_array)
    short_finish = get_abs_return(price_array, 'Short', days_to_exp, history_vol, current_price, strike_put_short,
                                prime_put_short,
                                vol_put_short)


    long_finish = get_abs_return(price_array, 'Long', days_to_exp, history_vol, current_price, strike_put_long,
                                 prime_put_long,
                                 vol_put_long)

    expected_return = (short_finish + long_finish) * 100

    return expected_return


if __name__ == '__main__':
    # # ======================================= SAXO_long_RISK ============================================

    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("SAXO_long_RISK")
    worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace('', np.nan)
    worksheet_df = worksheet_df[:len(worksheet_df['Тикер'].dropna())]

    worksheet_df_FORMULA = pd.DataFrame(worksheet.get_all_records(value_render_option='FORMULA')).replace('', np.nan)
    worksheet_df_FORMULA = worksheet_df_FORMULA[:len(worksheet_df_FORMULA['Тикер'].dropna())]

    for i in range(len(worksheet_df)):

        ticker = worksheet_df['Тикер'].iloc[i]
        yahoo_data = yf.download(ticker)
        trend_val, RSI = trend(yahoo_data)
        worksheet_df_FORMULA['TREND'].iloc[i] = trend_val

    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    worksheet_df_FORMULA.to_csv('worksheet_df.csv', index=False)
    worksheet_df_FORMULA = pd.read_csv('worksheet_df.csv')
    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df_FORMULA.columns.values.tolist()] + worksheet_df_FORMULA.values.tolist(),
                     value_input_option='USER_ENTERED')

    # # ======================================= SAXO_long_PUT ============================================

    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("SAXO_long_PUT")
    worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace('', np.nan)
    worksheet_df = worksheet_df[:len(worksheet_df['Тикер'].dropna())]

    worksheet_df_FORMULA = pd.DataFrame(worksheet.get_all_records(value_render_option='FORMULA')).replace('', np.nan)
    worksheet_df_FORMULA = worksheet_df_FORMULA[:len(worksheet_df_FORMULA['Тикер'].dropna())]

    print('worksheet_df')
    print(worksheet_df)

    for j in range(len(worksheet_df)):

        ticker = worksheet_df['Тикер'].iloc[j]
        yahoo_data = yf.download(ticker)
        print(yahoo_data)
        trend_val, RSI = trend(yahoo_data)


        current_price = worksheet_df['Рыночная цена'].iloc[j]
        history_vol = worksheet_df['HV 200'].iloc[j]
        vol_put_short = worksheet_df['IV short'].iloc[j]
        vol_put_long = worksheet_df['IV long'].iloc[j]
        days_to_exp = worksheet_df['Осталось дней до закрытия'].iloc[j]
        strike_put_short = worksheet_df['STRIKE шорт'].iloc[j]
        strike_put_long = worksheet_df['STRIKE лонг'].iloc[j]
        prime_put_short = worksheet_df['Премия шорт'].iloc[j]
        prime_put_long = worksheet_df['Премия лонг'].iloc[j]
        position_num = worksheet_df['Количество позиций лонг'].iloc[j]

        print(vol_put_short)
        print(vol_put_long)
        print(current_price)
        print(history_vol)
        print(days_to_exp)
        print(strike_put_long)
        print(strike_put_short)
        print(prime_put_long)
        print(prime_put_short)

        expected_return = expected_return_calc(vol_put_short, vol_put_long, current_price, history_vol, days_to_exp, strike_put_long, strike_put_short, prime_put_long, prime_put_short)
        #
        print('expected_return', expected_return)

        worksheet_df_FORMULA['TREND'].iloc[j] = trend_val
        worksheet_df_FORMULA['Expected Return'].iloc[j] = expected_return

    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    worksheet_df_FORMULA.to_csv('worksheet_df.csv', index=False)
    worksheet_df_FORMULA = pd.read_csv('worksheet_df.csv')
    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df_FORMULA.columns.values.tolist()] + worksheet_df_FORMULA.values.tolist(),
                     value_input_option='USER_ENTERED')


    # # ======================================= SAXO_short_PUT ============================================

    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("SAXO_short_PUT")
    worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace('', np.nan)
    worksheet_df = worksheet_df[:len(worksheet_df['Тикер'].dropna())]

    worksheet_df_FORMULA = pd.DataFrame(worksheet.get_all_records(value_render_option='FORMULA')).replace('', np.nan)
    worksheet_df_FORMULA = worksheet_df_FORMULA[:len(worksheet_df_FORMULA['Тикер'].dropna())]

    print('worksheet_df')
    print(worksheet_df)

    for j1 in range(len(worksheet_df)):

        ticker = worksheet_df['Тикер'].iloc[j1]
        yahoo_data = yf.download(ticker)
        print(yahoo_data)
        trend_val, RSI = trend(yahoo_data)

        worksheet_df_FORMULA['TREND'].iloc[j1] = trend_val

    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    worksheet_df_FORMULA.to_csv('worksheet_df.csv', index=False)
    worksheet_df_FORMULA = pd.read_csv('worksheet_df.csv')
    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df_FORMULA.columns.values.tolist()] + worksheet_df_FORMULA.values.tolist(),
                     value_input_option='USER_ENTERED')


    # # ======================================= SAXO_short_CALL ============================================

    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("SAXO_short_CALL")
    worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace('', np.nan)
    worksheet_df = worksheet_df[:len(worksheet_df['Тикер'].dropna())]

    worksheet_df_FORMULA = pd.DataFrame(worksheet.get_all_records(value_render_option='FORMULA')).replace('', np.nan)
    worksheet_df_FORMULA = worksheet_df_FORMULA[:len(worksheet_df_FORMULA['Тикер'].dropna())]

    print('worksheet_df')
    print(worksheet_df)

    for j2 in range(len(worksheet_df)):

        ticker = worksheet_df['Тикер'].iloc[j]
        yahoo_data = yf.download(ticker)
        print(yahoo_data)
        trend_val, RSI = trend(yahoo_data)


        current_price = worksheet_df['Рыночная цена'].iloc[j2]
        history_vol = worksheet_df['HV 200'].iloc[j2]
        vol_put_short = worksheet_df['IV short'].iloc[j2]
        vol_put_long = worksheet_df['IV long'].iloc[j2]
        days_to_exp = worksheet_df['Осталось дней до закрытия'].iloc[j2]
        strike_put_short = worksheet_df['STRIKE шорт'].iloc[j2]
        strike_put_long = worksheet_df['STRIKE лонг'].iloc[j2]
        prime_put_short = worksheet_df['Премия шорт'].iloc[j2]
        prime_put_long = worksheet_df['Премия лонг'].iloc[j2]
        position_num = worksheet_df['Количество позиций лонг'].iloc[j2]

        print(vol_put_short)
        print(vol_put_long)
        print(current_price)
        print(history_vol)
        print(days_to_exp)
        print(strike_put_long)
        print(strike_put_short)
        print(prime_put_long)
        print(prime_put_short)

        expected_return = expected_return_calc(vol_put_short, vol_put_long, current_price, history_vol, days_to_exp, strike_put_long, strike_put_short, prime_put_long, prime_put_short)
        #
        print('expected_return', expected_return)

        worksheet_df_FORMULA['TREND'].iloc[j2] = trend_val
        worksheet_df_FORMULA['Expected Return'].iloc[j2] = expected_return

    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    worksheet_df_FORMULA.to_csv('worksheet_df.csv', index=False)
    worksheet_df_FORMULA = pd.read_csv('worksheet_df.csv')
    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df_FORMULA.columns.values.tolist()] + worksheet_df_FORMULA.values.tolist(),
                     value_input_option='USER_ENTERED')