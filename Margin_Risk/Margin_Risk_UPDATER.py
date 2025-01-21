import pandas as pd
import numpy as np
import scipy.stats as stats
import sys
import datetime
import time
from dateutil.relativedelta import relativedelta
import yfinance as yf
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
import gspread as gd
from short_selling import get_current_regime
from momentum import calculate_stock_momentum
from up_down_volume import up_down_vol_regr
import requests
import asyncio
import aiohttp
from Earnings_GET import run_earnings_get
import pandas_ta as pta
import warnings
warnings.filterwarnings("ignore")

def get_tech_data(df):
    df["RSI"] = pta.rsi(df["Close"])
    df["SMA_20"] = df["Close"].rolling(window=20).mean()
    df["SMA_100"] = df["Close"].rolling(window=100).mean()

    sma_20 = df["SMA_20"].dropna().iloc[-1]
    sma_100 = df["SMA_100"].dropna().iloc[-1]
    rsi = df["RSI"].dropna().iloc[-1]

    return sma_20, sma_100, rsi


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


def calculate_beta(stock_yahoo, market_yahoo):
    stock_data = stock_yahoo["Close"].pct_change()[1:]
    market_data = market_yahoo.pct_change()[1:]
    covariance = np.cov(stock_data, market_data)[0][1]
    var = np.var(market_data)
    beta = covariance / var
    return beta


def strategist_pcr_signal(ticker_list):
    barcode = "dranatom"
    password = "MSIGX660"
    # ____________________ Работа с Selenium ____________________________
    path = os.path.join(os.getcwd(), "chromedriver.exe")
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("headless")

    checker = webdriver.Chrome(options=chrome_options)

    checker.get(f"https://www.optionstrategist.com/subscriber-content/put-call-ratios")
    time.sleep(2)

    sign_in_userName = checker.find_element(by=By.ID, value="edit-name")
    sign_in_userName.send_keys(barcode)
    sign_in_password = checker.find_element(by=By.ID, value="edit-pass")
    sign_in_password.send_keys(password)
    sign_in = checker.find_element(by=By.ID, value="""edit-submit""")
    sign_in.click()
    time.sleep(2)
    try:
        close_popup = checker.find_element(
            By.XPATH, '//*[@id="PopupSignupForm_0"]/div[2]/div[1]'
        )
        close_popup.click()
    except:
        pass

    time.sleep(2)

    html_txt = checker.find_element(
        By.XPATH, """//*[@id="node-47"]/div/div/div/div/pre"""
    ).text.split("\n")

    strategist_signals = []
    plot_links_list = []

    for tick in ticker_list:
        local_flag = 0
        for piece in html_txt:
            if tick in piece:
                if tick == piece.split(" ")[0] or tick + "_W" == piece.split(" ")[0]:
                    strategist_signals.append(piece[len(tick) + 3 :])
                    # print(piece)
                    local_flag = 1
                    break
        if local_flag == 0:
            strategist_signals.append("Empty")
            # print('Empty')

    # print(strategist_signals)

    # получаем ссылки на графики
    all_link = checker.find_elements(By.XPATH, "//a[@href]")
    total_links = []
    for elem in all_link:
        total_links.append(elem.get_attribute("href"))

    # print(total_links)

    for tick in ticker_list:
        local_flag = 0
        for elem in total_links:
            if "=" + tick + "." in elem or "=" + tick + "_W" in elem:
                plot_links_list.append(elem)
                local_flag = 1
                break
        if local_flag == 0:
            plot_links_list.append("Empty")
            # print('Empty')

    # print(plot_links_list)

    return strategist_signals


def nearest_equal(lst, target):
    # ближайшее значение к таргету относительно переданного списка
    return min(lst, key=lambda x: abs(x - target))


def get_atm_strikes(chains_df, current_price):
    chains_df["ATM_strike_volatility"] = np.nan
    for exp in chains_df["EXP_date"].unique():
        solo_exp_df = chains_df[chains_df["EXP_date"] == exp]
        atm_strike = nearest_equal(solo_exp_df["strike"].tolist(), current_price)
        atm_put_volatility = (
            solo_exp_df[solo_exp_df["strike"] == atm_strike]["iv"]
            .reset_index(drop=True)
            .iloc[0]
        )
        chains_df.loc[
            chains_df["EXP_date"] == exp, "ATM_strike_volatility"
        ] = atm_put_volatility

    return chains_df


def total_loss_on_strike(chain, expiry_price, opt_type):
    """
    Get's the total loss at the given strike price
    """
    # call options with strike price below the expiry price -> loss for option writers
    if opt_type == "call":
        in_money = chain[chain["strike"] < expiry_price][["openInterest", "strike"]]
        in_money["Loss"] = (expiry_price - in_money["strike"]) * in_money[
            "openInterest"
        ]

    if opt_type == "put":
        in_money = chain[chain["strike"] > expiry_price][["openInterest", "strike"]]
        in_money["Loss"] = (in_money["strike"] - expiry_price) * in_money[
            "openInterest"
        ]

    return in_money["Loss"].sum()


def get_max_pain(df_chains_for_max_pain):
    call_max_pain_list = []
    put_max_pain_list = []
    strike_list = []

    max_pain_put = df_chains_for_max_pain[
        df_chains_for_max_pain["side"] == "put"
    ].reset_index(drop=True)
    max_pain_call = df_chains_for_max_pain[
        df_chains_for_max_pain["side"] == "call"
    ].reset_index(drop=True)

    for i in range(len(max_pain_put)):
        put_max_pain_list.append(
            total_loss_on_strike(max_pain_put, max_pain_put["strike"][i], "put")
        )
        call_max_pain_list.append(
            total_loss_on_strike(max_pain_call, max_pain_put["strike"][i], "call")
        )
        strike_list.append(max_pain_put["strike"][i])

    max_pain = pd.DataFrame(
        {"PUT": put_max_pain_list, "CALL": call_max_pain_list, "Strike": strike_list}
    )

    max_pain_value = (max_pain["PUT"] + max_pain["CALL"]).min()
    max_pain["Sum"] = max_pain["PUT"] + max_pain["CALL"]
    max_pain_strike = (
        max_pain[max_pain["Sum"] == max_pain_value]["Strike"]
        .reset_index(drop=True)
        .iloc[0]
    )

    return max_pain_strike


async def get_market_data(session, url):
    async with session.get(url) as resp:
        market_data = await resp.json(content_type=None)
        option_chain_df = pd.DataFrame(market_data)

        return option_chain_df


async def get_prime(exp_date_list, tick):
    option_chain_df = pd.DataFrame()
    async with aiohttp.ClientSession() as session:
        tasks = []
        for exp in exp_date_list:
            url = f"https://api.marketdata.app/v1/options/chain/{tick}/?token={KEY}&expiration={exp}"  #
            tasks.append(asyncio.create_task(get_market_data(session, url)))

        solo_exp_chain = await asyncio.gather(*tasks)

        for chain in solo_exp_chain:
            option_chain_df = pd.concat([option_chain_df, chain])

    option_chain_df["updated"] = pd.to_datetime(option_chain_df["updated"], unit="s")
    option_chain_df["EXP_date"] = pd.to_datetime(
        option_chain_df["expiration"], unit="s", errors="coerce"
    )
    option_chain_df["days_to_exp"] = (
        option_chain_df["EXP_date"] - option_chain_df["updated"]
    ).dt.days
    option_chain_df = option_chain_df.reset_index(drop=True)

    return option_chain_df


def get_df_chains(tick, limit_date_min, limit_date_max):
    url_exp = f"https://api.marketdata.app/v1/options/expirations/{tick}/?token={KEY}"
    response_exp = requests.request("GET", url_exp)
    expirations_df = pd.DataFrame(response_exp.json())
    expirations_df["expirations"] = pd.to_datetime(
        expirations_df["expirations"], format="%Y-%m-%d"
    )
    expirations_df = expirations_df[expirations_df["expirations"] > limit_date_min]
    expirations_df = expirations_df[expirations_df["expirations"] < limit_date_max]
    print(expirations_df)
    option_chain_df = asyncio.run(get_prime(expirations_df["expirations"], tick))

    return option_chain_df


if __name__ == "__main__":
    KEY = "ckZsUXdiMTZEZVQ3a25TVEFtMm9SeURsQ1RQdk5yWERHS0RXaWNpWVJ2cz0"
    api_token = "34b27ff5b013ecb09d2eeafdf8724472:2ab9f1f92f838c3c431fc85e772d0f6c"
    # ================ раббота с таблицей============================================
    gc = gd.service_account(filename="Seetus.json")
    worksheet = gc.open("IBKR").worksheet("Margin/risk_EXANTE")
    worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace("", np.nan)
    last_row = worksheet_df.where(worksheet_df["ТИКЕР"] == None)
    worksheet_df = worksheet_df[: len(worksheet_df["PL"].dropna()) - 1]
    print(worksheet_df)
    tickers_list = worksheet_df["ТИКЕР"].values.tolist()
    worksheet_df_FORMULA = pd.DataFrame(
        worksheet.get_all_records(value_render_option="FORMULA")
    ).replace("", np.nan)

    print("worksheet_df_FORMULA")
    print(worksheet_df_FORMULA)

    yahoo_data = yf.download(tickers_list, group_by="ticker").dropna(axis=1, how="all")
    yahoo_data.index = pd.to_datetime(yahoo_data.index)
    trend_moving_list = []

    gf_score_list = []
    gf_valuation_list = []
    pcr_list = []
    max_pain_list = []

    start_date = datetime.datetime.now().date()
    start_date = start_date.strftime("%Y-%m-%d")
    regime_start_date = (
        datetime.datetime.strptime(start_date, "%Y-%m-%d") - relativedelta(years=5)
    ).strftime("%Y-%m-%d")
    beta_start_date = (
        datetime.datetime.strptime(start_date, "%Y-%m-%d") - relativedelta(years=3)
    ).strftime("%Y-%m-%d")
    benchmark = round(
        yf.download(
            tickers="^GSPC",
            start=regime_start_date,
            interval="1d",
            group_by="column",
            auto_adjust=True,
            prepost=True,
            proxy=None,
        )["Close"],
        2,
    )

    fdafsafsd = strategist_pcr_signal(tickers_list)
    print(fdafsafsd)
    for pcr_signal in fdafsafsd:
        if "NOW ON A SELL" in pcr_signal:
            pcr_list.append("bear")
        elif "NOW ON A BUY" in pcr_signal:
            pcr_list.append("bull")
        else:
            pcr_list.append("Empty")

    print(pcr_list)

    earnings = run_earnings_get(tickers_list)

    yahoo_data_regime = yf.download(tickers_list, group_by="ticker", auto_adjust = True).dropna(axis=1, how="all")
    yahoo_data_regime.index = pd.to_datetime(yahoo_data.index)

    for i, tick in enumerate(tickers_list):
        try:
            current_price = yahoo_data[tick]["Close"].iloc[-1]
            # скользящий тренд
            print(tick)
            trend_moving = trend(yahoo_data[tick])
            # тренд режим

            current_regime = get_current_regime(
                yahoo_data_regime[tick], benchmark, regime_start_date, tick
            )

            trend_short = current_regime[0]
            trend_rel = current_regime[1]

            # url = f"https://api.gurufocus.com/public/user/{api_token}/stock/{tick}/summary"
            # response_exp = requests.request("GET", url).json()
            # guru_df = pd.DataFrame(response_exp["summary"])
            # gf_score = guru_df["general"]["gf_score"]
            # gf_valuation = guru_df["general"]["gf_valuation"]
            # # gf_score_list.append(gf_score)
            # # gf_valuation_list.append(gf_valuation)
            # print("gf_score:", gf_score)
            # print("gf_valuation:", gf_valuation)

            # let's calculate the beta for Apple stock with respect to the S&P500 market index
            beta = calculate_beta(
                yahoo_data[tick][beta_start_date:], benchmark[beta_start_date:]
            )

            print("Beta:", beta)

            # ------------------------------------------ Max Pain  ---------------------

            limit_date_min = datetime.datetime.now() + relativedelta(days=+3)
            limit_date_max = datetime.datetime.now() + relativedelta(days=+31)
            df_chains = get_df_chains(tick, limit_date_min, limit_date_max)
            #
            # print('---------------- df_chains  ---------------------')
            # print(df_chains)
            df_chains = get_atm_strikes(df_chains, current_price)
            max_pain_val = get_max_pain(df_chains)
            print("max_pain_val", max_pain_val)

            # ------------------------------------------ Momentum  ---------------------

            print('Momentum')
            stock_momentum = calculate_stock_momentum(tick, yahoo_data)
            print('Momentum', stock_momentum)

            # ------------------------------------------ UP DOWN VOLUME  ---------------------

            print('UP DOWN VOLUME')

            up_dow_vol, up_dow_vol_regr = up_down_vol_regr(tick, yahoo_data)

            print('UP DOWN VOLUME', up_dow_vol, up_dow_vol_regr)

            # UP/Down Volume
            worksheet_df_FORMULA["Тренд по скользящим"].iloc[i] = trend_moving
            worksheet_df_FORMULA["Абсолютный ряд"].iloc[i] = trend_short
            worksheet_df_FORMULA["Относительный ряд"].iloc[i] = trend_rel
            worksheet_df_FORMULA["Momentum"].iloc[i] = stock_momentum
            worksheet_df_FORMULA["UP/Down Volume"].iloc[i] = up_dow_vol
            worksheet_df_FORMULA["UP/Down Volume Regression"].iloc[i] = up_dow_vol_regr
            # worksheet_df_FORMULA["GF SCORE"].iloc[i] = gf_score
            worksheet_df_FORMULA["PCR"].iloc[i] = pcr_list[i]
            worksheet_df_FORMULA["БЕТА"].iloc[i] = round(beta, 2)
            # worksheet_df_FORMULA["Max Pain"].iloc[i] = max_pain_val
            worksheet_df_FORMULA["Дней до отчетности/дивиденда"].iloc[i] = earnings[i]

        except Exception as eeee:
            print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(eeee).__name__, eeee)

            worksheet_df_FORMULA["Тренд по скользящим"].iloc[i] = "No data"
            worksheet_df_FORMULA["Абсолютный ряд"].iloc[i] = "No data"
            worksheet_df_FORMULA["Относительный ряд"].iloc[i] = "No data"
            worksheet_df_FORMULA["Momentum"].iloc[i] = "No data"
            worksheet_df_FORMULA["UP/Down Volume"].iloc[i] = "No data"
            worksheet_df_FORMULA["UP/Down Volume Regression"].iloc[i] = "No data"
            # worksheet_df_FORMULA["GF SCORE"].iloc[i] = "No data"
            worksheet_df_FORMULA["PCR"].iloc[i] = "No data"
            worksheet_df_FORMULA["БЕТА"].iloc[i] = "No data"
            # worksheet_df_FORMULA["Max Pain"].iloc[i] = "No data"
            worksheet_df_FORMULA["Дней до отчетности/дивиденда"].iloc[i] = earnings[i]

        print(worksheet_df_FORMULA)


    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna("'")
    # # # ===================================  запись в таблицу ================================================
    worksheet.update(
        "A1",
        [worksheet_df_FORMULA.columns.values.tolist()]
        + worksheet_df_FORMULA.values.tolist(),
        value_input_option="USER_ENTERED",
    )

    # ===========================================================
    # ================ Margin/risk_SAXO ============================================
    # ===========================================================

    # # ================ раббота с таблицей============================================
    gc = gd.service_account(filename="Seetus.json")
    worksheet = gc.open("IBKR").worksheet("Margin/risk_SAXO")
    worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace("", np.nan)
    last_row = worksheet_df.where(worksheet_df["ТИКЕР"] == None)
    worksheet_df = worksheet_df[: len(worksheet_df["SHORT VALUE"].dropna()) - 1]
    print(worksheet_df)
    tickers_list = worksheet_df["ТИКЕР"].values.tolist()
    worksheet_df_FORMULA = pd.DataFrame(
        worksheet.get_all_records(value_render_option="FORMULA")
    ).replace("", np.nan)

    print("worksheet_df_FORMULA")
    print(worksheet_df_FORMULA)

    yahoo_data = yf.download(tickers_list, group_by="ticker").dropna(axis=1, how="all")
    yahoo_data.index = pd.to_datetime(yahoo_data.index)
    trend_moving_list = []

    gf_score_list = []
    gf_valuation_list = []
    pcr_list = []
    max_pain_list = []

    start_date = datetime.datetime.now().date()
    start_date = start_date.strftime("%Y-%m-%d")
    regime_start_date = (
        datetime.datetime.strptime(start_date, "%Y-%m-%d") - relativedelta(years=5)
    ).strftime("%Y-%m-%d")
    beta_start_date = (
        datetime.datetime.strptime(start_date, "%Y-%m-%d") - relativedelta(years=3)
    ).strftime("%Y-%m-%d")
    benchmark = round(
        yf.download(
            tickers="^GSPC",
            start=regime_start_date,
            interval="1d",
            group_by="column",
            auto_adjust=True,
            prepost=True,
            proxy=None,
        )["Close"],
        2,
    )

    fdafsafsd = strategist_pcr_signal(tickers_list)
    print(fdafsafsd)
    for pcr_signal in fdafsafsd:
        if "NOW ON A SELL" in pcr_signal:
            pcr_list.append("bear")
        elif "NOW ON A BUY" in pcr_signal:
            pcr_list.append("bull")
        else:
            pcr_list.append("Empty")

    print(pcr_list)

    earnings = run_earnings_get(tickers_list)

    yahoo_data_regime = yf.download(tickers_list, group_by="ticker", auto_adjust = True).dropna(axis=1, how="all")
    yahoo_data_regime.index = pd.to_datetime(yahoo_data.index)

    for i, tick in enumerate(tickers_list):
        try:
            current_price = yahoo_data[tick]["Close"].iloc[-1]
            # скользящий тренд
            print(tick)
            trend_moving = trend(yahoo_data[tick])
            # тренд режим
            current_regime = get_current_regime(
                yahoo_data_regime[tick], benchmark, regime_start_date, tick
            )
            trend_short = current_regime[0]
            trend_rel = current_regime[1]

            # url = f"https://api.gurufocus.com/public/user/{api_token}/stock/{tick}/summary"
            # response_exp = requests.request("GET", url).json()
            # guru_df = pd.DataFrame(response_exp["summary"])
            # gf_score = guru_df["general"]["gf_score"]
            # gf_valuation = guru_df["general"]["gf_valuation"]
            # print("gf_score:", gf_score)
            # print("gf_valuation:", gf_valuation)

            # let's calculate the beta for Apple stock with respect to the S&P500 market index
            beta = calculate_beta(
                yahoo_data[tick][beta_start_date:], benchmark[beta_start_date:]
            )

            print("Beta:", beta)

            # ------------------------------------------ Max Pain  ---------------------

            limit_date_min = datetime.datetime.now() + relativedelta(days=+3)
            limit_date_max = datetime.datetime.now() + relativedelta(days=+31)
            df_chains = get_df_chains(tick, limit_date_min, limit_date_max)
            #
            # print('---------------- df_chains  ---------------------')
            # print(df_chains)
            df_chains = get_atm_strikes(df_chains, current_price)
            max_pain_val = get_max_pain(df_chains)
            print("max_pain_val", max_pain_val)

            # ------------------------------------------ Momentum  ---------------------
            print('Momentum')
            stock_momentum = calculate_stock_momentum(tick, yahoo_data)
            print('Momentum', stock_momentum)

            # ------------------------------------------ UP DOWN VOLUME  ---------------------

            up_dow_vol, up_dow_vol_regr = up_down_vol_regr(tick, yahoo_data)


            worksheet_df_FORMULA["Тренд по скользящим"].iloc[i] = trend_moving
            worksheet_df_FORMULA["Абсолютный ряд"].iloc[i] = trend_short
            worksheet_df_FORMULA["Относительный ряд"].iloc[i] = trend_rel
            worksheet_df_FORMULA["Momentum"].iloc[i] = stock_momentum
            worksheet_df_FORMULA["UP/Down Volume"].iloc[i] = up_dow_vol
            worksheet_df_FORMULA["UP/Down Volume Regression"].iloc[i] = up_dow_vol_regr
            # worksheet_df_FORMULA["GF SCORE"].iloc[i] = gf_score
            worksheet_df_FORMULA["PCR"].iloc[i] = pcr_list[i]
            worksheet_df_FORMULA["БЕТА"].iloc[i] = round(beta, 2)
            # worksheet_df_FORMULA["Max Pain"].iloc[i] = max_pain_val
            worksheet_df_FORMULA["Дней до отчетности/дивиденда"].iloc[i] = earnings[i]


        except Exception as eeee:
            print(eeee)
            worksheet_df_FORMULA["Тренд по скользящим"].iloc[i] = "No data"
            worksheet_df_FORMULA["Абсолютный ряд"].iloc[i] = "No data"
            worksheet_df_FORMULA["Относительный ряд"].iloc[i] = "No data"
            worksheet_df_FORMULA["Momentum"].iloc[i] = "No data"
            worksheet_df_FORMULA["UP/Down Volume"].iloc[i] = "No data"
            worksheet_df_FORMULA["UP/Down Volume Regression"].iloc[i] = "No data"
            # worksheet_df_FORMULA["GF SCORE"].iloc[i] = "No data"
            worksheet_df_FORMULA["PCR"].iloc[i] = "No data"
            worksheet_df_FORMULA["БЕТА"].iloc[i] = "No data"
            # worksheet_df_FORMULA["Max Pain"].iloc[i] = "No data"
            worksheet_df_FORMULA["Дней до отчетности/дивиденда"].iloc[i] = earnings[i]

        print(worksheet_df_FORMULA)

    worksheet_df_FORMULA = worksheet_df_FORMULA.fillna("'")
    # # # ===================================  запись в таблицу ================================================
    worksheet.update(
        "A1",
        [worksheet_df_FORMULA.columns.values.tolist()]
        + worksheet_df_FORMULA.values.tolist(),
        value_input_option="USER_ENTERED",
    )
