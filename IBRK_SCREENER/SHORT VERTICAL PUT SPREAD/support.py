import pandas as pd
import numpy as np
from ib_insync import *
import asyncio
import aiohttp
# import scipy.stats as stats
import requests
import datetime
import time
from dateutil.relativedelta import relativedelta
import pickle
import pandas_ta as pta
from sklearn import mixture as mix
import scipy.stats as stats
import pandas_ta as pta

KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"

def nearest_equal(lst, target):
    # ближайшее значение к таргету относительно переданного списка
    return min(lst, key=lambda x: abs(x - target))

def nearest_equal_abs(lst, target):
    return min(lst, key=lambda x: abs(abs(x) - target))

def needed_strike_delta(all_contract_df, delta, position):
    if position == 'short':
        needed_delta = nearest_equal_abs(all_contract_df['Delta bid'].tolist(), delta)
        needed_strike = all_contract_df[all_contract_df['Delta bid'] == needed_delta]['Strike'].reset_index(drop=True).iloc[0]

    if position == 'long':
        needed_delta = nearest_equal_abs(all_contract_df['Delta ask'].tolist(), delta)
        needed_strike = all_contract_df[all_contract_df['Delta ask'] == needed_delta]['Strike'].reset_index(drop=True).iloc[0]

    return needed_strike


async def get_market_data(session, url):
    async with session.get(url) as resp:
        market_data = await resp.json(content_type=None)
        option_chain_df = pd.DataFrame(market_data)

        return option_chain_df


async def get_prime(exp_date_list, tick):
    option_chain_df = pd.DataFrame()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for exp in exp_date_list:
            url = f"https://api.marketdata.app/v1/options/chain/{tick}/?token={KEY}&expiration={exp}"  #
            tasks.append(asyncio.create_task(get_market_data(session, url)))

        solo_exp_chain = await asyncio.gather(*tasks)

        for chain in solo_exp_chain:
            option_chain_df = pd.concat([option_chain_df, chain])

    option_chain_df['updated'] = pd.to_datetime(option_chain_df['updated'], unit='s')
    option_chain_df['EXP_date'] = pd.to_datetime(option_chain_df['expiration'], unit='s', errors='coerce')
    option_chain_df['days_to_exp'] = (option_chain_df['EXP_date'] - option_chain_df['updated']).dt.days
    option_chain_df = option_chain_df.reset_index(drop=True)

    return option_chain_df


def get_df_chains(tick, limit_date_min, limit_date_max):
    url_exp = f"https://api.marketdata.app/v1/options/expirations/{tick}/?token={KEY}"
    response_exp = requests.request("GET", url_exp)
    expirations_df = pd.DataFrame(response_exp.json())
    expirations_df['expirations'] = pd.to_datetime(expirations_df['expirations'], format='%Y-%m-%d')
    expirations_df = expirations_df[expirations_df['expirations'] > limit_date_min]
    expirations_df = expirations_df[expirations_df['expirations'] < limit_date_max]
    print(expirations_df)
    option_chain_df = asyncio.run(get_prime(expirations_df['expirations'], tick))

    return option_chain_df

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


def get_ib_data(tick, yahoo_df, ib):
    try:
        contract = Stock(tick, 'SMART', 'USD')
        bars = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='365 D',
            barSizeSetting='1 day', whatToShow='OPTION_IMPLIED_VOLATILITY', useRTH=True)
        df_iv = util.df(bars)
        test = df_iv['close'].rolling(364).apply(
            lambda x: stats.percentileofscore(x, x.iloc[-1]))

    except Exception as e:
        print(e)
        print('Work with ARCA')
        contract = Stock(tick, 'ARCA', 'USD')
        bars = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='365 D',
            barSizeSetting='1 day', whatToShow='OPTION_IMPLIED_VOLATILITY', useRTH=True)
        df_iv = util.df(bars)
        test = df_iv['close'].rolling(364).apply(
            lambda x: stats.percentileofscore(x, x.iloc[-1]))

    current_price = yahoo_df['Close'].iloc[-1]

    # STAGE =========================================================================
    df_iv = df_iv.set_index('date')
    print(df_iv)

    unsup = mix.GaussianMixture(n_components=4,
                                covariance_type="spherical",
                                n_init=100,
                                random_state=42)

    unsup.fit(np.reshape(df_iv, (-1, df_iv.shape[1])))

    regime = unsup.predict(np.reshape(df_iv, (-1, df_iv.shape[1])))
    df_iv['Return'] = np.log(df_iv['close'] / df_iv['close'].shift(1))
    Regimes = pd.DataFrame(regime, columns=['Regime'], index=df_iv.index) \
        .join(df_iv, how='inner') \
        .assign(market_cu_return=df_iv.Return.cumsum()) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'Date'})

    Regimes = Regimes.dropna()

    one_period_price_mean = Regimes[Regimes['Regime'] == 0]['close'].max()
    two_period_price_mean = Regimes[Regimes['Regime'] == 1]['close'].max()
    three_period_price_mean = Regimes[Regimes['Regime'] == 2]['close'].max()
    four_period_price_mean = Regimes[Regimes['Regime'] == 3]['close'].max()

    print([one_period_price_mean, two_period_price_mean, three_period_price_mean, four_period_price_mean])

    lisusss = [one_period_price_mean, two_period_price_mean, three_period_price_mean, four_period_price_mean]
    lisusss_sort = sorted(lisusss)
    print(lisusss_sort)

    period_set = {0: lisusss_sort.index(lisusss[0]) + 1,
                  1: lisusss_sort.index(lisusss[1]) + 1,
                  2: lisusss_sort.index(lisusss[2]) + 1,
                  3: lisusss_sort.index(lisusss[3]) + 1,
                  }

    Regimes_plot = Regimes.copy()

    Regimes_plot['Regime'] = Regimes_plot['Regime'].replace(period_set)

    # PERCENTILE =====================================================================

    df_iv['IV_percentile'] = df_iv['close'].rolling(364).apply(
        lambda x: stats.percentileofscore(x, x.iloc[-1]))
    iv_percqntile = df_iv['IV_percentile'].iloc[-1]

    return current_price, iv_percqntile, Regimes_plot['Regime'].iloc[-1]

def get_historical_vol(yahoo_data):
    TRADING_DAYS = 200
    returns = np.log(yahoo_data['Close'] / yahoo_data['Close'].shift(1))
    returns.fillna(0, inplace=True)
    volatility = returns.rolling(window=TRADING_DAYS).std() * np.sqrt(TRADING_DAYS)

    volatility = volatility.to_frame().dropna()
    volatility = volatility[-200:]

    unsup = mix.GaussianMixture(n_components=4,
                                covariance_type="spherical",
                                n_init=100,
                                random_state=42)

    unsup.fit(np.reshape(volatility, (-1, volatility.shape[1])))

    regime = unsup.predict(np.reshape(volatility, (-1, volatility.shape[1])))
    volatility['Return'] = np.log(volatility['Close'] / volatility['Close'].shift(1))
    Regimes = pd.DataFrame(regime, columns=['Regime'], index=volatility.index) \
        .join(volatility, how='inner') \
        .assign(market_cu_return=volatility.Return.cumsum()) \
        .reset_index(drop=False) \
        .rename(columns={'index': 'Date'})

    Regimes = Regimes.dropna()

    one_period_price_mean = Regimes[Regimes['Regime'] == 0]['Close'].max()
    two_period_price_mean = Regimes[Regimes['Regime'] == 1]['Close'].max()
    three_period_price_mean = Regimes[Regimes['Regime'] == 2]['Close'].max()
    four_period_price_mean = Regimes[Regimes['Regime'] == 3]['Close'].max()

    lisusss = [one_period_price_mean, two_period_price_mean, three_period_price_mean, four_period_price_mean]
    lisusss_sort = sorted(lisusss)


    period_set = {0: lisusss_sort.index(lisusss[0]) + 1,
                  1: lisusss_sort.index(lisusss[1]) + 1,
                  2: lisusss_sort.index(lisusss[2]) + 1,
                  3: lisusss_sort.index(lisusss[3]) + 1,
                  }

    Regimes_plot = Regimes.copy()

    Regimes_plot['Regime'] = Regimes_plot['Regime'].replace(period_set)


    return volatility['Close'].iloc[-1], Regimes_plot['Regime'].iloc[-1]