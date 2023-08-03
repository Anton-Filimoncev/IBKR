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
                (np.log(price_array[stock_price_num] / current_price) / (history_vol * math.sqrt(days_to_exp / 365))))
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


    if type_option == 'P':
        return ((prime - put_df['put_price']) * put_df['proba']).sum()

    if type_option == 'C':
        return ((prime - put_df['call_price']) * put_df['proba']).sum()


if __name__ == '__main__':
    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("STRANGL")
    worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace('', np.nan)
    worksheet_df = worksheet_df[:len(worksheet_df['Тикер'].dropna())]

    worksheet_df_FORMULA = pd.DataFrame(worksheet.get_all_records(value_render_option='FORMULA')).replace('', np.nan)
    worksheet_df_FORMULA = worksheet_df_FORMULA[:len(worksheet_df_FORMULA['Тикер'].dropna())]



    print('worksheet_df')
    print(worksheet_df)
    # print('worksheet_df_FORMULA')
    # print(worksheet_df_FORMULA['Рыночная цена'])


    for i in range(len(worksheet_df)):
        current_price = worksheet_df['Рыночная цена'].iloc[i]
        history_vol = worksheet_df['HV 200'].iloc[i]
        vol_call = worksheet_df['IV call'].iloc[i]
        vol_put = worksheet_df['IV put'].iloc[i]
        days_to_exp = worksheet_df['Осталось дней до закрытия'].iloc[i]
        strike_put = worksheet_df['STRIKE PUT'].iloc[i]
        strike_call = worksheet_df['STRIKE CALL'].iloc[i]
        prime_put = worksheet_df['Премия пута'].iloc[i]
        prime_call = worksheet_df['Премия колла'].iloc[i]
        position_num = abs(worksheet_df['Количество позиций коллов'].iloc[i])

        price_array = np.arange(current_price - current_price / 2, current_price + current_price, 0.1)
        put_finish = get_abs_return(price_array, 'P', days_to_exp, history_vol, current_price, strike_put, prime_put,
                                    vol_put)
        call_finish = get_abs_return(price_array, 'C', days_to_exp, history_vol, current_price, strike_call, prime_call,
                                     vol_call)

        worksheet_df_FORMULA['Вероятный статистический доход'].iloc[i] = (put_finish + call_finish)*100*position_num

        print(worksheet_df['Тикер'].iloc[i], put_finish + call_finish)


    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    worksheet_df_FORMULA.to_csv('worksheet_df.csv', index=False)
    worksheet_df_FORMULA = pd.read_csv('worksheet_df.csv')
    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df_FORMULA.columns.values.tolist()] + worksheet_df_FORMULA.values.tolist(),
                     value_input_option='USER_ENTERED')

