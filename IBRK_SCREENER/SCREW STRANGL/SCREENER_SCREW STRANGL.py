import pandas as pd
import numpy as np
from ib_insync import *
import asyncio
import scipy.stats as stats
import datetime
import time
from dateutil.relativedelta import relativedelta
import yfinance as yf
import pickle
from support import *
import nest_asyncio

nest_asyncio.apply()
import mibian
from contextvars import ContextVar
import math


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
    EVR_list = []
    events_available = []

    for tic in tickers_list:
        try:
            checker.get(f'https://www.optionslam.com/earnings/stocks/{tic}')
        except:
            pass
        try:
            days = checker.find_element(By.XPATH,
                                        '/html/body/table[2]/tbody/tr/td[2]/div/table/tbody/tr[2]/td[2]/table/tbody/tr/td[2]')
            days = int(days.text.split(' ')[0])
            print(days)
            days_to_earnings.append(days)
        except:
            days_to_earnings.append('NA')

        try:
            evr = checker.find_element(By.XPATH,
                                       '/html/body/table[2]/tbody/tr/td[2]/div/table/tbody/tr[2]/td[1]/table/tbody/tr[1]/td[2]')
            evr = float(evr.text)
            print('evr', evr)
            EVR_list.append(evr)
        except:
            EVR_list.append('NA')

        try:
            events = checker.find_element(By.XPATH, '/html/body/table[2]/tbody/tr/td[2]/span[2]')
            print('events', events.text)
            events = int(events.text.split(' ')[-1])
            print('events', events)
            events_available.append(events)
        except:
            events_available.append('NA')

    print('days_to_earnings', days_to_earnings)
    print('EVR_list', EVR_list)
    checker.close()
    return days_to_earnings, EVR_list, events_available


def nearest_equal_abs(lst, target):
    return min(lst, key=lambda x: abs(abs(x) - target))


def get_BS_prices(current_price, type_option, option_chains_short_FULL):
    price_gen_list = []

    for i in range(len(option_chains_short_FULL)):
        try:
            strike = option_chains_short_FULL['strike'].iloc[i]
            dte = option_chains_short_FULL['days_to_exp'].iloc[i]
            atm_IV = option_chains_short_FULL['ATM_strike_volatility'].iloc[i]

            c = mibian.BS([current_price, strike, 1.5, dte], volatility=atm_IV * 100)
            if type_option == 'P':
                price_gen_list.append(c.putPrice)
            if type_option == 'C':
                price_gen_list.append(c.callPrice)
        except Exception as e:
            print(e)
            pass

    option_chains_short_FULL['BS_PRICE'] = price_gen_list
    return option_chains_short_FULL


def get_historical_vol(yahoo_data):
    TRADING_DAYS = 200
    returns = np.log(yahoo_data['Close'] / yahoo_data['Close'].shift(1))
    returns.fillna(0, inplace=True)
    volatility = returns.rolling(window=TRADING_DAYS).std() * np.sqrt(TRADING_DAYS)

    return volatility[-1]


def margin_calc(needed_put, needed_call, current_price):
    # Страйк пута * 0.1*100 - net credit
    margin_put = needed_put['bid'] + np.max(
        [0.1 * current_price - (current_price - needed_put['strike']), 0.1 * needed_put['strike']])
    margin_call = needed_call['bid'] + np.max(
        [0.1 * current_price - (needed_put['strike'] - current_price), 0.1 * current_price])

    # if margin_put > margin_call:
    #     position_margin = (margin_put + needed_call['bid']) * 100
    # else:
    #     position_margin = (margin_call + needed_put['bid']) * 100

    position_margin = needed_put['strike'] * 0.1 * 100 - (needed_put['bid'] - needed_call['ask'])

    return position_margin


def ratios_calc(needed_put, needed_call, current_price):
    delta_theta_ratio = (needed_put['delta'] + needed_call['delta']) / (
                needed_put['theta'] + needed_call['theta'])
    gamma_theta_ratio = (needed_put['gamma'] + needed_call['gamma']) / (
                needed_put['theta'] + needed_call['theta'])
    vega_theta_ratio = (needed_put['vega'] + needed_call['vega']) / (
                needed_put['theta'] + needed_call['theta'])

    return delta_theta_ratio, gamma_theta_ratio, vega_theta_ratio


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




    if type_option == 'P':
        return ((prime - put_df['put_price']) * put_df['proba']).sum()

    if type_option == 'C':
        return ((prime - put_df['call_price']) * put_df['proba']).sum()


def expected_return_calc(needed_call, needed_put, current_price, history_vol):
    vol_call = needed_call['iv']
    vol_put = needed_put['iv']
    days_to_exp = needed_put['days_to_exp']
    strike_put = needed_put['strike']
    strike_call = needed_call['strike']
    prime_put = needed_put['bid']
    prime_call = needed_call['bid']

    print('history_vol', history_vol)
    print('vol_call', vol_call)
    print('vol_put', vol_put)
    print('days_to_exp', days_to_exp)
    print('strike_put', strike_put)
    print('strike_call', strike_call)
    print('prime_put', prime_put)
    print('prime_call', prime_call)
    print('expected_return CALCULATION ...')

    price_array = np.arange(current_price - current_price / 2, current_price + current_price, 0.1)
    put_finish = get_abs_return(price_array, 'P', days_to_exp, history_vol, current_price, strike_put,
                                prime_put,
                                vol_put)
    call_finish = get_abs_return(price_array, 'C', days_to_exp, history_vol, current_price, strike_call,
                                 prime_call,
                                 vol_call)

    expected_return = (put_finish + call_finish) * 100

    return expected_return


ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=12)  # 7497

except:
    ib.connect('127.0.0.1', 7496, clientId=12)

date_name = '7-12'
gf_screener_native = pd.read_excel(f'{date_name}.xlsx')
gf_screener = gf_screener_native[21:]
gf_screener.columns = gf_screener_native.iloc[19]
print(gf_screener)
ticker_list = gf_screener['Symbol'].tolist()[:10]

# earnings_list, EVR_list, events_available = scraper_earnings([ticker_list])

call_strike_list = []
put_strike_list = []
possition_margin_list = []
delta_theta_ratio_list = []
gamma_theta_ratio_list = []
vega_theta_ratio_list = []
expected_return_list = []
expected_return_percent_list = []
iv_percentile_list = []
exp_date_list = []

yahoo_df_native = yf.download(ticker_list)['Close']

for tick in ticker_list:
    try:
        yahoo_df = pd.DataFrame()
        yahoo_df['Close'] = yahoo_df_native[tick]

        print(f'------- {tick} --------')

        # ДАТЫ ЭКСПИРАЦИИ
        limit_date_min = datetime.datetime.now() + relativedelta(days=+250)
        limit_date_max = datetime.datetime.now() + relativedelta(days=+500)

        current_price, current_iv_percentile = get_ib_data(tick, yahoo_df, ib)

        df_chains = get_df_chains(tick, limit_date_min, limit_date_max)
        df_chains = get_atm_strikes(df_chains, current_price)
        print('---------------- df_chains  ---------------------')
        print(df_chains)

        put_df = df_chains[df_chains['side'] == 'put'].reset_index(drop=True)
        put_df = put_df[put_df['strike'] < current_price]
        call_df = df_chains[df_chains['side'] == 'call'].reset_index(drop=True)

        put_df = get_BS_prices(current_price, 'P', put_df)
        put_df['Difference'] = put_df['bid'] - put_df['BS_PRICE']
        needed_put = put_df[put_df['Difference'] == put_df['Difference'].max()].reset_index(drop=True).iloc[0]
        put_delta = needed_put['delta']

        call_df = call_df[call_df['EXP_date'] == needed_put['EXP_date']]
        call_delta = nearest_equal_abs(call_df['delta'].dropna(), abs(put_delta))
        needed_call = call_df[call_df['delta'] == call_delta].reset_index(drop=True).iloc[0]

        position_margin = margin_calc(needed_put, needed_call, current_price)

        print('---------------- needed_put ---------------------')
        print(needed_put['EXP_date'])
        print(needed_put['strike'])
        print(needed_put['delta'])

        print('---------------- needed_call ---------------------')
        print(needed_call['EXP_date'])
        print(needed_call['strike'])
        print(needed_call['delta'])


        #     базовые ратио
        delta_theta_ratio, gamma_theta_ratio, vega_theta_ratio = ratios_calc(needed_put, needed_call, current_price)

        #  historical volatility
        hist_vol = get_historical_vol(yahoo_df)
        # expected return
        expected_return = expected_return_calc(needed_call, needed_put, current_price, hist_vol)
        print('expected_return', expected_return)

        expected_return_percent = (expected_return / position_margin) * 100

        print('expected_return_percent', expected_return_percent)


        call_strike_list.append(needed_call['strike'])
        put_strike_list.append(needed_put['strike'])
        possition_margin_list.append(position_margin)
        delta_theta_ratio_list.append(delta_theta_ratio)
        gamma_theta_ratio_list.append(gamma_theta_ratio)
        vega_theta_ratio_list.append(vega_theta_ratio)
        expected_return_list.append(expected_return)
        expected_return_percent_list.append(expected_return_percent)
        iv_percentile_list.append(current_iv_percentile)
        exp_date_list.append(needed_put['EXP_date'])

    except:
        call_strike_list.append(np.nan)
        put_strike_list.append(np.nan)
        possition_margin_list.append(np.nan)
        delta_theta_ratio_list.append(np.nan)
        gamma_theta_ratio_list.append(np.nan)
        vega_theta_ratio_list.append(np.nan)
        expected_return_list.append(np.nan)
        expected_return_percent_list.append(np.nan)
        iv_percentile_list.append(np.nan)
        exp_date_list.append(np.nan)
        pass

FINISH_DF = pd.DataFrame(
    {
        'Symbol': ticker_list,
        'EXP_date': exp_date_list,
        'CALL_Strike': call_strike_list,
        'PUT_Strike': put_strike_list,
        'Delta_Theta_Ratio': delta_theta_ratio_list,
        'Gamma_Theta_Ratio': gamma_theta_ratio_list,
        'Vega_Theta_Ratio': vega_theta_ratio_list,
        'Margin': possition_margin_list,
        'Rxpected_Return': expected_return_list,
        'Rxpected_Return_Percent': expected_return_percent_list,
        'IV_Percentile': iv_percentile_list,

    }
)

gf_screener = gf_screener.merge(FINISH_DF, on='Symbol')
gf_screener.to_excel('gf_screener.xlsx', index=False)