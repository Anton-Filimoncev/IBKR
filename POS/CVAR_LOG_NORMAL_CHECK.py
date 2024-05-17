import pandas as pd
import numpy as np
import scipy.stats as stats
import datetime
import time
from dateutil.relativedelta import relativedelta
import yfinance as yf
import os
import gspread as gd
import mibian
import math
from popoption.ShortPut import shortPut
from popoption.ShortCall import shortCall
from popoption.ShortStrangle import shortStrangle
from popoption.PutCalendar import putCalendar
from popoption.CallCalendar import callCalendar
from popoption.PutRatio import putRatio

pd.options.mode.chained_assignment = None


def get_proba_putRatio(current_price, yahoo_data, put_long_strike, put_short_strike1, put_short_strike2, total_prime,
                                          sigma_short1, sigma_short2, sigma_long, days_to_expiration):
    rate = 4.6
    closing_days_array = [days_to_expiration]
    percentage_array = [50]
    trials = 3000

    proba_50 = putRatio(
        current_price,
        sigma_long,
        sigma_short1,
        sigma_short2,
        rate,
        trials,
        days_to_expiration,
        closing_days_array,
        percentage_array,
        put_long_strike,
        put_short_strike1,
        put_short_strike2,
        total_prime,
        yahoo_data,
    )
    print(proba_50)
    return proba_50




def get_proba_50_put(
    current_price, yahoo_data, short_strike, short_price, sigma, days_to_expiration
):
    rate = 4.6
    closing_days_array = [days_to_expiration]
    percentage_array = [50]
    trials = 3000

    proba_50 = shortPut(
        current_price,
        sigma,
        rate,
        trials,
        days_to_expiration,
        closing_days_array,
        percentage_array,
        short_strike,
        short_price,
        yahoo_data,
    )

    return proba_50


def get_proba_50_call(
    current_price, yahoo_data, short_strike, short_price, sigma, days_to_expiration
):
    rate = 4.6
    days_to_expiration = days_to_expiration
    closing_days_array = [days_to_expiration]
    percentage_array = [50]
    trials = 3000
    proba_50 = shortCall(
        current_price,
        sigma,
        rate,
        trials,
        days_to_expiration,
        closing_days_array,
        percentage_array,
        short_strike,
        short_price,
        yahoo_data,
    )

    proba_100 = shortCall(
        current_price,
        sigma,
        rate,
        trials,
        days_to_expiration,
        closing_days_array,
        [100],
        short_strike,
        short_price,
        yahoo_data,
    )

    prob_100 = proba_100[0]

    prob_50 = proba_50[0]
    expected_profit = proba_50[1]
    avg_dtc = proba_50[2]
    cvar = proba_50[3]

    return prob_50, expected_profit, avg_dtc, prob_100, cvar


def get_proba_50_strangle(
    current_price,
    yahoo_data,
    call_short_strike,
    put_short_strike,
    call_short_price,
    put_short_price,
    sigma,
    days_to_expiration,
):
    rate = 4.6
    closing_days_array = [days_to_expiration]
    percentage_array = [50]
    trials = 3000
    proba_50 = shortStrangle(
        current_price,
        sigma,
        rate,
        trials,
        days_to_expiration,
        closing_days_array,
        percentage_array,
        call_short_strike,
        call_short_price,
        put_short_strike,
        put_short_price,
        yahoo_data,
    )

    proba_100 = shortStrangle(
        current_price,
        sigma,
        rate,
        trials,
        days_to_expiration,
        closing_days_array,
        [100],
        call_short_strike,
        call_short_price,
        put_short_strike,
        put_short_price,
        yahoo_data,
    )

    prob_100 = proba_100[0]
    prob_50 = proba_50[0]
    expected_profit = proba_50[1]
    avg_dtc = proba_50[2]
    cvar = proba_50[3]

    return prob_50, expected_profit, avg_dtc, prob_100, cvar

def get_abs_return(price_array, type_option, days_to_exp, days_to_exp_short, history_vol, current_price, strike, prime, vol_opt, side):
    put_price_list = []
    call_price_list = []
    proba_list = []
    price_gen_list = []

    for stock_price_num in range(len(price_array)):
        try:
            P_below = stats.norm.cdf(
                (np.log(price_array[stock_price_num] / current_price) / (
                        history_vol * math.sqrt(days_to_exp_short / 365))))
            P_current = stats.norm.cdf(
                (np.log(price_array[stock_price_num + 1] / current_price) / (
                        history_vol * math.sqrt(days_to_exp_short / 365))))
            proba_list.append(P_current - P_below)
            if type_option == 'Short':
                c = mibian.BS([price_array[stock_price_num + 1], strike, 4, 1], volatility=vol_opt * 100)
            if type_option == 'Long':
                c = mibian.BS([price_array[stock_price_num + 1], strike, 4, days_to_exp], volatility=vol_opt * 100)

            put_price_list.append(c.putPrice)
            call_price_list.append(c.callPrice)
            price_gen_list.append(price_array[stock_price_num + 1])
        except:
            pass

    gen_df = pd.DataFrame({
        'gen_price': price_gen_list,
        'put_price': put_price_list,
        'call_price': call_price_list,
        'proba': proba_list,
    })

    gen_df['return'] = (gen_df['put_price'] - prime)

    if side =='P':
        if type_option == 'Short':
            return ((prime - gen_df['put_price']) * gen_df['proba']).sum(), ((prime - gen_df['put_price']) * gen_df['proba']).sort_values()[:int(len(gen_df)*0.05)].mean()

        if type_option == 'Long':
            return ((gen_df['put_price'] - prime) * gen_df['proba']).sum(), ((gen_df['put_price'] - prime) * gen_df['proba']).sort_values()[:int(len(gen_df)*0.05)].mean()

    if side == 'C':
        if type_option == 'Short':
            return ((prime - gen_df['call_price']) * gen_df['proba']).sum(), ((prime - gen_df['call_price']) * gen_df['proba']).sort_values()[:int(len(gen_df)*0.05)].mean()

        if type_option == 'Long':
            return ((gen_df['call_price'] - prime) * gen_df['proba']).sum(), ((gen_df['call_price'] - prime) * gen_df['proba']).sort_values()[:int(len(gen_df)*0.05)].mean()

def expected_return_calc(vol_short, vol_long, current_price, history_vol, days_to_exp_short, days_to_exp_long, strike_long, strike_short, prime_long, prime_short, side):

    # print('expected_return CALCULATION ...')

    price_array = np.arange(current_price - current_price / 2, current_price + current_price, 0.2)

    short_finish, cvar_df_short = get_abs_return(price_array, 'Short', days_to_exp_short, days_to_exp_short, history_vol, current_price, strike_short,
                                prime_short,
                                vol_short, side)

    long_finish, cvar_df_long = get_abs_return(price_array, 'Long', days_to_exp_long, days_to_exp_short, history_vol, current_price, strike_long,
                                 prime_long,
                                 vol_long, side)

    expected_return = (short_finish + long_finish) * 100
    cvar_df = (cvar_df_short + cvar_df_long) * 100

    return expected_return, cvar_df

def get_proba_50_calendar(current_price, yahoo_data, long_strike, long_price, short_strike, short_price,
                          sigma_short, sigma_long, days_to_expiration_short, days_to_expiration_long, side, short_count, long_count):
    rate = 4.6
    closing_days_array = [days_to_expiration_short]
    percentage_array = [10]
    if short_count > long_count:
        percentage_array = [3]
    trials = 3000

    if side == 'P':
        response = putCalendar(current_price, sigma_short, sigma_long, rate, trials, days_to_expiration_short,
                    days_to_expiration_long, closing_days_array, percentage_array, long_strike,
                    long_price, short_strike, short_price, yahoo_data, short_count, long_count)
    else:
        response = callCalendar(current_price, sigma_short, sigma_long, rate, trials, days_to_expiration_short,
                    days_to_expiration_long, closing_days_array, percentage_array, long_strike,
                    long_price, short_strike, short_price, yahoo_data, short_count, long_count)

    print(response)
    return response['pop'][0], response['cvar']*100, response['exp_return']*100



if __name__ == "__main__":
    ticker = 'XLK'
    # solo_company_data.iloc[2, 3] = "" # заполнить поле
    yahoo_data = yf.download(ticker)
    print(yahoo_data)
    # Compute the logarithmic returns using the Closing price
    log_returns = np.log(yahoo_data['Close'] / yahoo_data['Close'].shift(1))
    # Compute Volatility using the pandas rolling standard deviation function
    hv = log_returns.rolling(window=252).std() * np.sqrt(252)
    hv = hv[-1]

    current_price = yahoo_data["Close"].iloc[-1]

    sigma_short = 16.2
    sigma_long = 18.4
    days_to_expiration_short = 24
    days_to_expiration_long = 87
    days_to_expiration_long_return = days_to_expiration_long-days_to_expiration_short
    put_long_strike = 220
    put_short_strike = 220
    put_long_price = 5.1
    put_short_price = 1.26

    print("current_price", current_price)
    print("put_long_strike", put_long_strike)
    print("put_short_strike", put_short_strike)
    print("put_long_price", put_long_price)
    print("put_long_price", put_long_price)
    print("put_short_price", put_short_price)
    print("sigma_short", sigma_short)
    print("sigma_long", sigma_long)
    print("hv", hv)
    print("days_to_expiration_short", days_to_expiration_short)
    print("days_to_expiration_long", days_to_expiration_long)
    print("days_to_expiration_long_return", days_to_expiration_long_return)

    # print("proba_30", proba_50)
    expected_return, cvar_df = expected_return_calc(sigma_short/100, sigma_long/100, current_price, hv, days_to_expiration_short,
                               days_to_expiration_long_return, put_long_strike, put_short_strike, put_long_price,
                               put_short_price, 'C')
    print(cvar_df)
    # print("cvar_df", cvar_.df.sort_values()[:int(len(cvar_df)*0.05)].mean())
    print("expected_return", expected_return)
