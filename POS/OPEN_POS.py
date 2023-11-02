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

pd.options.mode.chained_assignment = None


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

    return prob_50, expected_profit, avg_dtc, prob_100


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

    return prob_50, expected_profit, avg_dtc, prob_100


def get_abs_return(
    price_array,
    type_option,
    days_to_exp,
    days_to_exp_short,
    history_vol,
    current_price,
    strike,
    prime,
    vol_opt,
):
    put_price_list = []
    call_price_list = []
    proba_list = []
    price_gen_list = []

    for stock_price_num in range(len(price_array)):
        try:
            P_below = stats.norm.cdf(
                (
                    np.log(price_array[stock_price_num] / current_price)
                    / (history_vol * math.sqrt(days_to_exp_short / 365))
                )
            )
            P_current = stats.norm.cdf(
                (
                    np.log(price_array[stock_price_num + 1] / current_price)
                    / (history_vol * math.sqrt(days_to_exp_short / 365))
                )
            )
            proba_list.append(P_current - P_below)
            if type_option == "Short":
                c = mibian.BS(
                    [price_array[stock_price_num + 1], strike, 4, 1],
                    volatility=vol_opt * 100,
                )
            if type_option == "Long":
                c = mibian.BS(
                    [price_array[stock_price_num + 1], strike, 4, days_to_exp],
                    volatility=vol_opt * 100,
                )

            put_price_list.append(c.putPrice)
            call_price_list.append(c.callPrice)
            price_gen_list.append(price_array[stock_price_num + 1])
        except:
            pass

    put_df = pd.DataFrame(
        {
            "gen_price": price_gen_list,
            "put_price": put_price_list,
            "call_price": call_price_list,
            "proba": proba_list,
        }
    )

    put_df["return"] = put_df["put_price"] - prime

    if type_option == "Short":
        return ((prime - put_df["put_price"]) * put_df["proba"]).sum()

    if type_option == "Long":
        return ((put_df["put_price"] - prime) * put_df["proba"]).sum()


def expected_return_calc(
    vol_put_short,
    vol_put_long,
    current_price,
    history_vol,
    days_to_exp_short,
    days_to_exp_long,
    strike_put_long,
    strike_put_short,
    prime_put_long,
    prime_put_short,
):
    # print('expected_return CALCULATION ...')

    price_array = np.arange(
        current_price - current_price / 2, current_price + current_price, 0.2
    )

    short_finish = get_abs_return(
        price_array,
        "Short",
        days_to_exp_short,
        days_to_exp_short,
        history_vol,
        current_price,
        strike_put_short,
        prime_put_short,
        vol_put_short,
    )

    long_finish = get_abs_return(
        price_array,
        "Long",
        days_to_exp_long,
        days_to_exp_short,
        history_vol,
        current_price,
        strike_put_long,
        prime_put_long,
        vol_put_long,
    )

    expected_return = (short_finish + long_finish) * 100

    return expected_return


def get_proba_50_calendar(
    current_price,
    yahoo_data,
    put_long_strike,
    put_long_price,
    put_short_strike,
    put_short_price,
    sigma_short,
    sigma_long,
    days_to_expiration_short,
    days_to_expiration_long,
):
    rate = 4.6
    closing_days_array = [days_to_expiration_short]
    percentage_array = [30]
    trials = 3000

    proba_50 = putCalendar(
        current_price,
        sigma_short,
        sigma_long,
        rate,
        trials,
        days_to_expiration_short,
        days_to_expiration_long,
        closing_days_array,
        percentage_array,
        put_long_strike,
        put_long_price,
        put_short_strike,
        put_short_price,
        yahoo_data,
    )

    return proba_50


if __name__ == "__main__":
    # **********************   Указываем назыание таблицы в которой работаем *************
    tables = [
        "POS_template_OTM_calendar"
    ]  #  "POS_template_call", 'POS_template_put', 'POS_template_strangl', 'POS_template_OTM_calendar', 'POS_template_ITM_calendar'

    for table_name in tables:
        # # ================ раббота с таблицей============================================
        gc = gd.service_account(filename="Seetus.json")
        worksheet = gc.open("IBKR").worksheet(table_name)
        worksheet_df = pd.DataFrame(worksheet.get_all_values()).replace("", np.nan)
        print(f"==========  {table_name}  ===========")
        # print(worksheet_df)
        # tickers_list = worksheet_df["Тикер"].values.tolist()
        worksheet_df_FORMULA = pd.DataFrame(
            worksheet.get_all_values(value_render_option="FORMULA")
        ).replace("", np.nan)

        # print("worksheet_df_FORMULA")
        # print(worksheet_df_FORMULA)
        num_total = worksheet_df_FORMULA[0][worksheet_df_FORMULA[0] == "next"].index
        print("num_total", num_total)

        worksheet_df_FORMULA_sum = pd.DataFrame()

        if table_name == "POS_template_put":
            for num, next_num in enumerate(num_total):
                # last_num = next_num + 1
                try:
                    if num >= 0:
                        solo_company_data = worksheet_df.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)
                        solo_company_data_formula = worksheet_df_FORMULA.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)

                        worksheet_df_FORMULA_sum = pd.concat(
                            [worksheet_df_FORMULA_sum, solo_company_data_formula]
                        )
                        continue
                except:
                    solo_company_data = worksheet_df.iloc[num_total[-1] :].reset_index(
                        drop=True
                    )
                    solo_company_data_formula = worksheet_df_FORMULA.iloc[
                        num_total[-1] :
                    ].reset_index(drop=True)
                print("============")
                # Работаем с карточкой одной компании

                # ticker = solo_company_data[solo_company_data[0] == "ПОЗИЦИЯ"][3].values[0]
                ticker = solo_company_data.iloc[2, 3]
                print("ticker", ticker)
                # solo_company_data.iloc[2, 3] = "pisya" # заполнить поле
                yahoo_data = yf.download(ticker)
                current_price = float(solo_company_data.iloc[2, 13])

                short_strike = float(solo_company_data.iloc[4, 13])
                short_price = float(solo_company_data.iloc[6, 11])
                sigma = float(solo_company_data.iloc[7, 11]) * 100
                days_to_expiration = int(solo_company_data.iloc[3, 1])
                number_positions = abs(float(solo_company_data.iloc[4, 11]))

                pop = solo_company_data.iloc[4, 8]

                print("start_price", current_price)
                print("short_strike", short_strike)
                print("start_short_price", short_price)
                print("sigma", sigma)
                print("days_to_expiration", days_to_expiration)

                pop_50, expected_profit, avg_dtc = get_proba_50_put(
                    current_price,
                    yahoo_data,
                    short_strike,
                    short_price,
                    sigma,
                    days_to_expiration,
                )

                print("pop_50", pop_50)
                print("expected_profit", expected_profit)
                print("avg_dtc", avg_dtc[0])

                solo_company_data_formula.iloc[
                    8, 3
                ] = pop_50  # заполняем поле в таблице
                solo_company_data_formula.iloc[7, 3] = int(
                    avg_dtc[0]
                )  # заполняем поле в таблице
                solo_company_data_formula.iloc[3, 3] = (
                    expected_profit * number_positions
                )  # заполняем поле в таблице

                worksheet_df_FORMULA_sum = pd.concat(
                    [worksheet_df_FORMULA_sum, solo_company_data_formula]
                )
                print("=================================")
            print(worksheet_df_FORMULA_sum)

            worksheet_df_FORMULA_sum = worksheet_df_FORMULA_sum.fillna("'")
            # # # ===================================  запись в таблицу ================================================
            worksheet.update(
                "A1",
                worksheet_df_FORMULA_sum.values.tolist(),
                value_input_option="USER_ENTERED",
            )

        # ============================================================================================================
        # ============================================================================================================
        # ============================================================================================================
        # ========================================     CALL     =====================================================
        # ============================================================================================================
        # ============================================================================================================
        # ============================================================================================================
        if table_name == "POS_template_call":
            for num, next_num in enumerate(num_total):
                # last_num = next_num + 1
                try:
                    if num >= 0:
                        solo_company_data = worksheet_df.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)
                        solo_company_data_formula = worksheet_df_FORMULA.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)

                        worksheet_df_FORMULA_sum = pd.concat(
                            [worksheet_df_FORMULA_sum, solo_company_data_formula]
                        )
                        continue
                except:
                    solo_company_data = worksheet_df.iloc[num_total[-1] :].reset_index(
                        drop=True
                    )
                    solo_company_data_formula = worksheet_df_FORMULA.iloc[
                        num_total[-1] :
                    ].reset_index(drop=True)
                print("============")
                # Работаем с карточкой одной компании

                # ticker = solo_company_data[solo_company_data[0] == "ПОЗИЦИЯ"][3].values[0]
                ticker = solo_company_data.iloc[2, 3]
                print("ticker", ticker)
                # solo_company_data.iloc[2, 3] = "pisya" # заполнить поле
                yahoo_data = yf.download(ticker)
                current_price = float(solo_company_data.iloc[2, 13])

                short_strike = float(solo_company_data.iloc[4, 13])
                short_price = float(solo_company_data.iloc[6, 11])
                sigma = float(solo_company_data.iloc[7, 11]) * 100
                days_to_expiration = int(solo_company_data.iloc[3, 1])
                number_positions = abs(float(solo_company_data.iloc[4, 11]))

                pop = solo_company_data.iloc[4, 8]

                print("start_price", current_price)
                print("short_strike", short_strike)
                print("start_short_price", short_price)
                print("sigma", sigma)
                print("days_to_expiration", days_to_expiration)

                proba_50, expected_profit, avg_dtc, prob_100 = get_proba_50_call(
                    current_price,
                    yahoo_data,
                    short_strike,
                    short_price,
                    sigma,
                    days_to_expiration,
                )

                print("pop_50", proba_50)
                print("expected_profit", expected_profit)
                print("avg_dtc", avg_dtc[0])

                solo_company_data_formula.iloc[
                    8, 3
                ] = proba_50  # заполняем поле в таблице
                solo_company_data_formula.iloc[7, 3] = int(
                    avg_dtc[0]
                )  # заполняем поле в таблице
                solo_company_data_formula.iloc[3, 3] = (
                    expected_profit * number_positions
                )  # заполняем поле в таблице

                worksheet_df_FORMULA_sum = pd.concat(
                    [worksheet_df_FORMULA_sum, solo_company_data_formula]
                )
                print("=================================")
            print(worksheet_df_FORMULA_sum)

            worksheet_df_FORMULA_sum = worksheet_df_FORMULA_sum.fillna("'")
            # # # ===================================  запись в таблицу ================================================
            worksheet.update(
                "A1",
                worksheet_df_FORMULA_sum.values.tolist(),
                value_input_option="USER_ENTERED",
            )
        # ============================================================================================================
        # ============================================================================================================
        # ============================================================================================================
        # ========================================   STRANGLE   =====================================================
        # ============================================================================================================
        # ============================================================================================================
        # ============================================================================================================

        if table_name == "POS_template_strangl":
            for num, next_num in enumerate(num_total):
                # last_num = next_num + 1
                try:
                    if num >= 0:
                        solo_company_data = worksheet_df.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)
                        solo_company_data_formula = worksheet_df_FORMULA.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)

                        worksheet_df_FORMULA_sum = pd.concat(
                            [worksheet_df_FORMULA_sum, solo_company_data_formula]
                        )
                        continue
                except:
                    solo_company_data = worksheet_df.iloc[num_total[-1] :].reset_index(
                        drop=True
                    )
                    solo_company_data_formula = worksheet_df_FORMULA.iloc[
                        num_total[-1] :
                    ].reset_index(drop=True)
                print("============")
                # Работаем с карточкой одной компании

                # ticker = solo_company_data[solo_company_data[0] == "ПОЗИЦИЯ"][3].values[0]
                ticker = solo_company_data.iloc[2, 3]
                print("ticker", ticker)
                # solo_company_data.iloc[2, 3] = "pisya" # заполнить поле
                yahoo_data = yf.download(ticker)
                current_price = float(solo_company_data.iloc[2, 13])

                call_short_strike = float(solo_company_data.iloc[4, 13])
                put_short_strike = float(solo_company_data.iloc[5, 13])
                call_short_price = float(solo_company_data.iloc[13, 13])
                put_short_price = float(solo_company_data.iloc[13, 11])
                sigma = (
                    (
                        float(solo_company_data.iloc[8, 11])
                        + float(solo_company_data.iloc[9, 11])
                    )
                    / 2
                    * 100
                )

                days_to_expiration = int(solo_company_data.iloc[3, 1])
                number_positions = abs(float(solo_company_data.iloc[4, 11]))

                pop = solo_company_data.iloc[4, 8]

                print("start_price", current_price)
                print("call_short_strike", call_short_strike)
                print("put_short_strike", put_short_strike)
                print("call_short_price", call_short_price)
                print("put_short_price", put_short_price)
                print("sigma", sigma)
                print("days_to_expiration", days_to_expiration)

                proba_50, expected_profit, avg_dtc, prob_100 = get_proba_50_strangle(
                    current_price,
                    yahoo_data,
                    call_short_strike,
                    put_short_strike,
                    call_short_price,
                    put_short_price,
                    sigma,
                    days_to_expiration,
                )

                print("pop_50", proba_50)
                print("expected_profit", expected_profit)
                print("avg_dtc", avg_dtc[0])

                solo_company_data_formula.iloc[
                    8, 3
                ] = proba_50  # заполняем поле в таблице
                solo_company_data_formula.iloc[7, 3] = int(
                    avg_dtc[0]
                )  # заполняем поле в таблице
                solo_company_data_formula.iloc[3, 3] = (
                    expected_profit * number_positions
                )  # заполняем поле в таблице

                worksheet_df_FORMULA_sum = pd.concat(
                    [worksheet_df_FORMULA_sum, solo_company_data_formula]
                )
                print("=================================")
            print(worksheet_df_FORMULA_sum)

            worksheet_df_FORMULA_sum = worksheet_df_FORMULA_sum.fillna("'")
            # # # ===================================  запись в таблицу ================================================
            worksheet.update(
                "A1",
                worksheet_df_FORMULA_sum.values.tolist(),
                value_input_option="USER_ENTERED",
            )

            # ============================================================================================================
            # ============================================================================================================
            # ============================================================================================================
            # ========================================   CALENDAR OTM  =====================================================
            # ============================================================================================================
            # ============================================================================================================
            # ============================================================================================================

        if table_name == "POS_template_OTM_calendar":
            for num, next_num in enumerate(num_total):
                # last_num = next_num + 1
                try:
                    if num >= 0:
                        solo_company_data = worksheet_df.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)
                        solo_company_data_formula = worksheet_df_FORMULA.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)

                        worksheet_df_FORMULA_sum = pd.concat(
                            [worksheet_df_FORMULA_sum, solo_company_data_formula]
                        )
                        continue
                except:
                    solo_company_data = worksheet_df.iloc[num_total[-1] :].reset_index(
                        drop=True
                    )
                    solo_company_data_formula = worksheet_df_FORMULA.iloc[
                        num_total[-1] :
                    ].reset_index(drop=True)
                print("============")
                # Работаем с карточкой одной компании

                # ticker = solo_company_data[solo_company_data[0] == "ПОЗИЦИЯ"][3].values[0]
                ticker = solo_company_data.iloc[2, 3]
                print("ticker", ticker)
                # solo_company_data.iloc[2, 3] = "pisya" # заполнить поле
                yahoo_data = yf.download(ticker)
                # Compute the logarithmic returns using the Closing price
                log_returns = np.log(yahoo_data["Close"] / yahoo_data["Close"].shift(1))
                # Compute Volatility using the pandas rolling standard deviation function
                hv = log_returns.rolling(window=252).std() * np.sqrt(252)
                hv = hv[-1]
                current_price = float(solo_company_data.iloc[2, 13])
                put_long_strike = float(solo_company_data.iloc[5, 13])
                put_short_strike = float(solo_company_data.iloc[5, 11])

                put_long_price = float(solo_company_data.iloc[15, 13])
                put_short_price = float(solo_company_data.iloc[15, 11])

                sigma_short = float(solo_company_data.iloc[11, 11]) * 100
                sigma_long = float(solo_company_data.iloc[10, 11]) * 100

                days_to_expiration_short = int(solo_company_data.iloc[13, 11])
                days_to_expiration_long = int(solo_company_data.iloc[4, 13])
                days_to_expiration_long_return = (
                    int(solo_company_data.iloc[12, 11]) - days_to_expiration_short
                )
                number_positions = abs(float(solo_company_data.iloc[6, 11]))

                print("current_price", current_price)
                print("put_long_strike", put_long_strike)
                print("put_short_strike", put_short_strike)
                print("put_long_price", put_long_price)
                print("put_short_price", put_short_price)
                print("hv", hv)
                print("sigma_short", sigma_short)
                print("sigma_long", sigma_long)
                print("days_to_expiration_short", days_to_expiration_short)
                print("days_to_expiration_long", days_to_expiration_long)

                proba_50, avg_dtc = get_proba_50_calendar(
                    current_price,
                    yahoo_data,
                    put_long_strike,
                    put_long_price,
                    put_short_strike,
                    put_short_price,
                    sigma_short,
                    sigma_long,
                    days_to_expiration_short,
                    days_to_expiration_long,
                )

                print("proba_50", proba_50)
                expected_return = expected_return_calc(
                    sigma_short,
                    sigma_long,
                    current_price,
                    hv,
                    days_to_expiration_short,
                    days_to_expiration_long_return,
                    put_long_strike,
                    put_short_strike,
                    put_long_price,
                    put_short_price,
                )

                print("expected_return", expected_return)
                print("pop_30", proba_50)
                print("avg_dtc", avg_dtc[0])

                solo_company_data_formula.iloc[
                    8, 3
                ] = proba_50  # заполняем поле в таблице
                solo_company_data_formula.iloc[7, 3] = int(
                    avg_dtc[0]
                )  # заполняем поле в таблице
                solo_company_data_formula.iloc[3, 3] = (
                    expected_return * number_positions
                )  # заполняем поле в таблице

                worksheet_df_FORMULA_sum = pd.concat(
                    [worksheet_df_FORMULA_sum, solo_company_data_formula]
                )
                print("=================================")
            print(worksheet_df_FORMULA_sum)

            worksheet_df_FORMULA_sum = worksheet_df_FORMULA_sum.fillna("'")
            # # # ===================================  запись в таблицу ================================================
            worksheet.update(
                "A1",
                worksheet_df_FORMULA_sum.values.tolist(),
                value_input_option="USER_ENTERED",
            )

            # ============================================================================================================
            # ============================================================================================================
            # ============================================================================================================
            # ========================================   CALENDAR ITM  =====================================================
            # ============================================================================================================
            # ============================================================================================================
            # ============================================================================================================

        if table_name == "POS_template_ITM_calendar":
            for num, next_num in enumerate(num_total):
                # last_num = next_num + 1
                try:
                    if num >= 0:
                        solo_company_data = worksheet_df.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)
                        solo_company_data_formula = worksheet_df_FORMULA.iloc[
                            num_total[num] : num_total[num + 1]
                        ].reset_index(drop=True)

                        worksheet_df_FORMULA_sum = pd.concat(
                            [worksheet_df_FORMULA_sum, solo_company_data_formula]
                        )
                        continue
                except:
                    solo_company_data = worksheet_df.iloc[num_total[-1] :].reset_index(
                        drop=True
                    )
                    solo_company_data_formula = worksheet_df_FORMULA.iloc[
                        num_total[-1] :
                    ].reset_index(drop=True)
                print("============")
                print(solo_company_data_formula)
                # Работаем с карточкой одной компании

                # ticker = solo_company_data[solo_company_data[0] == "ПОЗИЦИЯ"][3].values[0]
                ticker = solo_company_data.iloc[2, 3]
                print("ticker", ticker)
                # solo_company_data.iloc[2, 3] = "pisya" # заполнить поле
                yahoo_data = yf.download(ticker)
                # Compute the logarithmic returns using the Closing price
                log_returns = np.log(yahoo_data["Close"] / yahoo_data["Close"].shift(1))
                # Compute Volatility using the pandas rolling standard deviation function
                hv = log_returns.rolling(window=252).std() * np.sqrt(252)
                hv = hv[-1]
                current_price = float(solo_company_data.iloc[2, 13])
                put_long_strike = float(solo_company_data.iloc[5, 13])
                put_short_strike = float(solo_company_data.iloc[5, 11])

                put_long_price = float(solo_company_data.iloc[15, 13])
                put_short_price = float(solo_company_data.iloc[15, 11])

                sigma_short = float(solo_company_data.iloc[11, 11]) * 100
                sigma_long = float(solo_company_data.iloc[10, 11]) * 100

                days_to_expiration_short = int(solo_company_data.iloc[13, 11])
                days_to_expiration_long = int(solo_company_data.iloc[12, 11])
                days_to_expiration_long_return = (
                    int(solo_company_data.iloc[12, 11]) - days_to_expiration_short
                )

                number_positions = abs(float(solo_company_data.iloc[6, 11]))

                print("current_price", current_price)
                print("put_long_strike", put_long_strike)
                print("put_short_strike", put_short_strike)
                print("put_long_price", put_long_price)
                print("put_short_price", put_short_price)
                print("hv", hv)
                print("sigma_short", sigma_short)
                print("sigma_long", sigma_long)
                print("days_to_expiration_short", days_to_expiration_short)
                print("days_to_expiration_long", days_to_expiration_long)

                proba_50, avg_dtc = get_proba_50_calendar(
                    current_price,
                    yahoo_data,
                    put_long_strike,
                    put_long_price,
                    put_short_strike,
                    put_short_price,
                    sigma_short,
                    sigma_long,
                    days_to_expiration_short,
                    days_to_expiration_long,
                )

                print("proba_50", proba_50)
                expected_return = expected_return_calc(
                    sigma_short/100,
                    sigma_long/100,
                    current_price,
                    hv,
                    days_to_expiration_short,
                    days_to_expiration_long_return,
                    put_long_strike,
                    put_short_strike,
                    put_long_price,
                    put_short_price,
                )

                print("expected_return", expected_return)
                print("pop_30", proba_50)
                print("avg_dtc", avg_dtc[0])

                solo_company_data_formula.iloc[
                    8, 3
                ] = proba_50  # заполняем поле в таблице
                solo_company_data_formula.iloc[7, 3] = int(
                    avg_dtc[0]
                )  # заполняем поле в таблице
                solo_company_data_formula.iloc[3, 3] = (
                    expected_return * number_positions
                )  # заполняем поле в таблице

                worksheet_df_FORMULA_sum = pd.concat(
                    [worksheet_df_FORMULA_sum, solo_company_data_formula]
                )
                print("=================================")
            print(worksheet_df_FORMULA_sum)

            worksheet_df_FORMULA_sum = worksheet_df_FORMULA_sum.fillna("'")
            # # # ===================================  запись в таблицу ================================================
            worksheet.update(
                "A1",
                worksheet_df_FORMULA_sum.values.tolist(),
                value_input_option="USER_ENTERED",
            )
