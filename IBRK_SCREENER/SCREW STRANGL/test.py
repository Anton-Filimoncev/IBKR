import requests
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
import yfinance as yf
import numpy as np
import mibian
import asyncio
import aiohttp

KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"


async def get_market_data(session, url):
    async with session.get(url) as resp:
        # try:
        market_data = await resp.json(content_type=None)
        print('market_data')
        print(market_data)
        option_chain_df = pd.DataFrame(market_data)

        return option_chain_df
        # except:
        #     pass


async def get_prime(exp_date_list, tick, side):
    option_chain_df = pd.DataFrame()

    async with aiohttp.ClientSession() as session:

        tasks = []
        for exp in exp_date_list:
            print(exp)
            url = f"https://api.marketdata.app/v1/options/chain/{tick}/?token={KEY}&expiration={exp}&side={side}"  #
            tasks.append(asyncio.create_task(get_market_data(session, url)))

        solo_exp_chain = await asyncio.gather(*tasks)

        for chain in solo_exp_chain:
            print(chain)
            option_chain_df = pd.concat([option_chain_df, chain])
            #
            # try:
            #     return_df = return_df.merge(prime, how='right', on=['updated'])  # .bfill(axis='rows')
            # except Exception as er:
            #     # print('except')
            #     # print(er)
            #     return_df = prime

    option_chain_df['updated'] = pd.to_datetime(option_chain_df['updated'], unit='s')
    option_chain_df['EXP_date'] = pd.to_datetime(option_chain_df['expiration'], unit='s', errors='coerce')
    option_chain_df['days_to_exp'] = (option_chain_df['EXP_date'] - option_chain_df['updated']).dt.days
    option_chain_df = option_chain_df.reset_index(drop=True)

    return option_chain_df


def get_df_chains(tick, limit_date_min, limit_date_max, side):

    url_exp = f"https://api.marketdata.app/v1/options/expirations/{tick}/?token={KEY}"
    response_exp = requests.request("GET", url_exp)
    expirations_df = pd.DataFrame(response_exp.json())
    expirations_df['expirations'] = pd.to_datetime(expirations_df['expirations'], format='%Y-%m-%d')
    expirations_df = expirations_df[expirations_df['expirations'] > limit_date_min]
    expirations_df = expirations_df[expirations_df['expirations'] < limit_date_max]

    print(expirations_df)

    option_chain_df = asyncio.run(get_prime(expirations_df['expirations'], tick, side))
    print('option_chain_df')
    print(option_chain_df)

    return option_chain_df

def nearest_equal_abs(lst, target):
    return min(lst, key=lambda x: abs(abs(x) - target))

def get_atm_strikes(chains_df, current_price):
    chains_df['ATM_strike_volatility'] = np.nan
    for exp in chains_df['EXP_date'].unique():
        solo_exp_df = chains_df[chains_df['EXP_date'] == exp]
        atm_strike = nearest_equal_abs(solo_exp_df['strike'].tolist(), current_price)
        atm_put_volatility = solo_exp_df[solo_exp_df['strike'] == atm_strike]['iv'].reset_index(drop=True).iloc[0]
        chains_df.loc[chains_df['EXP_date'] == exp, "ATM_strike_volatility"] = atm_put_volatility

    return chains_df

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

tick = 'SPY'

current_price = yf.download(tick)['Close'].iloc[-1]

limit_date_min = datetime.datetime.now() + relativedelta(days=+30)
limit_date_max = datetime.datetime.now() + relativedelta(days=+120)
df_chains = get_df_chains(tick, limit_date_min, limit_date_max)


put_df = df_chains[df_chains['side'] == 'put'].reset_index(drop=True)
put_df = put_df[put_df['strike'] < current_price]
print(df_chains)

put_df = get_atm_strikes(put_df, current_price)
put_df = get_BS_prices(current_price, 'P', put_df)
print('---------------- get_BS_prices  ---------------------')
print(put_df)
put_df['Difference'] = put_df['bid'] - put_df['BS_PRICE']
print('---------------- df_chains  ---------------------')


put_df.to_excel(f'df_chains.xlsx')

df_chains = df_chains[df_chains['strike'] < current_price]
needed_exp_date = df_chains[df_chains['Difference'] == df_chains['Difference'].max()].reset_index(drop=True).iloc[0][
    'EXP_date']
needed_put_short = df_chains[df_chains['EXP_date'] == needed_exp_date].reset_index(drop=True)
needed_put_strike = nearest_equal_abs(needed_put_short['strike'].dropna(), current_price)
needed_put_short = needed_put_short[needed_put_short['strike'] == needed_put_strike].reset_index(drop=True).iloc[0]

print('---------------- needed_put_short ---------------------')
print(needed_put_short['EXP_date'])
print(needed_put_short['strike'])
print(needed_put_short['delta'])

put_delta_short = needed_put_short['delta']
needed_put_long = df_chains[df_chains['EXP_date'] == needed_exp_date].reset_index(drop=True)
put_delta_long = nearest_equal_abs(needed_put_long['delta'].dropna(), 0.2)
needed_put_long = needed_put_long[needed_put_long['delta'] == put_delta_long].reset_index(drop=True).iloc[0]

print('---------------- needed_put_long  ---------------------')
print(needed_put_long['EXP_date'])
print(needed_put_long['strike'])
print(needed_put_long['delta'])


# url = f"https://api.marketdata.app/v1/options/chain/AAPL/?token={KEY}&from=2023-07-26&to=2025-07-26"
#
# response = requests.request("GET", url)
# print(response)
# response_df = pd.DataFrame(response.json())
# print(response_df)
# response_df.to_excel('response_df.xlsx')