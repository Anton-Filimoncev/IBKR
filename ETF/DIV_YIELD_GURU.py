import threading
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import os
from time import sleep
from pathlib import Path


def get_fundamental_data( table_name):
    # print('Remove old files...')
    # for filename in os.listdir(f'guru_files'):
    #     os.remove(f'guru_files\{filename}')

    # executor = ThreadPoolExecutor(5)

    # def scrape(url, *, loop):
    #     loop.run_in_executor(executor, scraper, url)

    def scraper(tk):

        barcode = 'fin@ss-global-group.com'
        password = 'MSIGX660'
        # ____________________ Работа с Selenium ____________________________
        path = os.path.join(os.getcwd(), 'chromedriver.exe')
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument("--start-maximized")
        # chrome_options.add_argument('headless')
        path_folder = f'{Path(__file__).parent.absolute()}\div_data'
        print(path_folder)

        prefs = {"download.default_directory": f'''{Path(__file__).parent.absolute()}\div_data''',
                 "download.prompt_for_download": False,
                 'profile.managed_default_content_settings.javascript': 1,
                 'profile.managed_default_content_settings.images': 1,
                 "download.directory_upgrade": True}  # set path

        chrome_options.add_experimental_option("prefs", prefs)  # set option

        checker = webdriver.Chrome(options=chrome_options)
        checker.get('chrome://settings/')
        checker.execute_script('chrome.settingsPrivate.setDefaultZoom(0.6);')

        checker.get(f'https://www.gurufocus.com/')
        sleep(random.randint(10, 25))
        sign_in_click = checker.find_element(by=By.LINK_TEXT, value='''Login''')
        sign_in_click.click()
        sleep(5)
        sign_in_userName = checker.find_element(by=By.ID, value="login-dialog-name-input")
        sign_in_userName.send_keys(barcode)
        sign_in_password = checker.find_element(by=By.ID, value="login-dialog-pass-input")
        sign_in_password.send_keys(password)
        sleep(4)
        sign_in = checker.find_element(by=By.XPATH,
                                       value='''//*[@id="__layout"]/div/div/div[2]/form/div[6]/button/span/span/div''')
        sign_in.click()
        sleep(10)

        # for num in range(len(tk)):
        #     print(num)
        #     checker.find_element(by=By.XPATH, value='''/html/body''').send_keys(Keys.CONTROL + 't')
        #     sleep(1)
        #     # checker.get(f'https://www.gurufocus.com/')

        def data_loader(ticker: str):
            try:
                print(f'Downloading: {ticker} ...')
                url_f = f"https://www.gurufocus.com/etf/{ticker}/summary#etf-main|fundamental-chart"
                checker.get(url_f)
                # sleep(0.5)
                # html = checker.find_element(by=By.XPATH, value='/html/body')
                # html.click()

                sleep(7)

                select_all = checker.find_element(By.XPATH,
                                                  '''/html/body/div/div/section/section/main/div[1]/div[4]/div[2]/div/div[1]/div[1]/div[2]/div/div/div[3]/div[2]/div/div/div[2]/div/span/div/span''')
                select_all.click()
                sleep(2)

                export = checker.find_element(By.XPATH, '''/html/body/ul/li[2]/span''')

                export.click()
                sleep(5)

                try:
                    os.remove(f'guru_files\{ticker}.xlsx')
                except:
                    pass

                os.chdir(path_folder)
                files = sorted(os.listdir(os.getcwd()), key=os.path.getmtime)
                newest = files[-1]
                os.rename(newest, ticker+'.xlsx')


                # print('Go to next ticker')
            except Exception as e:
                print(e)
                print('Cant download file')

        for ticker in tk:
            data_loader(ticker)

    worksheet_df = pd.read_excel(table_name)['Ticker']
    tickers_list_list = []

    tickers_list_list.append(worksheet_df.tolist())
    # tickers_list_list.append(worksheet_df[1::5]['ETF COMPLEX POSITION'].tolist())
    # tickers_list_list.append(worksheet_df[2::5]['ETF COMPLEX POSITION'].tolist())
    # tickers_list_list.append(worksheet_df[3::5]['ETF COMPLEX POSITION'].tolist())
    # tickers_list_list.append(worksheet_df[4::5]['ETF COMPLEX POSITION'].tolist())

    def run_threads():
        threads = [
            threading.Thread(target=scraper, args=[tickers_list])
            for tickers_list in tickers_list_list
        ]
        for thread in threads:
            thread.start()  # каждый поток должен быть запущен
        for thread in threads:
            thread.join()  # дожидаемся исполнения всех потоков

    run_threads()

    # all_data_to_one()



# get_fundamental_data()

def run_guru():

    table_name = 'tickers.xlsx'

    # get_fundamental_data(table_name)

    tick_list = pd.read_excel(table_name)['Ticker']


    for tick in tick_list:

        print('TICKER = ', tick)

        try:
            div_data = pd.read_excel(f'{Path(__file__).parent.absolute()}\div_data\{tick}.xlsx')[2:]
            print(div_data.T.reset_index(drop=True))

            div_data = div_data.T[::-1][:-1].reset_index(drop=True)
            print(div_data)


            div_data.columns = [['Date', 'Dividend Yield']]


            data_val_list = []
            div_list = []
            for div_num in range(len(div_data)):
                data_val_list.append(div_data['Date'].iloc[div_num].values[0])
                div_list.append(div_data['Dividend Yield'].iloc[div_num].values[0])


            new_df = pd.DataFrame({
                'Date': data_val_list,
                'Dividend Yield': div_list,
            })

            new_df['Date'] = pd.to_datetime(new_df['Date'], format='%Y-%m-%d', errors='coerce')
            new_df = new_df.set_index('Date')


            print('new_df')
            print(new_df)

            new_df.to_excel(f'{Path(__file__).parent.absolute()}\div_data\{tick}.xlsx')

        except:
            current_div_data = 'Empty'
            median_div_data = 'Empty'

 #
 #            current_div_data = new_df['Dividend Yield'].iloc[-1]
 #            median_last_days = datetime.datetime.now() - relativedelta(days=450)
 #            print(median_last_days)
 #            median_div_data = new_df['Dividend Yield'][median_last_days:].median()
 #
 #            print('-')
 #            print(current_div_data)
 #            print(median_div_data)
 #
 #        except:
 #            current_div_data = 'Empty'
 #            median_div_data = 'Empty'
 #
 #        # ----------------------------
 #        worksheet_df['Dividend Yield'].iloc[i] = current_div_data
 #        worksheet_df['Dividend Yield Median'].iloc[i] = median_div_data
 #
 #    worksheet_df = worksheet_df.fillna(0)
 #    worksheet_df.to_csv('worksheet_df.csv', index=False)
 #    worksheet_df = pd.read_csv('worksheet_df.csv')
 #    worksheet_df = worksheet_df.fillna(0)
 #

run_guru()