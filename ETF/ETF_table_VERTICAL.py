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


def get_tech_data(df):
    df['RSI'] = pta.rsi(df['Close'])
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_100'] = df['Close'].rolling(window=100).mean()

    print(df)

    sma_20 = df['SMA_20'].iloc[-1]
    sma_100 = df['SMA_100'].iloc[-1]
    rsi = df['RSI'].iloc[-1]

    return sma_20, sma_100, rsi

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




def get_avalible_exp_dates(ticker, limit_date_expiration_min):
    with client.connect():  # Make any requests for data inside this block. Requests made outside this block wont run.
        exp_date_data = client.get_expirations(ticker).dt.date
        all_exp_date = exp_date_data[exp_date_data > limit_date_expiration_min].reset_index(drop=True)

        strike_list =[]

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
                req=OptionReqType.QUOTE,  # End of day data   GREEKS
                root=ticker,
                exp=exp_date,
                strike=strike,
                right=right,
                date_range=DateRange(datetime.date(2020, 1, 1), exp_date),
                interval_size=3_600_000
            )

        print('out')
        print(out.columns)
        # out.columns = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'COUNT', 'DATE']
        out.columns = ['MS_OF_DAY', 'BID_SIZE', 'BID_CONDITION', 'BID', 'BID_EXCHANGE', 'ASK_SIZE', 'ASK_CONDITION',
                        'ASK', 'ASK_EXCHANGE', 'DATE']
        # out['days_to_exp'] = (exp_date - out['DATE']).dt.days
        out = out.groupby('DATE').mean()
        print('out')
        print(out)
        str_exp_date = datetime.datetime.strftime(exp_date, "%Y-%m-%d")
        str_exp_date = datetime.datetime.strptime(str_exp_date, "%Y-%m-%d")
        # datetime.datetime.strptime(str_exp_date, "%Y-%m-%d")
        out['exp_date'] = [exp_date] * len(out)
        out['DATE'] = pd.to_datetime(out.index.tolist())
        out['days_to_exp'] = (str_exp_date - out['DATE'])
        out['days_to_exp'] = out['days_to_exp'].dt.days
        out['Side'] = [side] * len(out)
        out['Strike'] = [strike] * len(out)

        print('out2')
        print(out)

    except Exception as tt:
        print(tt)
        out = pd.DataFrame()

    return out


def nearest_equal(lst, target):
    # ближайшее значение к таргету относительно переданного списка
    return min(lst, key=lambda x: abs(x - target))



client = ThetaClient(username='itmednov@gmail.com',
                     passwd='MSIGX6600')


# # ================ раббота с таблицей============================================
gc = gd.service_account(filename='Seetus.json')
worksheet = gc.open("IBKR").worksheet("ETF")
worksheet_spark = gc.open("IBKR").worksheet("sparkline")

worksheet_df_len = pd.DataFrame(worksheet.get_all_records())[:-1]

print(worksheet_df_len)

for i in range(len(worksheet_df_len))[7:8]:

    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename='Seetus.json')
    worksheet = gc.open("IBKR").worksheet("ETF")
    worksheet_spark = gc.open("IBKR").worksheet("sparkline")

    worksheet_df = pd.DataFrame(worksheet.get_all_records())[:-1]

    print(worksheet_df)

    tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]

    print(f'-----------  {tick} -----------------')

    yahoo_data = yf.download(tick)

    # -----------  PCR -----------------
    limit_date_expiration_min_PCR = datetime.datetime.now().date() - relativedelta(days=300)

    exp_date_list, strike_list = get_avalible_exp_dates(tick, limit_date_expiration_min_PCR)

    side_list = ['P', 'C']

    full_df = pd.DataFrame()

    for exp_date, strike_listus in zip(exp_date_list, strike_list):
        print(strike_listus)
        for strike in strike_listus:
            for side in side_list:
                # print('exp_date')
                # print(type(exp_date))
                # print('strike')
                # print(int(strike))
                one_strike_df = get_option_chains(exp_date, strike, side, tick)
                full_df = pd.concat([full_df, one_strike_df])
                # print(pcr_df)

    full_df.to_csv(f'full_df_{tick}.csv', index=False)

client.close_stream()
