import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta


# Define a function to calculate stock momentum
def calculate_stock_momentum(symbol, yahoo_data):
    end_date = datetime.now() - timedelta(days=30)  # Exclude the most recent month
    start_date = end_date - timedelta(days=365)  # Go back 13 months

    # Fetch historical prices
    stock_data = yahoo_data[symbol][start_date:end_date]

    # Compute monthly returns
    df_monthly = stock_data['Adj Close'].resample('M').ffill()
    df_monthly_returns = df_monthly.pct_change()

    # Exclude the last month
    df_monthly_returns = df_monthly_returns[:-1]

    # Calculate average growth rate
    avg_growth_rate = df_monthly_returns.mean()

    # Calculate standard deviation
    sd = df_monthly_returns.std()

    # Calculate momentum
    momentum = avg_growth_rate / sd if sd != 0 else 0

    return momentum