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
import datetime


def scraper_earnings(tickers_list):
    barcode = 'dranatom'
    password = 'MSIGX660'
    # ____________________ Работа с Selenium ____________________________
    path = os.path.join(os.getcwd(), 'chromedriver.exe')
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('headless')

    checker = webdriver.Chrome(options=chrome_options)

    days_to_earnings = []

    for tic in tickers_list:
        try:
            checker.get(f'https://www.optionslam.com/earnings/stocks/{tic}')

            sleep(1)

            days = checker.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td[2]/div/table/tbody/tr[2]/td[2]/table/tbody/tr/td[2]')
            days = int(days.text.split(' ')[0])
            print(days)
            days_to_earnings.append(days)
        except:
            days_to_earnings.append('NA')

    checker.close()
    return days_to_earnings


def run_earnings_get(ticker_list):
    earnings_list = scraper_earnings(ticker_list)

    FINISH_DF = pd.DataFrame(
        {
            'Symbol': ticker_list,
            'Earnings': earnings_list,
        }
    )

    return earnings_list