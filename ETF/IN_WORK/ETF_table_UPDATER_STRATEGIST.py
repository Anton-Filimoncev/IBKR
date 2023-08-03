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


def hist_vol():
    barcode = 'dranatom'
    password = 'MSIGX660'
    # ____________________ Работа с Selenium ____________________________
    path = os.path.join(os.getcwd(), 'chromedriver.exe')
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


def strategist_pcr_signal(ticker_list):
    barcode = 'dranatom'
    password = 'MSIGX660'
    # ____________________ Работа с Selenium ____________________________
    path = os.path.join(os.getcwd(), 'chromedriver.exe')
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('headless')

    checker = webdriver.Chrome(options=chrome_options)

    checker.get(f'https://www.optionstrategist.com/subscriber-content/put-call-ratios')
    time.sleep(2)

    sign_in_userName = checker.find_element(by=By.ID, value="edit-name")
    sign_in_userName.send_keys(barcode)
    sign_in_password = checker.find_element(by=By.ID, value="edit-pass")
    sign_in_password.send_keys(password)
    sign_in = checker.find_element(by=By.ID,
                                   value='''edit-submit''')
    sign_in.click()
    time.sleep(2)
    try:
        close_popup = checker.find_element(By.XPATH, '//*[@id="PopupSignupForm_0"]/div[2]/div[1]')
        close_popup.click()
    except:
        pass

    # select_fresh_txt = checker.find_element(By.XPATH,
    #                                         '''//*[@id="node-35"]/div/div/div/div/table[1]/tbody/tr[1]/td[1]''')
    #
    # select_fresh_txt.click()
    time.sleep(2)

    html_txt = checker.find_element(By.XPATH,
                                    '''//*[@id="node-47"]/div/div/div/div/pre''').text.split('\n')

    strategist_signals = []
    plot_links_list = []

    for tick in ticker_list:
        local_flag = 0
        for piece in html_txt:
            if tick in piece:
                if tick + '_W' == piece.split(' ')[0]:
                    strategist_signals.append(piece[len(tick) + 3:])
                    print(piece)
                    local_flag = 1
        if local_flag == 0:
            strategist_signals.append('Empty')
            print('Empty')

    print(strategist_signals)

    # получаем ссылки на графики
    all_link = checker.find_elements(By.XPATH, "//a[@href]")
    total_links = []
    for elem in all_link:
        total_links.append(elem.get_attribute("href"))

    print(total_links)

    for tick in ticker_list:
        local_flag = 0
        for elem in total_links:
            if tick + '_W' in elem:
                plot_links_list.append(elem)
                local_flag = 1
                break
        if local_flag == 0:
            plot_links_list.append('Empty')
            print('Empty')

    print(plot_links_list)

    return strategist_signals, plot_links_list

def run_strategist():
    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("ETF")
    worksheet_spark = gc.open("IBKR").worksheet("sparkline")

    worksheet_df_len = pd.DataFrame(worksheet.get_all_records())[:-1]
    worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]
    company_list = worksheet_df_len['ETF COMPLEX POSITION'].values.tolist()
    strategist_pcr_signals, plot_links_list = strategist_pcr_signal(company_list)
    hist_vol_df = hist_vol_start()

    for i in range(len(worksheet_df_len)):

        # заполняем столбцы с формулами
        for k in range(len(worksheet_df_len)):
            worksheet_df['CURRENT PRICE'].iloc[k] = f'=GOOGLEFINANCE(A{k + 2},"price")'
            worksheet_df['WEIGHT PCR sparkline'].iloc[k] = f'=sparkline(sparkline!B{k + 1}:W{k + 1})'
            # worksheet_df['% BETA DELTA'].iloc[k] = f'=C{k + 2}/$C$27'

        print(worksheet_df)

        tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]
        print('TICKER = ', tick)
        print(hist_vol_df[hist_vol_df['Symbol'] == tick]['Percentile'])
        iv_os = hist_vol_df[hist_vol_df['Symbol'] == tick]['Percentile']

        if iv_os.empty == True:
            iv_os = 'Empty'
        else:
            iv_os = iv_os.values[0] / 100

        # ----------------------------
        worksheet_df['O_S WEIGHT PCR SIGNAL'].iloc[i] = strategist_pcr_signals[i]
        worksheet_df['O_S Plot Link'].iloc[i] = plot_links_list[i]
        worksheet_df['IV O_S'].iloc[i] = iv_os

    worksheet_df = worksheet_df.fillna(0)
    worksheet_df.to_csv('worksheet_df.csv', index=False)
    worksheet_df = pd.read_csv('worksheet_df.csv')
    worksheet_df = worksheet_df.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(),
                     value_input_option='USER_ENTERED')

