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
                req=OptionReqType.EOD,  # End of day data   GREEKS
                root=ticker,
                exp=exp_date,
                strike=strike,
                right=right,
                date_range=DateRange(datetime.date(2020, 1, 1), exp_date),
                interval_size=3_600_000
            )


        # print('out')
        # print(out.columns)
        out.columns = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME', 'COUNT', 'DATE']
        # out.columns = ['MS_OF_DAY', 'BID_SIZE', 'BID_CONDITION', 'BID', 'BID_EXCHANGE', 'ASK_SIZE', 'ASK_CONDITION',
        #                 'ASK', 'ASK_EXCHANGE', 'DATE']

        out['Side'] = [side] * len(out)
        out['Strike'] = [strike] * len(out)
        print('out')
    except:
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

    # заполняем столбцы с формулами
    for k in range(len(worksheet_df_len)):
        worksheet_df['CURRENT PRICE'].iloc[k] = f'=GOOGLEFINANCE(A{k + 2},"price")'
        worksheet_df['WEIGHT PCR sparkline'].iloc[k] = f'=sparkline(sparkline!B{k + 1}:W{k + 1})'
        worksheet_df['% BETA DELTA'].iloc[k] = f'=C{k + 2}/$C$27'

    print(worksheet_df)


    tick = worksheet_df['ETF COMPLEX POSITION'].iloc[i]

    print(f'-----------  {tick} -----------------')

    yahoo_data = yf.download(tick)

    # -----------  PCR -----------------
    limit_date_expiration_min_PCR = datetime.datetime.now().date() - relativedelta(days=30)

    exp_date_list, strike_list = get_avalible_exp_dates(tick, limit_date_expiration_min_PCR)

    side_list = ['P', 'C']

    pcr_df = pd.DataFrame()

    for exp_date, strike_listus in zip(exp_date_list, strike_list):
        print('===============')
        print(strike_listus)
        print(strike_listus[int(len(strike_listus)*0.3):int(len(strike_listus)*0.7)])
        for strike in strike_listus:
            for side in side_list:
                # print('exp_date')
                # print(type(exp_date))
                # print('strike')
                # print(int(strike))
                one_strike_df = get_option_chains(exp_date, strike, side, tick)
                pcr_df = pd.concat([pcr_df, one_strike_df])
                # print(pcr_df)

    pcr_df['weighted'] = pcr_df['CLOSE'] * pcr_df['VOLUME']
    print('pcr2')
    print(pcr_df)
    pcr_df.to_csv('pcr_df_all.csv', index=False)
    # pcr_df['DATE'] = pcr_df.index.tolist()

    NEW_pcr_df = pd.DataFrame()

    for date in pcr_df['DATE'].unique():
        try:
            local_pcr_df = pcr_df[pcr_df['DATE'] == date]
            local_pcr_df = local_pcr_df[local_pcr_df['Strike'] < yahoo_data['Close'][date] * 1.3]
            local_pcr_df = local_pcr_df[local_pcr_df['Strike'] > yahoo_data['Close'][date] * 0.7]
            print('Close')
            print(yahoo_data['Close'][date])
            print('unique')
            print('local_pcr_df')
            print(local_pcr_df)
            NEW_pcr_df = pd.concat([NEW_pcr_df, local_pcr_df])
        except:
            pass

    NEW_pcr_df[NEW_pcr_df['DATE'] == '2023-03-03'].to_excel('2023-03-03.xlsx')
    NEW_pcr_df[NEW_pcr_df['DATE'] == '2023-03-06'].to_excel('2023-03-06.xlsx')
    print(pcr_df[pcr_df['DATE'] == '2022-07-11'].head(40))
    # pcr_df = pcr_df[pcr_df['VOLUME'] >1]
    # pcr_df = pcr_df[pcr_df['CLOSE'] >1]
    NEW_pcr_df['weighted'] = NEW_pcr_df['CLOSE'] * NEW_pcr_df['VOLUME']

    pcr_df_put = NEW_pcr_df[NEW_pcr_df['Side'] == 'P']
    pcr_df_put = pcr_df_put.groupby('DATE').sum()
    pcr_df_put['weighted_put'] = pcr_df_put['weighted']

    pcr_df_call = NEW_pcr_df[NEW_pcr_df['Side'] == 'C']
    pcr_df_call = pcr_df_call.groupby('DATE').sum()
    pcr_df_call['weighted_call'] = pcr_df_call['weighted']

    NEW_pcr_df = pcr_df_call.merge(pcr_df_put, how='right', on=['DATE'])

    NEW_pcr_df['pcr'] = NEW_pcr_df['weighted_put'] / NEW_pcr_df['weighted_call']


    NEW_pcr_df['pcr_SMA_20'] = NEW_pcr_df['pcr'].rolling(window=20).mean()

    pcr_signal = 'UP'
    if NEW_pcr_df['pcr_SMA_20'].iloc[-1] <  NEW_pcr_df['pcr'].iloc[-1]:
        pcr_signal = 'DOWN'

    NEW_pcr_df.to_csv('pcr_df.csv', index=False)

    print('pcr')
    print(NEW_pcr_df)

    worksheet_spark.update(f'A{i+1}', [[tick] + NEW_pcr_df['pcr'].dropna()[-22:].values.tolist()])

    # -------

    sma_20, sma_100, rsi = get_tech_data(yahoo_data)

    worksheet_df['RSI 14'].iloc[i] = rsi
    worksheet_df['CURRENT PRICE'].iloc[i] = f'=GOOGLEFINANCE(A{i+2},"price")'
    worksheet_df['WEIGHT PCR SIGNAL'].iloc[i] = pcr_signal
    worksheet_df['WEIGHT PCR sparkline'].iloc[i] = f'=sparkline(sparkline!B{i+1}:W{i+1})'
    worksheet_df['SMA 20'].iloc[i] = sma_20
    worksheet_df['SMA 100'].iloc[i] = sma_100


    worksheet_df = worksheet_df.fillna(0)
    worksheet_df.to_csv('worksheet_df.csv', index=False)
    worksheet_df = pd.read_csv('worksheet_df.csv')
    worksheet_df = worksheet_df.fillna(0)
    # # ===================================  запись в таблицу ================================================
    worksheet.update('A1', [worksheet_df.columns.values.tolist()] + worksheet_df.values.tolist(), value_input_option='USER_ENTERED' )

client.close_stream()
