import pandas as pd
import numpy as np
import os
import time
import pickle
import gspread as gd
from ib_insync import *
from scipy import stats
from sklearn import mixture as mix
import yfinance as yf
import pandas_ta as pta
import datetime
from dateutil.relativedelta import relativedelta
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange, SecType, StockReqType
import requests


def market_stage_ticker(ticker, ib):
    # ==================================================== IB ==============================================================

    # ib = IB()
    # try:
    #     ib.connect('127.0.0.1', 7497, clientId=12)  # 7497
    #
    # except:
    #     ib.connect('127.0.0.1', 7497, clientId=12)

    IV_list = []
    hist_list = []
    iv_hist_list = []
    vega_risk_list = []

    try:
        print('==========================================   ', ticker,
              '  =============================================')

        #  ========================================  получение волатильности

        exch = 'SMART'
        if ticker == 'GDX' or ticker == 'GDXJ' or ticker == 'REMX':
            exch = 'ARCA'
        contract = Stock(ticker, exch, 'USD')
        bars = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='365 D',
            barSizeSetting='1 day', whatToShow='OPTION_IMPLIED_VOLATILITY', useRTH=True)

        df = util.df(bars)

        print('df')
        print(df)

        vega_risk = round(df.close.iloc[-1] - df[-22:].close.min(), 2)
        # vega_risk_list.append(vega_risk * 100)

    except:
        df = pd.DataFrame()

    # HIST VOLATILITY ====================================
    try:
        print('==========================================   ', ticker,
              '  =============================================')

        #  ========================================  получение волатильности
        contract = Stock(ticker, exch, 'USD')
        bars_hist = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='365 D',
            barSizeSetting='1 day', whatToShow='HISTORICAL_VOLATILITY', useRTH=True)

        df_hist = util.df(bars_hist)

    except:
        df_hist = pd.DataFrame()

    df = df.set_index('date')

    df_hist = df_hist.set_index('date')

    df = df.dropna()
    print(df)

    unsup = mix.GaussianMixture(n_components=4,
                                covariance_type="spherical",
                                n_init=100,
                                random_state=42)

    unsup.fit(np.reshape(df, (-1, df.shape[1])))

    regime = unsup.predict(np.reshape(df, (-1, df.shape[1])))
    df['Return'] = np.log(df['close'] / df['close'].shift(1))
    Regimes = pd.DataFrame(regime, columns=['Regime'], index=df.index) \
        .join(df, how='inner') \
        .assign(market_cu_return=df.Return.cumsum()) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'Date'})

    Regimes = Regimes.dropna()

    one_period_price_mean = Regimes[Regimes['Regime'] == 0]['close'].max()
    two_period_price_mean = Regimes[Regimes['Regime'] == 1]['close'].max()
    three_period_price_mean = Regimes[Regimes['Regime'] == 2]['close'].max()
    four_period_price_mean = Regimes[Regimes['Regime'] == 3]['close'].max()

    lisusss = [one_period_price_mean, two_period_price_mean, three_period_price_mean, four_period_price_mean]
    lisusss_sort = sorted(lisusss)

    period_set = {0: lisusss_sort.index(lisusss[0]) + 1,
                  1: lisusss_sort.index(lisusss[1]) + 1,
                  2: lisusss_sort.index(lisusss[2]) + 1,
                  3: lisusss_sort.index(lisusss[3]) + 1,
                  }

    Regimes_plot = Regimes.copy()

    Regimes_plot['Regime'] = Regimes_plot['Regime'].replace(period_set)

    one_period_days = len(Regimes_plot[Regimes_plot['Regime'] == 1])
    two_period_days = len(Regimes_plot[Regimes_plot['Regime'] == 2])
    three_period_days = len(Regimes_plot[Regimes_plot['Regime'] == 3])
    four_period_days = len(Regimes_plot[Regimes_plot['Regime'] == 4])
    full_period_days = len(Regimes_plot)

    one_period_price_min = round(Regimes_plot[Regimes_plot['Regime'] == 1]['close'].min(), 2)
    one_period_price_max = round(Regimes_plot[Regimes_plot['Regime'] == 1]['close'].max(), 2)

    two_period_price_min = round(Regimes_plot[Regimes_plot['Regime'] == 2]['close'].min(), 2)
    two_period_price_max = round(Regimes_plot[Regimes_plot['Regime'] == 2]['close'].max(), 2)

    three_period_price_min = round(Regimes_plot[Regimes_plot['Regime'] == 3]['close'].min(), 2)
    three_period_price_max = round(Regimes_plot[Regimes_plot['Regime'] == 3]['close'].max(), 2)

    four_period_price_min = round(Regimes_plot[Regimes_plot['Regime'] == 4]['close'].min(), 2)
    four_period_price_max = round(Regimes_plot[Regimes_plot['Regime'] == 4]['close'].max(), 2)

    # ================================================     hist vol ======================
    unsup_hist = mix.GaussianMixture(n_components=4,
                                     covariance_type="spherical",
                                     n_init=100,
                                     random_state=42)

    unsup_hist.fit(np.reshape(df_hist, (-1, df_hist.shape[1])))

    regime = unsup_hist.predict(np.reshape(df_hist, (-1, df_hist.shape[1])))
    df_hist['Return'] = np.log(df_hist['close'] / df_hist['close'].shift(1))
    Regimes_hist = pd.DataFrame(regime, columns=['Regime'], index=df_hist.index) \
        .join(df_hist, how='inner') \
        .assign(market_cu_return=df_hist.Return.cumsum()) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'Date'})

    Regimes_hist = Regimes_hist.dropna()

    one_period_price_mean_hist = Regimes_hist[Regimes_hist['Regime'] == 0]['close'].max()
    two_period_price_mean_hist = Regimes_hist[Regimes_hist['Regime'] == 1]['close'].max()
    three_period_price_mean_hist = Regimes_hist[Regimes_hist['Regime'] == 2]['close'].max()
    four_period_price_mean_hist = Regimes_hist[Regimes_hist['Regime'] == 3]['close'].max()

    print([one_period_price_mean_hist, two_period_price_mean_hist, three_period_price_mean_hist,
           four_period_price_mean_hist])

    lisusss_hist = [one_period_price_mean_hist, two_period_price_mean_hist, three_period_price_mean_hist,
                    four_period_price_mean_hist]
    lisusss_sort_hist = sorted(lisusss_hist)
    print(lisusss_sort_hist)

    period_set_hist = {0: lisusss_sort_hist.index(lisusss_hist[0]) + 1,
                       1: lisusss_sort_hist.index(lisusss_hist[1]) + 1,
                       2: lisusss_sort_hist.index(lisusss_hist[2]) + 1,
                       3: lisusss_sort_hist.index(lisusss_hist[3]) + 1,
                       }

    Regimes_hist['Regime'] = Regimes_hist['Regime'].replace(period_set_hist)

    percentile = round(stats.percentileofscore(Regimes_plot['close'], Regimes_plot['close'].iloc[-1]), 2)
    print('percentile')
    print(percentile)

    IV_Regime = Regimes_plot['Regime'].iloc[-1]
    HV_Regime = Regimes_hist['Regime'].iloc[-1]
    IV_Median = Regimes_plot[int(len(Regimes_plot) / 2):]['close'].median()
    HV_Median = Regimes_hist[int(len(Regimes_hist) / 2):]['close'].median()
    IV = Regimes_plot['close'].iloc[-1]

    HV_20 = Regimes_hist['close'].rolling(window=20).mean().iloc[-1]
    HV_50 = Regimes_hist['close'].rolling(window=50).mean().iloc[-1]
    HV_100 = Regimes_hist['close'].rolling(window=100).mean().iloc[-1]

    df['IV_percentile'] = df['close'].rolling(364).apply(
        lambda x: stats.percentileofscore(x, x.iloc[-1]))
    IV_percentile = df['IV_percentile'].iloc[-1]

    # ib.disconnect()

    return vega_risk, IV_percentile, IV_Regime, IV_Median, IV, HV_Regime, HV_20, HV_50, HV_100, HV_Regime


# подключение к гугл таблице


def total_loss_on_strike(chain, expiry_price, opt_type):
    '''
    Get's the total loss at the given strike price
    '''
    # call options with strike price below the expiry price -> loss for option writers
    if opt_type == 'call':
        in_money = chain[chain['Strike'] < expiry_price][["callOpenInterest", "Strike"]]
        in_money["Loss"] = (expiry_price - in_money['Strike']) * in_money["callOpenInterest"]

    if opt_type == 'put':
        in_money = chain[chain['Strike'] > expiry_price][["putOpenInterest", "Strike"]]
        in_money["Loss"] = (in_money['Strike'] - expiry_price) * in_money["putOpenInterest"]

    return in_money["Loss"].sum()


def chain_converter(tickers):
    # разбиваем контракты по грекам и страйкам, для того, что бы удобнее было строить позиции
    # со сложными условиями входа

    iv_bid = []
    iv_ask = []
    delta_bid = []
    delta_ask = []
    gamma_bid = []
    gamma_ask = []
    vega_bid = []
    vega_ask = []
    theta_bid = []
    theta_ask = []
    strike_list = []
    right_list = []
    exp_date_list = []

    for ticker in tickers:
        try:

            iv_bid.append(ticker.bidGreeks.impliedVol)
            iv_ask.append(ticker.askGreeks.impliedVol)
            delta_bid.append(ticker.bidGreeks.delta)
            delta_ask.append(ticker.askGreeks.delta)
            gamma_bid.append(ticker.bidGreeks.gamma)
            gamma_ask.append(ticker.askGreeks.gamma)
            vega_bid.append(ticker.bidGreeks.vega)
            vega_ask.append(ticker.askGreeks.vega)
            theta_bid.append(ticker.bidGreeks.theta)
            theta_ask.append(ticker.askGreeks.theta)
            strike_list.append(ticker.contract.strike)
            right_list.append(ticker.contract.right)
            exp_date_list.append(ticker.contract.lastTradeDateOrContractMonth)

        except:
            pass

    greek_df = pd.DataFrame(
        {
            'IV bid': iv_bid,
            'IV ask': iv_ask,
            'Delta bid': delta_bid,
            'Delta ask': delta_ask,
            'Gamma bid': gamma_bid,
            'Gamma ask': gamma_ask,
            'Vega bid': vega_bid,
            'Vega ask': vega_ask,
            'Theta bid': theta_bid,
            'Theta ask': theta_ask,
            'Strike': strike_list,
            'Right': right_list,
            'EXP_date': exp_date_list,
        }
    )

    df_chains = util.df(tickers)
    df_chains['time'] = df_chains['time'].dt.tz_localize(None)
    df_chains = pd.concat([df_chains, greek_df], axis=1)

    return df_chains


def get_df_chains(ticker_contract, limit_date_min, limit_date_max, tick, rights, ib):
    expirations_filter_list_date = []
    expirations_filter_list_strike = []

    chains = ib.reqSecDefOptParams(ticker_contract.symbol, '', ticker_contract.secType, ticker_contract.conId)
    chain = next(c for c in chains if c.tradingClass == tick and c.exchange == 'SMART')

    # фильтрация будущих контрактов по времени
    for exp in chain.expirations:
        year = exp[:4]
        month = exp[4:6]
        day = exp[6:]
        date = year + '-' + month + '-' + day
        datime_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        print('---')
        print(datime_date)
        print(limit_date_min)
        print(limit_date_max)
        if datime_date >= limit_date_min and datime_date <= limit_date_max:
            expirations_filter_list_date.append(exp)

    # print('expirations_filter_list_date', expirations_filter_list_date)
    print('strikes', chain.strikes)
    print('expirations', chain.expirations)
    # фильтрация страйков относительно текущей цены
    time.sleep(4)

    for strikus in chain.strikes:
        expirations_filter_list_strike.append(strikus)

    time.sleep(4)

    contracts = [Option(tick, expiration, strike, right, 'SMART', tradingClass=tick)
                 for right in rights
                 for expiration in [expirations_filter_list_date[0]]
                 # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                 for strike in expirations_filter_list_strike]

    contracts = ib.qualifyContracts(*contracts)
    ib.sleep(3)
    print('contracts')
    print(contracts)

    return contracts


def max_pain(tick, ib):
    # ib = IB()
    # try:
    #     ib.connect('127.0.0.1', 7497, clientId=12)  # 7497
    #
    # except:
    #     ib.connect('127.0.0.1', 7497, clientId=12)

    rights = ['P', 'C']

    exch = 'SMART'
    if tick == 'GDX' or tick == 'GDXJ' or tick == 'REMX':
        exch = 'ARCA'

    contract = Stock(tick, exch, 'USD')

    # получение айдишника тикера
    bars_id = ib.qualifyContracts(contract)
    df_bars_id = util.df(bars_id)
    ticker_id = df_bars_id['conId'].values[0]

    ticker_contract = Index(conId=ticker_id, symbol=tick, exchange='SMART', currency='USD', localSymbol=tick)
    # ticker_contract = Index('SPY', 'CBOE')
    ib.qualifyContracts(ticker_contract)
    ib.sleep(3)
    ib.reqMarketDataType(1)
    [ticker] = ib.reqTickers(ticker_contract)

    # ДАТЫ ЭКСПИРАЦИИ
    limit_date_min = datetime.datetime.now() + relativedelta(days=+20)
    limit_date_max = datetime.datetime.now() + relativedelta(days=+70)

    # получаем датасет с ценовыми рядами и греками по опционам
    contracts = get_df_chains(ticker_contract, limit_date_min, limit_date_max, tick, rights, ib)
    option_chains_df = pd.DataFrame()
    print('contracts')
    print(contracts)
    for cont in contracts:
        # try:
        # print(cont)
        req = ib.reqMktData(cont, "101")
        ib.sleep(4)
        one_position_df = util.df([req])
        print(req.contract.strike)
        one_position_df['Strike'] = req.contract.strike
        one_position_df['Side'] = req.contract.right
        print(one_position_df)

        option_chains_df = pd.concat([option_chains_df, one_position_df])
        # except:
        #     pass

    call_max_pain_list = []
    put_max_pain_list = []
    strike_list = []

    full_call = option_chains_df[option_chains_df['Side'] == 'C'].reset_index(drop=True)
    full_put = option_chains_df[option_chains_df['Side'] == 'P'].reset_index(drop=True)

    print('full_call')
    print(full_call)
    print('full_put')
    print(full_put)

    for i in range(len(full_put)):
        put_max_pain_list.append(total_loss_on_strike(full_put, full_put['Strike'][i], 'put'))
        call_max_pain_list.append(total_loss_on_strike(full_call, full_put['Strike'][i], 'call'))
        strike_list.append(full_put['Strike'][i])

    max_pain = pd.DataFrame({'PUT': put_max_pain_list,
                             'CALL': call_max_pain_list,
                             'Strike': strike_list
                             })

    max_pain_value = (max_pain['PUT'] + max_pain['CALL']).min()

    max_pain['Sum'] = max_pain['PUT'] + max_pain['CALL']
    max_pain[max_pain['Sum'] == max_pain_value]
    max_pain_strike = max_pain[max_pain['Sum'] == max_pain_value]['Strike']

    print('max_pain_strike')
    print(max_pain_strike)

    # ib.disconnect()

    return max_pain_strike


def get_avalible_exp_dates(ticker, limit_date_expiration_min):
    with client.connect():  # Make any requests for data inside this block. Requests made outside this block wont run.
        exp_date_data = client.get_expirations(ticker).dt.date
        all_exp_date = exp_date_data[exp_date_data > limit_date_expiration_min].reset_index(drop=True)

        strike_list = []

        for exp_date in all_exp_date:
            strike_list.append(client.get_strikes(ticker, exp_date).astype('float').values.tolist())

    return all_exp_date, strike_list


def get_option_chains(exp_date, strike, side, ticker) -> pd.DataFrame:
    print(exp_date)
    print(strike)
    print(side)
    print(ticker)
    try:
        with client.connect():

            if side == 'C':
                right = OptionRight.CALL
            if side == 'P':
                right = OptionRight.PUT

            # Make the request
            out = client.get_hist_option(
                req=OptionReqType.EOD,  # End of day data   GREEKS
                root=ticker,
                exp=exp_date,
                strike=strike,
                right=right,
                date_range=DateRange(datetime.date(2020, 1, 1), exp_date),
                interval_size=3_600_000
            )

        out.columns = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'COUNT', 'DATE']

        # out['days_to_exp'] = (exp_date - out['DATE']).dt.days
        out['Side'] = [side] * len(out)

    except:
        out = pd.DataFrame()

    return out


def nearest_equal(lst, target):
    # ближайшее значение к таргету относительно переданного списка
    return min(lst, key=lambda x: abs(x - target))


def nearest_equal_abs(lst, target):
    return min(lst, key=lambda x: abs(abs(x) - target))


def get_total_scew(tick, limit_date_min, limit_date_max, ib):


    rights = ['P', 'C']

    contract = Stock(tick, 'SMART', 'USD')

    # получение айдишника тикера
    bars_id = ib.qualifyContracts(contract)
    df_bars_id = util.df(bars_id)
    ticker_id = df_bars_id['conId'].values[0]

    ticker_contract = Index(conId=ticker_id, symbol=tick, exchange='SMART', currency='USD', localSymbol=tick)
    # ticker_contract = Index('SPY', 'CBOE')

    ib.qualifyContracts(ticker_contract)
    ib.sleep(3)
    ib.reqMarketDataType(1)
    [ticker] = ib.reqTickers(ticker_contract)

    current_price = ticker.marketPrice()

    # ДАТЫ ЭКСПИРАЦИИ
    # limit_date_min = datetime.datetime.now() + relativedelta(days=+25)
    # limit_date_max = datetime.datetime.now() + relativedelta(days=+60)

    # получаем датасет с ценовыми рядами и греками по опционам
    contracts = get_df_chains(ticker_contract, limit_date_min, limit_date_max, tick, rights, ib)

    tickers = ib.reqTickers(*contracts)
    ib.sleep(2)

    df_chains = chain_converter(tickers)
    print('df_chains')
    print(df_chains.columns.tolist())

    df_chains_put = df_chains[df_chains['Right'] == 'P']
    df_chains_call = df_chains[df_chains['Right'] == 'C']

    print('df_chains_put')
    print(df_chains_put)

    print('df_chains_call')
    print(df_chains_call)

    atm_strike = nearest_equal(df_chains_put['Strike'].tolist(), current_price)
    atm_put = df_chains_put[df_chains_put['Strike'] == atm_strike].reset_index(drop=True).iloc[0]
    # atm_call = df_chains_call[df_chains_call['Strike'] == atm_strike].reset_index(drop=True).iloc[0]

    print('atm_put')
    print(atm_put)

    # ib.disconnect()

    # VERTICAL SCEW

    print('Delta bid')
    print(df_chains_put['Delta bid'])

    delta_put = nearest_equal_abs(df_chains_put['Delta bid'].dropna().tolist(), 0.1)
    delta_put_IV = df_chains_put[df_chains_put['Delta bid'] == delta_put].reset_index(drop=True).iloc[0]['IV bid']
    delta_call = nearest_equal_abs(df_chains_call['Delta bid'].dropna().tolist(), 0.25)
    delta_call_IV = df_chains_call[df_chains_call['Delta bid'] == delta_call].reset_index(drop=True).iloc[0]['IV bid']

    print('delta_put_IV')
    print(delta_put_IV)
    print('delta_call_IV')
    print(delta_call_IV)

    return atm_put['IV bid'], delta_call_IV * 100, delta_put_IV * 100

# ----------------------------------   MAX PAIN ----------------------------------

def total_loss_on_strike(chain, expiry_price, opt_type):
    '''
    Get's the total loss at the given strike price
    '''
    # call options with strike price below the expiry price -> loss for option writers
    if opt_type == 'call':
        in_money = chain[chain['strike'] < expiry_price][["openInterest", "strike"]]
        in_money["Loss"] = (expiry_price - in_money['strike']) * in_money["openInterest"]

    if opt_type == 'put':
        in_money = chain[chain['strike'] > expiry_price][["openInterest", "strike"]]
        in_money["Loss"] = (in_money['strike'] - expiry_price) * in_money["openInterest"]

    return in_money["Loss"].sum()


def get_max_pain(ticker):
    current_price = yf.download(ticker)['Close'].iloc[-1]

    KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"

    unix_date_start_limit = datetime.datetime.now().timetuple()

    url = f"https://api.marketdata.app/v1/options/chain/{ticker}/?dte=30&token={KEY}"

    response_put_check = 0
    while (response_put_check != 200) and (response_put_check != 404):
        try:
            response_put = requests.request("GET", url)  # .json()
            response_put_check = response_put.status_code
            response_put = response_put.json()
        except:
            pass

    try:
        req_result = pd.DataFrame(response_put)
    except:
        req_result = pd.DataFrame(response_put, index=[0])

    if len(req_result) <= 1:
        unix_date = req_result['nextTime'][0]
        url = f"https://api.marketdata.app/v1/options/chain/{ticker}?&token={KEY}"
        response = requests.request("GET", url).json()
        req_result = pd.DataFrame(response)

    req_result['expiration'] = pd.to_datetime(req_result['expiration'], unit='s').dt.strftime('%Y-%m-%d')
    req_result['updated'] = pd.to_datetime(req_result['updated'], unit='s').dt.strftime('%Y-%m-%d')

    # ===========================================================================

    req_result['current_price'] = [current_price] * len(req_result)

    # call
    full_call = req_result[req_result['side'] == 'call'].reset_index(drop=True)

     # put
    full_put = req_result[req_result['side'] == 'put'].reset_index(drop=True)

    call_max_pain_list = []
    put_max_pain_list = []
    strike_list = []

    for i in range(len(full_put)):
        put_max_pain_list.append(total_loss_on_strike(full_put, full_put['strike'][i], 'put'))
        call_max_pain_list.append(total_loss_on_strike(full_call, full_put['strike'][i], 'call'))
        strike_list.append(full_put['strike'][i])

    max_pain = pd.DataFrame({'PUT': put_max_pain_list,
                             'CALL': call_max_pain_list,
                             'Strike': strike_list
                             })

    max_pain_value = (max_pain['PUT'] + max_pain['CALL']).min()

    max_pain['Sum'] = max_pain['PUT'] + max_pain['CALL']
    max_pain[max_pain['Sum'] == max_pain_value]
    max_pain_strike = max_pain[max_pain['Sum'] == max_pain_value]['Strike']

    print('max_pain_strike', ticker)
    print(max_pain_strike.values[0])

    return max_pain_strike.values[0]
#
# # ================ раббота с таблицей============================================
gc = gd.service_account(filename='Seetus.json')
worksheet = gc.open("IBKR").worksheet("ETF")
worksheet_spark = gc.open("IBKR").worksheet("sparkline")

worksheet_df_len = pd.DataFrame(worksheet.get_all_records())[:-1]

ib = IB()
try:
    ib.connect('127.0.0.1', 4002, clientId=12)  # 7497

except:
    ib.connect('127.0.0.1', 7496, clientId=12)

for i in range(len(worksheet_df_len)):  # указать с какой строки начать сбор [2:]

    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("ETF")
    worksheet_spark = gc.open("IBKR").worksheet("sparkline")

    worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]

    # заполняем столбцы с формулами
    for k in range(len(worksheet_df_len)):
        worksheet_df['CURRENT PRICE'].iloc[k] = f'=GOOGLEFINANCE(A{k + 2},"price")'
        worksheet_df['WEIGHT PCR sparkline'].iloc[k] = f'=sparkline(sparkline!B{k + 1}:W{k + 1})'
        worksheet_df['% BETA DELTA'].iloc[k] = f'=C{k + 2}/$C$27'

    print(worksheet_df)

    tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]
    print(f'---------    {tick}')
    yahoo_data = yf.download(tick)

    # -----------  Horizontal scew -----------------

    limit_date_min_1 = datetime.datetime.now() + relativedelta(days=+20)
    limit_date_max_1 = datetime.datetime.now() + relativedelta(days=+45)
    limit_date_min_2 = datetime.datetime.now() + relativedelta(days=+55)
    limit_date_max_2 = datetime.datetime.now() + relativedelta(days=+200)

    iv_horizontal_1_put, delta_call_IV, delta_put_IV = get_total_scew(tick, limit_date_min_1, limit_date_max_1, ib)
    iv_horizontal_2_put, delta_call_IV_2, delta_put_IV_2 = get_total_scew(tick, limit_date_min_2, limit_date_max_2, ib)

    # -----------  Vertical scew -----------------

    call_delta_max = worksheet_df['CALL 25 delta IV max'].iloc[i]
    call_delta_min = worksheet_df['CALL 25 delta IV min'].iloc[i]

    put_delta_max = worksheet_df['PUT 10 delta IV max'].iloc[i]
    put_delta_min = worksheet_df['PUT 10 delta IV min'].iloc[i]

    vertical_skew_call = 'Neutral'
    vertical_skew_put = 'Neutral'

    if delta_call_IV > call_delta_max:
        vertical_skew_call = 'UP'
    if delta_call_IV < call_delta_min:
        vertical_skew_call = 'DOWN'

    if delta_put_IV > put_delta_max:
        vertical_skew_put = 'UP'
    if delta_put_IV < put_delta_min:
        vertical_skew_call = 'DOWN'

    # ----------------------------

    put_iv_horizontal = iv_horizontal_1_put - iv_horizontal_2_put

    iv_horizontal = round(put_iv_horizontal, 4)

    # -------

    print(tick)
    vega_risk, IV_percentile, IV_Regime, IV_Median, IV, HV_Regime, HV_20, HV_50, HV_100, HV_Regime = market_stage_ticker(
        tick, ib)

    print('max_pain_START')
    max_pain_value = get_max_pain(tick)

    worksheet_df['VEGA RISK month'].iloc[i] = vega_risk
    worksheet_df['IV % year'].iloc[i] = IV_percentile
    worksheet_df['IV DIA year'].iloc[i] = IV_Regime
    worksheet_df['IV median 6 m'].iloc[i] = IV_Median
    worksheet_df['IV ATM'].iloc[i] = IV
    worksheet_df['HV 20'].iloc[i] = HV_20
    worksheet_df['HV 50'].iloc[i] = HV_50
    worksheet_df['HV 100'].iloc[i] = HV_100
    worksheet_df['HV DIA'].iloc[i] = HV_Regime



    worksheet_df['CALL MONTH  VERTICAL SCEW '].iloc[i] = vertical_skew_call
    worksheet_df['PUT MONTH VERTICAL SCEW'].iloc[i] = vertical_skew_put



    # worksheet_df['WEIGHT PCR SIGNAL'].iloc[i] = pcr_signal
    worksheet_df['MAX PAIN month'].iloc[i] = max_pain_value
    worksheet_df['Horizontal scew (IV 1 month - 2 month)'].iloc[i] = iv_horizontal
    worksheet_df = worksheet_df.fillna(0)

    worksheet_df = worksheet_df.fillna(0)
    worksheet_df.to_csv('worksheet_df.csv', index=False)
    worksheet_df = pd.read_csv('worksheet_df.csv')
    worksheet_df = worksheet_df.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(),
                     value_input_option='USER_ENTERED')

