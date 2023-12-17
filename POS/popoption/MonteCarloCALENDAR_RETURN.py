import numpy as np
import pandas as pd
from numba import jit
import math

# Assumptions:
# The stock price volatility is equal to the implied volatility and remains constant.
# Geometric Brownian Motion is used to model the stock price.
# Risk-free interest rates remain constant.
# The Black-Scholes Model is used to price options contracts.
# Dividend yield is not considered.
# Commissions are not considered.
# Assignment risks are not considered.
# Earnings date and stock splits are not considered.


def monteCarlo_return(underlying, rate, sigma_short, sigma_long, days_to_expiration_short, days_to_expiration_long, closing_days_array, trials, initial_credit,
                   min_profit, strikes, bsm_func, yahoo_stock):

    log_returns = np.log(1 + yahoo_stock['Close'].pct_change())
    # Define the variables
    u = log_returns.mean()
    var = log_returns.var()

    # Calculate drift and standard deviation
    drift = u - (0.5 * var)

    # Compute the logarithmic returns using the Closing price
    log_returns = np.log(yahoo_stock['Close'] / yahoo_stock['Close'].shift(1))
    print(log_returns)
    # Compute Volatility using the pandas rolling standard deviation function
    volatility = log_returns.rolling(window=252).std() * np.sqrt(252)
    volatility = volatility[-1]

    dt = 1 / 365  # 365 calendar days in a year

    length = len(closing_days_array)
    max_closing_days = max(closing_days_array)

    sigma_short, sigma_long = sigma_short / 100, sigma_long / 100
    rate = rate / 100

    counter1 = [0] * length
    dtc = [0] * length
    dtc_history = np.zeros((length, trials))

    indices = [0] * length

    profit_last_day_short = []

    for c in range(trials):

        epsilon_cum = 0
        t_cum = 0

        for i in range(length):
            indices[i] = 0

        # +1 added to account for first day. sim_prices[0,...] = underlying price.
        for r in range(max_closing_days + 1):
            # Brownian Motion

            W = (dt ** (1 / 2)) * epsilon_cum

            # Geometric Brownian Motion
            # signal = (rate - 0.5 * (sigma ** 2)) * t_cum
            signal = drift - 0.5 * (volatility ** 2) * t_cum
            # noise = sigma * W

            noise = volatility * W
            y = noise + signal
            stock_price = underlying * np.exp(y)  # Stock price on current day

            epsilon = np.random.randn()
            epsilon_cum += epsilon
            t_cum += dt

            # Prevents crashes
            if stock_price <= 0:
                stock_price = 0.001

            time_fraction_short = dt * (days_to_expiration_short - r)
            time_fraction_long = dt * (days_to_expiration_long - r)



            debit = bsm_func(stock_price, strikes, rate, time_fraction_short, time_fraction_long, sigma_short, sigma_long)

            profit = debit + initial_credit  # Profit if we were to close on current day

            if r == max_closing_days-1:
                # print('days_to_expiration_short', days_to_expiration_short)
                # print('r', r)
                profit_last_day_short.append(profit)

    expected_profit = np.mean(profit_last_day_short)

    return expected_profit
