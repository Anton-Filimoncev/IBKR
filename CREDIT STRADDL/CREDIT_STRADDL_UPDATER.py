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
from selenium import webdriver
from concurrent.futures.thread import ThreadPoolExecutor
import os
from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
pd.options.mode.chained_assignment = None  # default='warn'


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



def hist_vol():
    barcode = 'dranatom'
    password = 'MSIGX660'
    # ____________________ Работа с Selenium ____________________________
    path = os.path.join(os.getcwd(), 'chromedriver.exe')
    print(path)
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('headless')

    checker = webdriver.Chrome(options=chrome_options)

    checker.get(f'https://www.optionstrategist.com/subscriber-content/volatility-history')
    sleep(2)

    sign_in_userName = checker.find_element(by=By.ID, value="edit-name")
    sign_in_userName.send_keys(barcode)
    sign_in_password = checker.find_element(by=By.ID, value="edit-pass")
    sign_in_password.send_keys(password)
    sign_in = checker.find_element(by=By.ID,
                                   value='''edit-submit''')
    sign_in.click()
    sleep(5)
    try:
        close_popup = checker.find_element(By.XPATH, '//*[@id="PopupSignupForm_0"]/div[2]/div[1]')
        close_popup.click()
    except:
        pass

    select_fresh_txt = checker.find_element(By.XPATH,
                                            '''//*[@id="node-35"]/div/div/div/div/table[1]/tbody/tr[1]/td[1]''')

    select_fresh_txt.click()
    sleep(2)

    html_txt = checker.page_source
    # print("The current url is:" + str(checker.page_source))

    full_txt = (html_txt[html_txt.index('800-724-1817'):html_txt.rindex('800-724-1817')]).replace('* ', '').replace(
        '^ ', '')

    col_name_replace = 'Symbol (option symbols)           hv20  hv50 hv100    DATE   curiv Days/Percentile Close'
    full_txt = full_txt.replace(col_name_replace, '').replace('\n', ' ')


    return full_txt, col_name_replace


def hist_vol_analysis(full_txt, col_name_replace):
    data_list = list(filter(len, full_txt.split(' ')))

    row_list = []

    for value_num in range(len(data_list)):
        try:
            float(data_list[value_num + 1])
            float(data_list[value_num + 2])
            float(data_list[value_num + 3])
            float(data_list[value_num + 4])
            float(data_list[value_num + 5])
            float(data_list[value_num + 8])
            row_list.append(data_list[value_num:value_num + 9])
        except:
            pass

    unnamed_df = pd.DataFrame(row_list)
    print('unnamed_df')
    print(unnamed_df)

    print('col_name_replace')
    print(col_name_replace)

    unnamed_df.columns = ['Symbol', 'hv20', 'hv50', 'hv100', 'DATE', 'curiv', 'Days', 'Percentile', 'Close']
    # unnamed_df = unnamed_df.set_index('Sc')

    int_percentile = []

    for perc in range(len(unnamed_df)):
        try:
            int_percentile.append(float(unnamed_df.iloc[perc]['Percentile'].replace('%ile', '')))
        except:
            int_percentile.append(0)

    unnamed_df['Percentile'] = int_percentile

    for i in unnamed_df.columns.tolist():
        try:
            unnamed_df[i] = unnamed_df[i].astype(float)
        except Exception as err:
            pass

    print('unnamed_df')
    print(unnamed_df)

    return unnamed_df


def hist_vol_start():
    html_txt, col_name_replace = hist_vol()

    history_vol = hist_vol_analysis(html_txt, col_name_replace)

    return history_vol

def run():
    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("CREDIT_STRADDL")
    worksheet_df_len = pd.DataFrame(worksheet.get_all_records())
    worksheet_df = pd.DataFrame(worksheet.get_all_records())

    hist_vol_df = hist_vol_start()

    for i in range(len(worksheet_df_len)):
        print(worksheet_df)

        tick = worksheet_df['TICKER'].iloc[i]
        print(f'---------    {tick}')
        yahoo_data = yf.download(tick)
        trend_signal = trend(yahoo_data)
        # sma_20, sma_100, rsi = get_tech_data(yahoo_data)

        print(hist_vol_df[hist_vol_df['Symbol'] == tick]['Percentile'])
        iv_os = hist_vol_df[hist_vol_df['Symbol'] == tick]['Percentile']

        if iv_os.empty == True:
            iv_os = 'Empty'
        else:
            iv_os = iv_os.values[0] / 100

        worksheet_df['TREND'].iloc[i] = trend_signal
        worksheet_df['IV_PERCENTILE'].iloc[i] = iv_os
        # worksheet_df['SMA 20'].iloc[i] = sma_20
        # worksheet_df['SMA 100'].iloc[i] = sma_100

    worksheet_df = worksheet_df.fillna(0)
    worksheet_df.to_csv('worksheet_df.csv', index=False)
    worksheet_df = pd.read_csv('worksheet_df.csv')
    worksheet_df['Updated'] = str(datetime.datetime.now())
    worksheet_df = worksheet_df.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(),
                     value_input_option='USER_ENTERED')



if __name__ == '__main__':
    run()

