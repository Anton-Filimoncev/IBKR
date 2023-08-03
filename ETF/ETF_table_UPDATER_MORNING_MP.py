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
import requests
from dateutil.relativedelta import relativedelta
from thetadata import ThetaClient, OptionReqType, OptionRight, DateRange, SecType, StockReqType



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


def max_pain_contracts(ticker):
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

max_pain_contracts('GLD')


