import pandas as pd
import numpy as np
import datetime as dt
from scipy.signal import argrelextrema
import datetime
import requests
import yfinance as yf
import plotly.express as px
import matplotlib.pyplot as plt
from dateutil.relativedelta import relativedelta
import seaborn as sns
import time
import mibian
from multiprocessing import Pool
from scipy.stats import norm
import math


def implied_volatility(row):

    P = row['BID']
    S = row['Close']
    E = row['Strike']
    T = row['days_to_exp']/365
    r = 0.002
    contract_type = row['Side']

    sigma = 0.01


    while sigma < 1:
        try:
            d_1 = float(float((math.log(S/E)+(r+(sigma**2)/2)*T))/float((sigma*(math.sqrt(T)))))
            d_2 = float(float((math.log(S/E)+(r-(sigma**2)/2)*T))/float((sigma*(math.sqrt(T)))))

            if contract_type == 'C':
                P_implied = float(S*norm.cdf(d_1) - E*math.exp(-r*T)*norm.cdf(d_2))

            if contract_type == 'P':
                P_implied = float(norm.cdf(-d_2)*E*math.exp(-r*T) - norm.cdf(-d_1)*S)

            if P-(P_implied) < 0.001:
                return sigma * 100


            sigma +=0.001
        except:
            return 0

    return 0

# #

def useBS_delta(row):
    underlyingPrice = row['Close']
    strikePrice = row['Strike']
    interestRate = 0.2
    dayss = row['days_to_exp']

    contract_type = row['Side']
    optPrice = row['BID']

    volatility = row['IV']
    try:
        if contract_type == 'P':
            delta = mibian.BS([underlyingPrice, strikePrice, 1.5, dayss], volatility=volatility)
            delta_res = delta.putDelta

        if contract_type == 'C':
            delta = mibian.BS([underlyingPrice, strikePrice, 1.5, dayss], volatility=volatility)
            delta_res = delta.callDelta
    except:
        delta_res = 0

    return delta_res
#

if __name__ == '__main__':
    start = time.time()  ## точка отсчета времени
    market_price_df = yf.download('EW')
    # market_price_df['Date'] = market_price_df.index.tolist()
    chains = pd.read_csv('full_df_EWZ.csv')
    chains = chains.dropna().reset_index(drop=True)
    chains['DATE'] = pd.to_datetime(chains['DATE'])
    print(chains)
    print(chains.columns.tolist())
    # chains = chains[:1000]

    chains = chains.merge(market_price_df, how='left', left_on=['DATE'], right_on=['Date'])

    print(chains.columns.tolist())

    with Pool(7) as p:
        iv = p.map(implied_volatility, [chains.iloc[i] for i in range(len(chains))])

    chains['IV'] = iv
    print(chains['IV'])

    with Pool(7) as p:
        delta = p.map(useBS_delta, [chains.iloc[i] for i in range(len(chains))])
        print(delta)

    chains['Delta'] = delta
    print(chains['IV'])
    print(chains['Delta'])
    end = time.time() - start  ## собственно время работы программы
    print(end) ## вывод времени
    print(chains)

    chains.to_csv('full_df_EWZ_GREEK.csv', index=False)