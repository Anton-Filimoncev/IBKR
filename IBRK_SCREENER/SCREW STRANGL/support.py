import pandas as pd
import numpy as np
from ib_insync import *
# import asyncio
# import scipy.stats as stats
import requests
import datetime
import time
from dateutil.relativedelta import relativedelta
import pickle
import pandas_ta as pta
import scipy.stats as stats
import asyncio
import aiohttp

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

def get_atm_strikes(chains_df, current_price):
    chains_df['ATM_strike_volatility'] = np.nan
    for exp in chains_df['EXP_date'].unique():
        solo_exp_df = chains_df[chains_df['EXP_date'] == exp]
        atm_strike = nearest_equal(solo_exp_df['strike'].tolist(), current_price)
        atm_put_volatility = solo_exp_df[solo_exp_df['strike'] == atm_strike]['iv'].reset_index(drop=True).iloc[0]
        chains_df.loc[chains_df['EXP_date'] == exp, "ATM_strike_volatility"] = atm_put_volatility

    return chains_df

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


def get_ib_data(tick, yahoo_df, ib):
    try:
        contract = Stock(tick, 'SMART', 'USD')
        bars = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='365 D',
            barSizeSetting='1 day', whatToShow='OPTION_IMPLIED_VOLATILITY', useRTH=True)
        df_iv = util.df(bars)
        df_iv['IV_percentile'] = df_iv['close'].rolling(364).apply(
            lambda x: stats.percentileofscore(x, x.iloc[-1]))
    except Exception as e:
        print(e)
        print('Work with ARCA')
        contract = Stock(tick, 'ARCA', 'USD')
        bars = ib.reqHistoricalData(
            contract, endDateTime='', durationStr='365 D',
            barSizeSetting='1 day', whatToShow='OPTION_IMPLIED_VOLATILITY', useRTH=True)
        df_iv = util.df(bars)
        df_iv['IV_percentile'] = df_iv['close'].rolling(364).apply(
            lambda x: stats.percentileofscore(x, x.iloc[-1]))

    current_price = yahoo_df['Close'].iloc[-1]

    return current_price, df_iv['IV_percentile'].iloc[-1]