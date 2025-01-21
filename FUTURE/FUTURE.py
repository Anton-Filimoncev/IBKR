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
import pandas_ta as pta

pd.options.mode.chained_assignment = None
import warnings
from hurst import compute_Hc
from scipy.signal import argrelextrema
from scipy.stats import pearsonr

warnings.filterwarnings("ignore")


def calcBollinger(data, size, std_type, ma_type):
    df = data.copy()
    if ma_type == 'SMA':
        df["ma"] = df['Close'].rolling(size).mean()

    if ma_type == 'EMA':
        df["ma"] = df['Close'].ewm(com=0.8).mean()

    if std_type == 'Close':
        df["bolu_3"] = df["ma"] + 3 * df['Close'].rolling(size).std(ddof=0)
        df["bolu_4"] = df["ma"] + 4 * df['Close'].rolling(size).std(ddof=0)
        df["bold_3"] = df["ma"] - 3 * df['Close'].rolling(size).std(ddof=0)
        df["bold_4"] = df["ma"] - 4 * df['Close'].rolling(size).std(ddof=0)

    if std_type == 'Close-Open':
        df["bolu_3"] = df["ma"] + 3 * (df['Close'] - df['Open']).rolling(size).std(ddof=0)
        df["bolu_4"] = df["ma"] + 4 * (df['Close'] - df['Open']).rolling(size).std(ddof=0)
        df["bold_3"] = df["ma"] - 3 * (df['Close'] - df['Open']).rolling(size).std(ddof=0)
        df["bold_4"] = df["ma"] - 4 * (df['Close'] - df['Open']).rolling(size).std(ddof=0)

    df.dropna(inplace=True)
    return df


def bollinger(yahoo_df, std_type, sma_type, numYearBoll, windowSizeBoll):
    startBoll = (datetime.datetime.today() - datetime.timedelta(numYearBoll * 365)).date().strftime("%Y-%m-%d")
    # endBoll = datetime.datetime.today()
    dataBoll = yahoo_df[startBoll:]

    df_boll = calcBollinger(dataBoll, windowSizeBoll, std_type, sma_type)
    df_boll = df_boll.reset_index()

    # добавление точек экстремума
    max_idx = argrelextrema(np.array(df_boll['Close'].values), np.greater, order=3)
    min_idx = argrelextrema(np.array(df_boll['Close'].values), np.less, order=3)
    df_boll['peaks'] = np.nan
    df_boll['lows'] = np.nan
    for i in max_idx:
        df_boll['peaks'][i] = df_boll['Close'][i]
    for i in min_idx:
        df_boll['lows'][i] = df_boll['Close'][i]

    return df_boll


def bolinger_indecator(yahoo_df, std_type, sma_type, numYearBoll, windowSizeBoll):
    df_boll = bollinger(yahoo_df, std_type, sma_type, numYearBoll, windowSizeBoll)

    val_3 = (df_boll['Close'].iloc[-1] - df_boll['bold_3'].iloc[-1]) / (
                df_boll['bolu_3'].iloc[-1] - df_boll['bold_3'].iloc[-1]) * 100
    val_4 = (df_boll['Close'].iloc[-1] - df_boll['bold_4'].iloc[-1]) / (
                df_boll['bolu_4'].iloc[-1] - df_boll['bold_4'].iloc[-1]) * 100

    val = str(round(val_3, 2)) + '_' + str(round(val_4, 2))
    return val


def williams_indicator(df):
    highest_high = df['High'][-10:].max()
    lowest_low = df['Low'][-10:].min()
    close = df['Close'].iloc[-1]
    williams = (highest_high - close) / (highest_high - lowest_low) * -100
    return williams


def trend(price_df):
    trend = ""
    current_price = price_df["Close"].iloc[-1]
    SMA_20 = price_df["Close"].rolling(window=20).mean().iloc[-1]
    SMA_100 = price_df["Close"].rolling(window=100).mean().iloc[-1]

    if current_price > SMA_100 and current_price > SMA_20 and SMA_20 > SMA_100:
        trend = "Strong Uptrend"
    if current_price > SMA_100 and current_price > SMA_20 and SMA_20 < SMA_100:
        trend = "Uptrend"
    if current_price > SMA_100 and current_price < SMA_20 and SMA_20:
        trend = "Weak Uptrend"
    if current_price < SMA_100 and current_price < SMA_20 and SMA_20 < SMA_100:
        trend = "Strong Downtrend"
    if current_price < SMA_100 and current_price < SMA_20 and SMA_20 > SMA_100:
        trend = "Downtrend"
    if current_price < SMA_100 and current_price > SMA_20:
        trend = "Weak downtrend"

    return trend


def get_tech_data(df):
    df["RSI"] = pta.rsi(df["Close"])
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_100"] = df["Close"].rolling(window=100).mean()

    sma_20 = df["SMA_20"].dropna().iloc[-1]
    sma_100 = df["SMA_100"].dropna().iloc[-1]
    rsi = df["RSI"].dropna().iloc[-1]

    return sma_20, sma_100, rsi


def get_garch(market_price_df):
    # ========== GARCH volatility calculated ============================================

    try:
        returns_long = np.log(market_price_df[756:] / market_price_df[756:].shift(1))
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
    cov_data = stock_data.to_frame('stock').merge(market_data.to_frame('mark'), on='Date').dropna()
    print('cov_data')
    print(cov_data)

    covariance = np.cov(cov_data['stock'], cov_data['mark'])[0][1]
    var = np.var(market_data)

    beta = covariance / var
    return beta


def run_beta(stock_yahoo, ticker):
    start_date = datetime.datetime.now().date()
    spy_yahoo = yf.download(ticker)
    limit_date = start_date - relativedelta(years=+3)
    limit_date = limit_date.strftime("%Y-%m-%d")

    # try:
    beta = calculate_beta(stock_yahoo[limit_date:], spy_yahoo[limit_date:])
    # except:
    #     beta = np.nan

    return beta


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


def season_pos(df_data):
    # Убедимся, что индекс типа datetime
    if not isinstance(df_data.index, pd.DatetimeIndex):
        raise ValueError("Индекс датафрейма должен быть типа DatetimeIndex.")

    # Определяем текущий месяц и год
    now = datetime.datetime.now()
    target_month = now.month
    current_year = now.year

    # Фильтруем данные за последние 4 года для текущего месяца
    start_year = current_year - 4
    relevant_data = df_data[(df_data.index.year >= start_year) & (df_data.index.month == target_month)]

    # Проверяем, есть ли данные за указанный период
    if relevant_data.empty:
        return None

    # Группируем данные по году
    returns = []
    for year in relevant_data.index.year.unique():
        yearly_data = relevant_data[relevant_data.index.year == year]
        if len(yearly_data) > 1:
            first_close = yearly_data['Close'].iloc[0]
            last_close = yearly_data['Close'].iloc[-1]
            yearly_return = (last_close - first_close) / first_close
            returns.append(yearly_return)

    # Рассчитываем среднюю доходность
    if not returns:
        return None

    average_return = sum(returns) / len(returns)

    return average_return

def hurst_coef(df):
    # Задаем диапазон дат в котором нужно собирать все данные по тикерам
    # start = dt.datetime(2010, 1, 1)
    # end = dt.datetime.now()  # сегодняшняя дата, чтобы не менять вручную.
    # # Получаем данные из Yahoo. Именно этот способ позволяет получить данные с тикерами в столбцах.
    # df = web.get_data_yahoo(ticker, start, end)
    try:
        start_size = datetime.datetime.today() - datetime.timedelta(days=150)
        # print('start_size', start_size)
        start_size_str = str(start_size).split(' ')[0]
        date_hurts = df.dropna().loc[start_size_str:]['Close']

        if compute_Hc(date_hurts, kind='price')[0] == 0.5:
            return 'Random walk price'
        elif compute_Hc(date_hurts, kind='price')[0] > 0.5:
            return 'Trendiness'
        elif compute_Hc(date_hurts, kind='price')[0] < 0.5:
            return 'Return to mean'

    except:
        start_size = datetime.datetime.today() - datetime.timedelta(days=160)
        print('start_size', start_size)
        start_size_str = str(start_size).split(' ')[0]
        date_hurts = df.dropna().loc[start_size_str:]['Close']
        print(date_hurts)

        if compute_Hc(date_hurts, kind='price')[0] == 0.5:
            return 'Random walk price'
        elif compute_Hc(date_hurts, kind='price')[0] > 0.5:
            return 'Trendiness'
        elif compute_Hc(date_hurts, kind='price')[0] < 0.5:
            return 'Return to mean'

    # 'Hurst Coefficient %.2f' % compute_Hc(date_hurts, kind='price')[0]


def drift_calc(yahoo_stock):
    log_returns = np.log(1 + yahoo_stock['Close'].pct_change())
    # Define the variables
    u = log_returns.mean()
    var = log_returns.var()
    # Calculate drift and standard deviation
    drift = u - (0.5 * var)
    return drift


def get_relative_price(price_yahoo):
    min_val = price_yahoo.min()
    max_val = price_yahoo.max()
    cur_val = price_yahoo[-1]
    mid_val = price_yahoo.mean()

    rel_price_val = ''
    # Расчет процента
    rel_price = ((cur_val - min_val) / (max_val - min_val)) * 100

    if cur_val > mid_val:
        rel_price_val += str(round(rel_price, 1)) + ' expensive'
    else:
        rel_price_val += str(round(rel_price, 1)) + ' cheap'

    return rel_price_val


def get_cot(barchart_df, product):
    try:
        print('product', product.lower())
        print(barchart_df.loc[product.lower()].iloc[2])
        data = barchart_df.loc[product.lower()]

        min_val = float(data['52W Low'].replace(',', '.'))
        max_val = float(data['52W High'].replace(',', '.'))
        cur_val = float(data.iloc[2].replace(',', '.'))
        print('cur_val', cur_val)
        mid_val = (max_val + min_val) / 2

        rel_price_val = ''
        # Расчет процента
        rel_price = ((cur_val - min_val) / (max_val - min_val)) * 100

        if cur_val > mid_val:
            rel_price_val += str(round(rel_price, 1)) + ' overbought'
        else:
            rel_price_val += str(round(rel_price, 1)) + ' oversold'

        return rel_price_val
    except Exception as err:
        print(err)
        return np.nan


def calc_corr(df, lookback, hold):
    # Create a copy of the dataframe
    data = df.copy()

    # Calculate lookback returns
    data['lookback_returns'] = data['Close'].pct_change(lookback)

    # Calculate hold returns
    data['future_hold_period_returns'] = data['Close'].pct_change(hold).shift(-hold)

    data = data.dropna()
    data = data.iloc[::hold]

    # Calculate correlation coefficient and p-value
    corr, p_value = pearsonr(data.lookback_returns,
                             data.future_hold_period_returns)
    return corr, p_value


# Define a function to calculate stock momentum
def calculate_stock_momentum(yahoo_data):
    crude_data = yahoo_data

    # Define lookback periods
    lookback = [15, 30, 60, 90, 150, 240, 360]

    # Define holding periods
    hold = [5, 10, 15, 30, 45, 60]

    # Create a dataframe which stores price of a security
    crude_data.dropna()

    # Create an array of length lookback*hold
    corr_grid = np.zeros((len(lookback), len(hold)))
    p_value_grid = np.zeros((len(lookback), len(hold)))

    # Run through a length of lookback and holding periods
    for i in range(len(lookback)):
        for j in range(len(hold)):
            # Call calc_corr function and calculate correlation coefficient and p-value
            corr_grid[i][j], p_value_grid[i][j] = calc_corr(
                crude_data, lookback[i], hold[j])

    opt = np.where(corr_grid == np.max(corr_grid))
    opt_lookback = lookback[opt[0][0]]

    hurst_val = compute_Hc(crude_data['Close'][-222:].dropna(), kind='price', simplified=False)[0]

    opt_hold = hold[opt[1][0]]
    # end_date = datetime.now() - timedelta(days=30)  # Exclude the most recent month
    start_date = datetime.datetime.now() - datetime.timedelta(days=opt_lookback)  # Go back

    # Fetch historical prices
    stock_data = yahoo_data[start_date:]

    # Compute monthly returns
    df_monthly = stock_data['Adj Close'].ffill()
    df_monthly_returns = df_monthly.pct_change()
    # Exclude the last month
    df_monthly_returns = df_monthly_returns[:-1]

    # Calculate average growth rate
    avg_growth_rate = df_monthly_returns.mean()

    # Calculate standard deviation
    sd = df_monthly_returns.std()

    # Calculate momentum
    momentum = avg_growth_rate / sd if sd != 0 else 0

    return momentum, opt_hold, hurst_val, opt_lookback


def wwma(values, n):
    """
     J. Welles Wilder's EMA
    """
    return values.ewm(alpha=1 / n, adjust=False).mean()


def atr(high, low, close, n):
    data = pd.DataFrame([])
    data['tr0'] = abs(high - low)
    data['tr1'] = abs(high - close.shift())
    data['tr2'] = abs(low - close.shift())
    tr = data[['tr0', 'tr1', 'tr2']].max(axis=1)
    atr = wwma(tr, n)

    return atr


def long_term_component(data):
    # если 60 > 275 - bull, 60<275 - bear
    data = data.dropna()
    print('data')
    print(data)
    val = 'bull'
    break_val = data["Close"][-254:].max()
    breakpoint_date = data[data["Close"] == break_val].index.tolist()[-1]
    breakpoint_val = data[data["Close"] == break_val]["Close"].values.tolist()[-1]

    data["SMA_60"] = data["Close"].rolling(window=60).mean()
    data["SMA_275"] = data["Close"].rolling(window=275).mean()
    if data["SMA_60"].iloc[-1] < data["SMA_275"].iloc[-1]:
        val = 'bear'
        break_val = data["Close"][-254:].min()
        breakpoint_date = data[data["Close"] == break_val].index.tolist()[-1]
        breakpoint_val = data[data["Close"] == break_val]["Close"].values.tolist()[-1]

    return val, str(breakpoint_date).split(' ')[0], str(round(breakpoint_val, 2))


def calc_emacd(data):
    df = data.copy()

    # Вычисление EMA, MACD и сигнальной линии
    df['ema12'] = df['Close'].ewm(span=12, min_periods=12).mean()
    df['ema26'] = df['Close'].ewm(span=26, min_periods=26).mean()
    df['macd'] = df['ema12'] - df['ema26']
    df['signal'] = df['macd'].ewm(span=9, min_periods=9).mean()
    df['diff'] = df['macd'] - df['signal']

    # Определение пересечений MACD и сигнальной линии
    df['cross_signal'] = (df['diff'] * df['diff'].shift(1) < 0)
    df['direction_signal'] = df['diff'] > 0  # True, если MACD > Signal

    # Отбор пересечений MACD и сигнальной линии
    crossings_signal = df[df['cross_signal']].copy()
    crossings_signal['type_signal'] = crossings_signal['direction_signal'].apply(lambda x: 'bull' if x else 'bear')
    last_cross_signal = crossings_signal.iloc[-1] if not crossings_signal.empty else None

    # Определение пересечений MACD с нулевой линией
    df['cross_zero'] = (df['macd'] * df['macd'].shift(1) < 0)
    df['direction_zero'] = df['macd'] > 0  # True, если MACD > 0

    # Отбор пересечений MACD с нулевой линией
    crossings_zero = df[df['cross_zero']].copy()
    crossings_zero['type_zero'] = crossings_zero['direction_zero'].apply(lambda x: 'bull' if x else 'bear')
    last_cross_zero = crossings_zero.iloc[-1] if not crossings_zero.empty else None

    # Результаты последнего пересечения
    if last_cross_signal is not None:
        print(f"Дата последнего пересечения MACD и signal: {last_cross_signal.name.date()}")
        print(f"Тип пересечения: {last_cross_signal['type_signal']}")
    else:
        print("Пересечений MACD и signal не найдено.")

    if last_cross_zero is not None:
        print(f"Дата последнего пересечения MACD и 0: {last_cross_zero.name.date()}")
        print(f"Тип пересечения: {last_cross_zero['type_zero']}")
    else:
        print("Пересечений MACD и 0 не найдено.")

    return (
        df['macd'].iloc[-1],
        str(last_cross_signal.name.date()) if last_cross_signal is not None else None,
        last_cross_signal['type_signal'] if last_cross_signal is not None else None,
        str(last_cross_zero.name.date()) if last_cross_zero is not None else None,
        last_cross_zero['type_zero'] if last_cross_zero is not None else None
    )



if __name__ == "__main__":
    tables = ['FUTURE']

    for table_name in tables:
        # # ================ раббота с таблицей============================================
        gc = gd.service_account(filename="Sheetus.json")
        worksheet = gc.open("IBKR").worksheet(table_name)
        worksheet_df = pd.DataFrame(worksheet.get_all_values()).replace("", np.nan)
        print(f"==========  {table_name}  ===========")

        worksheet_df_FORMULA = pd.DataFrame(
            worksheet.get_all_values(value_render_option="FORMULA")
        ).replace("", np.nan)
        print(worksheet_df_FORMULA)

        num_total = worksheet_df_FORMULA[0][worksheet_df_FORMULA[0] == "next"].index
        worksheet_df_FORMULA_sum = pd.DataFrame()

        folder_path = 'BARCHART_DATA'
        csv_file = [file for file in os.listdir(folder_path) if file.endswith('.csv')]
        barchart_df = pd.read_csv(f'BARCHART_DATA/{csv_file[0]}', skipfooter=1, engine='python', sep=','
                                  , on_bad_lines='skip', header=1)
        barchart_df.loc[-1] = barchart_df.columns  # Добавляем текущие названия столбцов как новую строку
        barchart_df.index = barchart_df.index + 1  # Смещаем индексы, чтобы сохранить порядок
        barchart_df = barchart_df.sort_index()  # Сортируем строки по индексам

        try:
            barchart_df.columns = ['Commodity', "52W High", "52W Low", "Net Positions", "Net Change", "Long Positions",
                                   'Change', "Short Positions", 'Change', 'un1', 'un2']
        except:
            barchart_df.columns = ['Commodity', "52W High", "52W Low", "Net Positions", "Net Change", "Long Positions",
                                   'Change', "Short Positions", 'Change']

        barchart_df = barchart_df.set_index('Commodity')
        barchart_df.index = barchart_df.index.str.lower()
        print(barchart_df)
        # print(barchart_df.index)
        # print(barchart_df.columns)

        if table_name == "FUTURE":
            futures_list = worksheet_df_FORMULA[1][1:].values.tolist()
            yahoo_data_native = yf.download(futures_list)
            yahoo_data_native_tick = yf.download(futures_list, group_by='ticker')
            yahoo_data = yahoo_data_native['Close'][-132:]

            print('yahoo_data_native_tick')
            print(yahoo_data_native_tick)

            print('yahoo_data')
            print(yahoo_data['LE=F'])
            print('corr')
            print(yahoo_data.corr()['ES=F'])
            for num, next_num in worksheet_df_FORMULA[1:].iterrows():
                tick = next_num[1]
                product = next_num[0]
                print(num)
                print(next_num)
                current_price = yahoo_data[tick].dropna().iloc[-1]
                print('current_price', current_price)
                current_corr = yahoo_data.corr()['ES=F'][tick]
                current_corr_dx = yahoo_data.corr()['DX=F'][tick]
                # Compute the logarithmic returns using the Closing price
                log_returns = np.log(yahoo_data[tick].dropna() / yahoo_data[tick].dropna().shift(1))
                # Compute Volatility using the pandas rolling standard deviation function
                hv = log_returns.rolling(window=21).std() * np.sqrt(252)
                hv = hv[-1]

                hv_60 = log_returns.rolling(window=60).std() * np.sqrt(252)
                hv_60 = hv_60[-1]

                skewness = yahoo_data_native['Close'][-2440:][tick].skew()
                kurtosis = yahoo_data_native['Close'][-2440:][tick].kurtosis()
                beta = run_beta(yahoo_data_native['Close'][tick], "ES=F")
                beta_dx = run_beta(yahoo_data_native['Close'][tick], 'DX=F')
                print(skewness)
                print(kurtosis)

                sma_20, sma_100, rsi = get_tech_data(yahoo_data_native_tick[tick])

                garch = get_garch(yahoo_data_native['Close'][-2440:][tick])
                print('garch', garch)

                median_move, median_move_std = hist_median_move(tick)
                print('median_move', median_move)
                print('median_move_std', median_move_std)
                es_volatility = estimated_vol(yahoo_data_native, tick)

                # trend_now = trend(yahoo_data_native_tick[tick])
                williams = williams_indicator(yahoo_data_native_tick[tick])
                bol_ind_val = bolinger_indecator(yahoo_data_native_tick[tick], 'Close-Open', 'SMA', 2, 20)
                hurst = hurst_coef(yahoo_data_native_tick[tick])
                drift = drift_calc(yahoo_data_native_tick[tick])
                print('drift', drift)
                long_term_component_val, breakpoint_date, breakpoint_val = long_term_component(yahoo_data_native_tick[tick])

                relative_price = get_relative_price(yahoo_data_native['Close'][-244:][tick])

                cot = get_cot(barchart_df, product)

                momentum, opt_hold, hurst_val, opt_lookback = calculate_stock_momentum(yahoo_data_native_tick[tick])

                atr_val = atr(yahoo_data_native_tick[tick]['High'], yahoo_data_native_tick[tick]['Low'],
                              yahoo_data_native_tick[tick]['Close'], 20).iloc[-1]

                atr_today = atr(yahoo_data_native_tick[tick]['High'], yahoo_data_native_tick[tick]['Low'],
                              yahoo_data_native_tick[tick]['Close'], 1).iloc[-1]

                emacd, shorttermsignal_date, shorttermsignal_side, midtermsignal_date, midtermsignal_side = calc_emacd(
                    yahoo_data_native_tick[tick])

                season_pos_val = season_pos(yahoo_data_native_tick[tick])

                print('*' * 200)
                print('season_pos_val', season_pos_val)


                worksheet_df_FORMULA.iloc[num, 3] = round(current_corr, 3)
                worksheet_df_FORMULA.iloc[num, 4] = round(beta, 3)
                worksheet_df_FORMULA.iloc[num, 5] = round(current_corr_dx, 3)
                worksheet_df_FORMULA.iloc[num, 6] = round(beta_dx, 3)
                worksheet_df_FORMULA.iloc[num, 7] = round(current_price, 3)

                worksheet_df_FORMULA.iloc[num, 9] = round(hv, 3)
                worksheet_df_FORMULA.iloc[num, 10] = round(hv_60, 3)
                worksheet_df_FORMULA.iloc[num, 11] = es_volatility / 100
                worksheet_df_FORMULA.iloc[num, 12] = garch
                worksheet_df_FORMULA.iloc[num, 13] = round(atr_val, 4)
                worksheet_df_FORMULA.iloc[num, 14] = round(atr_today, 4)
                worksheet_df_FORMULA.iloc[num, 15] = hurst
                worksheet_df_FORMULA.iloc[num, 16] = round(williams, 3)
                worksheet_df_FORMULA.iloc[num, 17] = bol_ind_val
                worksheet_df_FORMULA.iloc[num, 22] = cot
                worksheet_df_FORMULA.iloc[num, 23] = relative_price
                worksheet_df_FORMULA.iloc[num, 24] = round(season_pos_val*100, 3)
                worksheet_df_FORMULA.iloc[num, 25] = round(rsi, 3)
                worksheet_df_FORMULA.iloc[num, 26] = long_term_component_val
                worksheet_df_FORMULA.iloc[num, 27] = breakpoint_date + '_' + breakpoint_val
                worksheet_df_FORMULA.iloc[num, 28] = round(momentum, 3)
                worksheet_df_FORMULA.iloc[num, 29] = round(opt_hold, 3)
                worksheet_df_FORMULA.iloc[num, 30] = round(opt_lookback, 3)
                worksheet_df_FORMULA.iloc[num, 31] = round(emacd, 3)
                worksheet_df_FORMULA.iloc[num, 32] = shorttermsignal_date + '_' + shorttermsignal_side
                worksheet_df_FORMULA.iloc[num, 33] = midtermsignal_date + '_' + midtermsignal_side
                worksheet_df_FORMULA.iloc[num, 44] = round(median_move, 3)
                worksheet_df_FORMULA.iloc[num, 45] = round(median_move_std, 3)
                worksheet_df_FORMULA.iloc[num, 46] = round(skewness, 3)
                worksheet_df_FORMULA.iloc[num, 47] = round(kurtosis, 3)
                worksheet_df_FORMULA.iloc[num, 48] = round(drift * 100, 4)

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
