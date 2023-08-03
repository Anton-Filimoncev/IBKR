import pandas as pd
import numpy as np
import os
import time
import pickle
import gspread as gd
from scipy import stats
import yfinance as yf
import pandas_ta as pta
import datetime
from dateutil.relativedelta import relativedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import random
from naked_puts_exp import naked_puts_exp_start
from covered_call_writes import covered_call_writes_start
from calendar_spread_exp import calendar_spread_exp_start



def run():
    naked_puts = naked_puts_exp_start()
    covered_call_writes = covered_call_writes_start()
    calendar_spread = calendar_spread_exp_start()

    # # ================ раббота с таблицей============================================
    gc = gd.service_account('Seetus.json')
    worksheet = gc.open("IBKR").worksheet("ETF")
    worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]


    tickers = worksheet_df['ETF COMPLEX POSITION'].values.tolist()
    print('tickers')
    print(tickers)
    print('covered_call_writes')
    print(covered_call_writes)
    naked_puts_finish = pd.DataFrame()
    calendar_spread_finish = pd.DataFrame()
    covered_call_writes_finish = pd.DataFrame()
    for tick in tickers:
        naked_puts_local = naked_puts[naked_puts.index == tick]
        calendar_spread_local = calendar_spread[calendar_spread.index == tick]
        сovered_call_writes_local = covered_call_writes[covered_call_writes.index == tick]

        naked_puts_finish = pd.concat([naked_puts_finish, naked_puts_local])
        calendar_spread_finish = pd.concat([calendar_spread_finish, calendar_spread_local])
        covered_call_writes_finish = pd.concat([covered_call_writes_finish, сovered_call_writes_local])


    print('naked_puts_finish')
    print(naked_puts_finish)
    print('calendar_spread_finish')
    print(calendar_spread_finish)
    print('covered_call_writes_finish')
    print(covered_call_writes_finish)


    with pd.ExcelWriter('OptionStrategist.xlsx') as writer:
        naked_puts_finish.to_excel(writer, sheet_name='naked_puts')
        calendar_spread_finish.to_excel(writer, sheet_name='calendar_spread')
        covered_call_writes_finish.to_excel(writer, sheet_name='covered_call_writes')
run()

