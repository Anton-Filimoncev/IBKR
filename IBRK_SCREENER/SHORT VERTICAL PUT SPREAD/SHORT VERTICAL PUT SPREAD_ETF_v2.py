import pandas as pd
import numpy as np
from ib_insync import *
import asyncio
import scipy.stats as stats
import datetime
import time
from dateutil.relativedelta import relativedelta
import yfinance as yf
import os
from support import *
import nest_asyncio
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
nest_asyncio.apply()
import mibian
from contextvars import ContextVar
import math
import pandas_ta as pta
import gspread as gd


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
            print(strike)
            print(dte)
            print(atm_IV)
            c = mibian.BS([current_price, strike, 1.5, dte], volatility=atm_IV * 100)
            if type_option == 'P':
                price_gen_list.append(c.putPrice)
            if type_option == 'C':
                price_gen_list.append(c.callPrice)
        except Exception as e:
            print(e)
            pass

    print('price_gen_list')
    print(price_gen_list)
    option_chains_short_FULL['BS_PRICE'] = price_gen_list
    return option_chains_short_FULL


def margin_calc(needed_put_short, current_price):
    net_credit = needed_put_short['bid']
    position_margin = current_price * 0.2 * 100
    break_point = needed_put_short['strike'] - net_credit
    reward_risk = net_credit*100/position_margin

    return position_margin, break_point, reward_risk


def ratios_calc(needed_put_short, current_price):
    # delta_theta_ratio = (needed_put_short['delta'] + needed_put_long['delta']) / (
    #             needed_put_short['theta'] + needed_put_long['theta'])
    gamma_theta_ratio = (needed_put_short['gamma']) / (needed_put_short['theta'])
    vega_theta_ratio = (needed_put_short['vega']) / (needed_put_short['theta'])

    # theta_margin_ratio
    net_credit = needed_put_short['bid']
    position_margi_calc = current_price * 0.2
    theta_position = abs(needed_put_short['theta'])
    theta_margin_ratio = (theta_position / position_margi_calc) * 100

    return gamma_theta_ratio, vega_theta_ratio, theta_margin_ratio


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


def expected_return_calc(needed_put_short, current_price, history_vol):
    vol_put_short = needed_put_short['iv']
    # vol_put_long = needed_put_long['iv']
    days_to_exp = needed_put_short['days_to_exp']
    # strike_put_long = needed_put_long['strike']
    strike_put_short = needed_put_short['strike']
    # prime_put_long = needed_put_long['ask']
    prime_put_short = needed_put_short['bid']

    print('history_vol', history_vol)
    print('vol_put_short', vol_put_short)
    # print('vol_put_long', vol_put_long)
    print('days_to_exp', days_to_exp)
    # print('strike_put_long', strike_put_long)
    print('strike_put_short', strike_put_short)
    # print('prime_put_long', prime_put_long)
    print('prime_put_short', prime_put_short)

    print('expected_return CALCULATION ...')

    price_array = np.arange(current_price - current_price / 2, current_price + current_price, 0.2)
    # print('price_array', price_array)
    short_finish = get_abs_return(price_array, 'Short', days_to_exp, history_vol, current_price, strike_put_short,
                                prime_put_short,
                                vol_put_short)


    # long_finish = get_abs_return(price_array, 'Long', days_to_exp, history_vol, current_price, strike_put_long,
    #                              prime_put_long,
    #                              vol_put_long)

    expected_return = (short_finish) * 100

    return expected_return


def get_atm_strikes(chains_df, current_price):
    chains_df['ATM_strike_volatility'] = np.nan
    for exp in chains_df['EXP_date'].unique():
        solo_exp_df = chains_df[chains_df['EXP_date'] == exp]
        atm_strike = nearest_equal(solo_exp_df['strike'].tolist(), current_price)
        atm_put_volatility = solo_exp_df[solo_exp_df['strike'] == atm_strike]['iv'].reset_index(drop=True).iloc[0]
        chains_df.loc[chains_df['EXP_date'] == exp, "ATM_strike_volatility"] = atm_put_volatility

    return chains_df

def get_proba_below(needed_put_short, current_price, history_vol):

    days_to_exp = needed_put_short['days_to_exp']
    # strike_put_long = needed_put_long['strike']
    strike_put_short = needed_put_short['strike']

    P_below_short = stats.norm.cdf(
        (np.log(strike_put_short / current_price) / (
                history_vol * math.sqrt(days_to_exp / 365))))

    # P_below_long = stats.norm.cdf(
    #     (np.log(strike_put_long / current_price) / (
    #             history_vol * math.sqrt(days_to_exp / 365))))

    P_below = P_below_short

    return P_below

def trend(price_df):
    trend = ''
    current_price = price_df['Close'].iloc[-1]
    SMA_20 = price_df['Close'].rolling(window=20).mean().iloc[-1]
    SMA_100 = price_df['Close'].rolling(window=100).mean().iloc[-1]
    RSI = pta.rsi(price_df['Close'])

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





def get_max_pain(df_chains_for_max_pain):
    call_max_pain_list = []
    put_max_pain_list = []
    strike_list = []

    max_pain_put = df_chains_for_max_pain[df_chains_for_max_pain['side'] == 'put'].reset_index(drop=True)
    max_pain_call = df_chains_for_max_pain[df_chains_for_max_pain['side'] == 'call'].reset_index(drop=True)

    for i in range(len(max_pain_put)):
        put_max_pain_list.append(total_loss_on_strike(max_pain_put, max_pain_put['strike'][i], 'put'))
        call_max_pain_list.append(total_loss_on_strike(max_pain_call, max_pain_put['strike'][i], 'call'))
        strike_list.append(max_pain_put['strike'][i])

    max_pain = pd.DataFrame({'PUT': put_max_pain_list,
                             'CALL': call_max_pain_list,
                             'Strike': strike_list
                             })

    max_pain_value = (max_pain['PUT'] + max_pain['CALL']).min()
    max_pain['Sum'] = max_pain['PUT'] + max_pain['CALL']
    max_pain_strike = max_pain[max_pain['Sum'] == max_pain_value]['Strike'].reset_index(drop=True).iloc[0]

    return max_pain_strike


put_long_strike_list = []
put_short_strike_list = []
possition_margin_list = []
delta_theta_ratio_list = []
gamma_theta_ratio_list = []
vega_theta_ratio_list = []
theta_margin_ratio_list = []
expected_return_list = []
expected_return_percent_list = []
iv_percentile_list = []
break_point_list = []
proba_below_list = []
reward_risk_list = []
trend_list = []
exp_date_list = []
max_paint_list = []
# liquidity_short_list = []
liquidity_long_list = []
hist_vol_list = []
hist_vol_stage_list = []
iv_stage_list = []
ROI_day_list = []
RSI_list = []
div_list = []


# # ================ раббота с таблицей============================================
gc = gd.service_account(filename='Seetus.json')
worksheet = gc.open("IBKR").worksheet("ETF")
worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]
worksheet_df = worksheet_df.set_index('ETF COMPLEX POSITION')
print('worksheet_df')
print(worksheet_df)

ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=212)  # 7497

except:
    ib.connect('127.0.0.1', 7497, clientId=212)


ticker_list = pd.read_excel('ticker_list.xlsx')['ticker'].tolist()
yahoo_df_native = yf.download(ticker_list)['Close']



for tick in ticker_list:



    try:
        yahoo_df = pd.DataFrame()
        yahoo_df['Close'] = yahoo_df_native[tick]

        print(f'------- {tick} --------')

        # ДАТЫ ЭКСПИРАЦИИ
        limit_date_min = datetime.datetime.now() + relativedelta(days=+3)
        limit_date_max = datetime.datetime.now() + relativedelta(days=+365)

        current_price, current_iv_percentile, iv_regime = get_ib_data(tick, yahoo_df, ib)

        side = 'put'

        df_chains = get_df_chains(tick, limit_date_min, limit_date_max)

        print('---------------- df_chains  ---------------------')
        print(df_chains)

        df_chains = get_atm_strikes(df_chains, current_price)
        df_chains_for_max_pain = df_chains.copy()

        df_chains = df_chains[df_chains['side'] == 'put']
        df_chains = df_chains[df_chains['strike'] < current_price]
        needed_exp_date = df_chains[df_chains['ATM_strike_volatility'] == df_chains['ATM_strike_volatility'].unique().max()].reset_index(drop=True).iloc[0]['EXP_date']
        needed_put_short = df_chains[df_chains['EXP_date'] == needed_exp_date].reset_index(drop=True)
        needed_put_strike = nearest_equal_abs(needed_put_short['strike'].dropna(), current_price)
        needed_put_short = needed_put_short[needed_put_short['strike'] == needed_put_strike].reset_index(drop=True).iloc[0]

        print('---------------- needed_put_short ---------------------')
        print(needed_put_short['EXP_date'])
        print(needed_put_short['strike'])
        print(needed_put_short['delta'])
        #
        # put_delta_short = needed_put_short['delta']
        # needed_put_long = df_chains[df_chains['EXP_date'] == needed_exp_date].reset_index(drop=True)
        # put_delta_long = nearest_equal_abs(needed_put_long['delta'].dropna(), 0.05)
        # needed_put_long = needed_put_long[needed_put_long['delta'] == put_delta_long].reset_index(drop=True).iloc[0]
        # print('---------------- needed_put_long  ---------------------')
        # print(needed_put_long['EXP_date'])
        # print(needed_put_long['strike'])
        # print(needed_put_long['delta'])

        # ликвидность
        # liquidity_short = (abs(needed_put_short['ask'] - needed_put_short['bid']) / needed_put_short['strike']) * 100
        # liquidity_long = (abs(needed_put_long['ask'] - needed_put_long['bid']) / needed_put_long['strike']) * 100
    #

        position_margin, break_point, reward_risk = margin_calc(needed_put_short, current_price)
        #     базовые ратио
        gamma_theta_ratio, vega_theta_ratio, theta_margin_ratio = ratios_calc(needed_put_short, current_price)
        #  historical volatility
        hist_vol, hist_vol_regime = get_historical_vol(yahoo_df)
        # expected return

        expected_return = expected_return_calc(needed_put_short, current_price, hist_vol)
        print('expected_return', expected_return)

        expected_return_percent = (expected_return / position_margin) * 100

        print('expected_return_percent', expected_return_percent)

        proba_below = get_proba_below(needed_put_short, current_price, hist_vol)

        print('proba_below', proba_below)

        # price_df = yf.download(tick)
        trend_value, RSI = trend(yahoo_df)
        print('current_iv_percentile', current_iv_percentile)

        # Получить сигнал по PCR с стратегиста

        # ------ MAX PAIN ---------

        df_chains_for_max_pain = df_chains_for_max_pain[df_chains_for_max_pain['EXP_date'] == needed_exp_date].reset_index(drop=True)
        max_pain_val = get_max_pain(df_chains_for_max_pain)

        print('max_pain_val', max_pain_val)

        # ------ ROI/day ---------
        ROI_day = (expected_return/position_margin)/needed_put_short['days_to_exp']

        #  ------ Dividend Yield ---------
        try:
            if worksheet_df.loc[tick]['Dividend Yield'] > worksheet_df.loc[tick]['Dividend Yield Median']:
                div_signal = 'Dividend Yield > Median'
            else:
                div_signal = 'Dividend Yield < Median'
        except:
            div_signal = 'Empty'

        print(div_signal)

        # put_long_strike_list.append(needed_put_long['strike'])
        put_short_strike_list.append(needed_put_short['strike'])
        exp_date_list.append(needed_put_short['EXP_date'])
        possition_margin_list.append(position_margin)
        gamma_theta_ratio_list.append(gamma_theta_ratio)
        vega_theta_ratio_list.append(vega_theta_ratio)
        expected_return_list.append(expected_return)
        expected_return_percent_list.append(expected_return_percent)
        iv_percentile_list.append(current_iv_percentile)
        break_point_list.append(break_point)
        proba_below_list.append(proba_below)
        reward_risk_list.append(reward_risk)
        trend_list.append(trend_value)
        max_paint_list.append(max_pain_val)
        # liquidity_short_list.append(liquidity_short)
        # liquidity_long_list.append(liquidity_long)
        hist_vol_list.append(hist_vol)
        hist_vol_stage_list.append(hist_vol_regime)
        iv_stage_list.append(iv_regime)
        theta_margin_ratio_list.append(theta_margin_ratio)
        ROI_day_list.append(ROI_day)
        RSI_list.append(RSI)
        div_list.append(div_signal)


    except Exception as e:
        print(e)
        # put_long_strike_list.append(np.nan)
        put_short_strike_list.append(np.nan)
        possition_margin_list.append(np.nan)
        gamma_theta_ratio_list.append(np.nan)
        vega_theta_ratio_list.append(np.nan)
        expected_return_list.append(np.nan)
        expected_return_percent_list.append(np.nan)
        iv_percentile_list.append(np.nan)
        break_point_list.append(np.nan)
        proba_below_list.append(np.nan)
        reward_risk_list.append(np.nan)
        trend_list.append(np.nan)
        exp_date_list.append(np.nan)
        max_paint_list.append(np.nan)
        # liquidity_short_list.append(np.nan)
        # liquidity_long_list.append(np.nan)
        hist_vol_list.append(np.nan)
        hist_vol_stage_list.append(np.nan)
        iv_stage_list.append(np.nan)
        theta_margin_ratio_list.append(np.nan)
        ROI_day_list.append(np.nan)
        RSI_list.append(np.nan)
        div_list.append(np.nan)
        pass

FINISH_DF = pd.DataFrame(
    {
        'Symbol': ticker_list,
        'Exp_Date': exp_date_list,
        # 'PUT_Long_Strike': put_long_strike_list,
        'PUT_Short_Strike': put_short_strike_list,
        'Max_Pain': max_paint_list,
        'Gamma_Theta_Ratio': gamma_theta_ratio_list,
        'Vega_Theta_Ratio': vega_theta_ratio_list,
        'Theta_Margin_Ratio': theta_margin_ratio_list,
        'Margin': possition_margin_list,
        'Rxpected_Return': expected_return_list,
        'ROI_Day': ROI_day_list,
        'Rxpected_Return_Percent': expected_return_percent_list,
        'Hist_Volatility': hist_vol_list,
        'Hist_Vol_Stage': hist_vol_stage_list,
        'IV_Percentile': iv_percentile_list,
        'IV_Stage': iv_stage_list,
        'Break Point': break_point_list,
        'Proba_Below': proba_below_list,
        'Reward_Risk': reward_risk_list,
        # 'Earnings': earnings_list,
        # 'EVR': EVR_list,
        # 'Events_Available': events_available,
        # 'PCR_Signal': strategist_pcr_signals,
        'Trend': trend_list,
        # 'Liquidity_Short': liquidity_short_list,
        'RSI': RSI_list,
        'Dividend Yield': div_list,
    }
)

# gf_screener = gf_screener.merge(FINISH_DF, on='Symbol')
# gf_screener.to_excel('gf_screener.xlsx', index=False)

FINISH_DF.to_excel('gf_screener_ETF.xlsx', index=False)