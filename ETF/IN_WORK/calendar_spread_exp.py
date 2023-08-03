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


def scraper():
    barcode = 'dranatom'
    password = 'MSIGX660'
    # ____________________ Работа с Selenium ____________________________
    path = os.path.join(os.getcwd(), 'chromedriver.exe')
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument('headless')

    checker = webdriver.Chrome(options=chrome_options)

    checker.get(f'https://www.optionstrategist.com/subscriber-content/calendar-spreads')
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
                                            '''//*[@id="node-32"]/div/div/div/div/table[2]/tbody/tr[1]/td[1]''')


    select_fresh_txt.click()
    sleep(2)

    html_txt = checker.page_source
    print("The current url is:" + str(checker.page_source))

    full_txt = (html_txt[html_txt.index('guaranteed.'):html_txt.rindex('</pre>')]).replace('guaranteed.', '')
    col_name_replace = 'Symb     Stk  SOpt StrkMn  Sbid LOpt StrkMn  Lask    DBE    UBE  %DBE  %UBE PrDBE PrUBE  p(pft) Maxpft  p(max)    ERTN   AERTN   Invt   IVF  Sleftyr  bdIV  Lleftyr  asIV  CompIV  %ile     FullOptionSymbol'
    full_txt = full_txt.replace(col_name_replace, '').replace('\n', ' ')

    # with open('data.txt', 'w') as f:
    #     f.write(full_txt)

    return full_txt,  col_name_replace

def calendar_spread_exp(full_txt, col_name_replace):

    data_list = list(filter(len, full_txt.split(' ')))

    row_list = []

    for value_num in range(len(data_list)) :

        try:
            if data_list[value_num] == data_list[value_num + 30]:
                if data_list[value_num] == data_list[value_num + 28]:
                    try:
                        try:
                            float(data_list[value_num + 28])
                        except:
                            float(data_list[value_num + 8])
                            row_list.append(data_list[value_num:value_num + 31])
                    except:
                        pass
        except:
            pass

    unnamed_df = pd.DataFrame(row_list).iloc[:, :-1]
    unnamed_df.iloc[:, -2] = unnamed_df.iloc[:, -2]+unnamed_df.iloc[:, -1]
    unnamed_df.iloc[:, 3] = unnamed_df.iloc[:, 3] + ' ' + unnamed_df.iloc[:, 4]
    unnamed_df = unnamed_df.iloc[:, :-1]
    print(unnamed_df.iloc[:, 2:])
    unnamed_df = unnamed_df.drop(columns=4)
    print(unnamed_df.iloc[:, 2:])
    col_name = list(filter(len, col_name_replace.split(' ')))

    for i in unnamed_df.columns.tolist():
        try:
            unnamed_df[i] = unnamed_df[i].astype(float)
        except Exception as err:
            pass

    unnamed_df.columns = col_name
    unnamed_df = unnamed_df.set_index('Symb')

    # writer = pd.ExcelWriter(f'''Calendar Spreads Best.xlsx''', engine='xlsxwriter')
    # unnamed_df.to_excel(writer, sheet_name='Calendar Spreads Best')
    # writer.save()
    return unnamed_df

def calendar_spread_exp_start():
    html_txt,  col_name_replace = scraper()
    # with open('data.txt', 'r') as file:
    #     html_txt = file.read()
    calendar_spread = calendar_spread_exp(html_txt,  col_name_replace)

    return calendar_spread

