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
from arch import arch_model
pd.options.mode.chained_assignment = None

def get_garch(market_price_df):
    # ========== GARCH volatility calculated ============================================

    try:
        returns_long = np.log(market_price_df[:756] / market_price_df[:756].shift(1))
        returns_long = returns_long.dropna()
        # print(market_price_df[ticker][-252:])
        print('returns_long')
        print(returns_long)
        model_ibov_long = arch_model(returns_long, vol='Garch', p=1, o=0, q=1, dist='Normal', rescale=False)
        res_ibov = model_ibov_long.fit(update_freq=1)

        # =================== 1 =======================
        # Forecast
        forecast_ibov_1 = res_ibov.forecast(horizon=30)
        # Getting Annualized Standard Deviation
        # Garch Vol
        vol_ibov_for_1 = (forecast_ibov_1.variance.iloc[-1] / 10000) ** 0.5 * np.sqrt(252) * 100
        vol_ibov_for_1 = round(vol_ibov_for_1[-1], 3)

    except:
        vol_ibov_for_1 = None

    return vol_ibov_for_1


def calculate_beta(stock_ticker, market_ticker):
    stock_data = stock_ticker.pct_change()[1:]
    market_data = market_ticker["Close"].pct_change()[1:]
    print(stock_data)
    print(market_data)

    covariance = np.cov(stock_data, market_data)[0][1]
    var = np.var(market_data)

    beta = covariance / var
    return beta


def run_beta(stock_yahoo):
    start_date = datetime.datetime.now().date()
    spy_yahoo = yf.download("^SPX")

    limit_date = start_date - relativedelta(years=+3)
    limit_date = limit_date.strftime("%Y-%m-%d")

    # try:
    beta = calculate_beta(stock_yahoo[limit_date:], spy_yahoo[limit_date:])
    # except:
    #     beta = np.nan

    return beta


def get_hv(yahoo_data):
    # Compute the logarithmic returns using the Closing price
    log_returns = np.log(yahoo_data.dropna() / yahoo_data.dropna().shift(1))
    # Compute Volatility using the pandas rolling standard deviation function
    hv_20 = log_returns.rolling(window=20).std() * np.sqrt(252)
    hv_50 = log_returns.rolling(window=50).std() * np.sqrt(252)
    hv_100 = log_returns.rolling(window=100).std() * np.sqrt(252)
    return hv_20[-1], hv_50[-1], hv_100[-1]

def estimated_vol(df_data, tick):
    # calculate realized volatility
    intraday_vol = np.log(df_data['High'][tick].shift(-1) / df_data['Open'][tick].shift(-1)) * np.log(
        df_data['High'][tick].shift(-1) / df_data['Close'][tick].shift(-1)) + \
                   np.log(df_data['Open'][tick].shift(-1) / df_data['Open'][tick].shift(-1)) * \
                   np.log(df_data['Low'][tick].shift(-1) / df_data['Close'][tick].shift(-1))
    intraday_vol = (np.sqrt(intraday_vol) * 100 * 16) ** 2
    overnight_vol = (np.abs(np.log(df_data['Open'][tick] / df_data['Close'][tick])) * 100 * 16) ** 2
    realized_vol = np.sqrt(intraday_vol + overnight_vol)
    # calculate estimates for short medium and long term realized vol
    short_term_vol = np.sqrt(np.mean(realized_vol[-5:] ** 2))
    med_term_vol = np.sqrt(np.mean(realized_vol[-20:] ** 2))
    long_term_vol = np.sqrt(np.mean(realized_vol ** 2))
    # aggregate it into a single estimate
    estimate_vol = 0.6 * short_term_vol + 0.3 * med_term_vol + 0.1 * long_term_vol

    return estimate_vol

def hist_median_move(tick):
    group_data = []
    index_data = []
    last_step = 0
    nex_step = 0
    stat_data = yf.download(tick)
    stat_data_close = stat_data['Close']
    time_frame_stats = 22

    for step in range(len(stat_data_close) // time_frame_stats):
        nex_step = last_step + time_frame_stats

        period_values = (stat_data['Close'][last_step: nex_step][-1] - stat_data['Open'][last_step: nex_step][0]) / \
                        stat_data['Open'][last_step: nex_step][0]


        group_data.append(period_values * 100)
        index_data.append(stat_data[last_step: nex_step].index.tolist()[-1])
        last_step = nex_step

    # print(group_data)
    # print(len(group_data))

    group_df = pd.DataFrame({'Data': group_data})
    return group_df.median().values[0], group_df.std().values[0]



if __name__ == "__main__":
    tables = ['SP00_SECTORS']

    for table_name in tables:
        # # ================ раббота с таблицей============================================
        gc = gd.service_account(filename="Seetus.json")
        worksheet = gc.open("IBKR").worksheet(table_name)
        worksheet_df = pd.DataFrame(worksheet.get_all_values()).replace("", np.nan)
        print(f"==========  {table_name}  ===========")

        worksheet_df_FORMULA = pd.DataFrame(
            worksheet.get_all_values(value_render_option="FORMULA")
        ).replace("", np.nan)
        # print(worksheet_df_FORMULA)

        num_total = worksheet_df_FORMULA[0][worksheet_df_FORMULA[0] == "next"].index
        worksheet_df_FORMULA_sum = pd.DataFrame()

        if table_name == "SP00_SECTORS":
            company_list = worksheet_df_FORMULA[0][1:].values.tolist()
            yahoo_data_native = yf.download(company_list + ['^SPX'])
            yahoo_data = yahoo_data_native['Close'][-132:]
            for num, next_num in worksheet_df_FORMULA[1:].iterrows():
                tick = next_num[0]
                print(num)
                print(next_num)
                print('tick', tick)
                current_price = yahoo_data[tick].dropna().iloc[-1]
                print('current_price', current_price)
                current_corr = yahoo_data.corr()['^SPX'][tick]

                hv_20, hv_50, hv_100 = get_hv(yahoo_data_native['Close'][tick])

                # skewness = yahoo_data_native['Close'][-2440:][tick].skew()
                # kurtosis = yahoo_data_native['Close'][-2440:][tick].kurtosis()
                beta = run_beta(yahoo_data_native['Close'][tick])
                es_volatility = estimated_vol(yahoo_data_native, tick)
                print('es_volatility', es_volatility)


                median_move, median_move_std = hist_median_move(tick)
                print('median_move', median_move)
                print('median_move_std', median_move_std)

                garch = get_garch(yahoo_data_native['Close'][-2440:][tick])
                print('garch', garch)


                worksheet_df_FORMULA.iloc[num, 5] = round(hv_20, 3)
                worksheet_df_FORMULA.iloc[num, 6] = round(hv_50, 3)
                worksheet_df_FORMULA.iloc[num, 7] = round(hv_100, 3)
                worksheet_df_FORMULA.iloc[num, 9] = round(es_volatility/100, 3)
                worksheet_df_FORMULA.iloc[num, 2] = round(current_corr, 3)#
                worksheet_df_FORMULA.iloc[num, 3] = round(beta, 3)#
                worksheet_df_FORMULA.iloc[num, 10] = garch
                worksheet_df_FORMULA.iloc[num, 15] = median_move
                worksheet_df_FORMULA.iloc[num, 16] = median_move_std
                # worksheet_df_FORMULA.iloc[num, 9] = round(skewness, 3)
                # worksheet_df_FORMULA.iloc[num, 10] = round(kurtosis, 3)
                # print(solo_company_data)

            print(worksheet_df_FORMULA[[3, 4]])
            # print(yahoo_data['MBT=F'])

            #
            worksheet_df_FORMULA = worksheet_df_FORMULA.fillna("'")
            # # # ===================================  запись в таблицу ================================================
            worksheet.update(
                "A1",
                # [worksheet_df_FORMULA_sum.columns.values.tolist()]
                # +
                worksheet_df_FORMULA.values.tolist(),
                value_input_option="USER_ENTERED",
            )
