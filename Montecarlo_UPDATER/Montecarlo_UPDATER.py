import pandas as pd
import numpy as np
import scipy.stats as stats
import datetime
import time
from dateutil.relativedelta import relativedelta
import yfinance as yf
import os
import gspread as gd
from popoption.ShortPut import shortPut
from popoption.ShortCall import shortCall
from popoption.ShortStrangle import shortStrangle

pd.options.mode.chained_assignment = None


def get_proba_50_put(row, yahoo_data):
    tick = row["Тикер"]
    current_price = yahoo_data[tick]["Close"].iloc[-1]
    yahoo_stock = yahoo_data[tick]
    short_strike = row["STRIKE шорт"]
    short_price = row["Текущая премия шорт"]
    rate = 4.6
    sigma = row["IV short"] * 100
    days_to_expiration = row["Осталось дней до закрытия"]
    closing_days_array = [row["Осталось дней до закрытия"]]
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
        yahoo_stock,
    )

    return proba_50


def get_proba_50_call(row, yahoo_data):
    tick = row["Тикер"]
    current_price = yahoo_data[tick]["Close"].iloc[-1]
    yahoo_stock = yahoo_data[tick]
    short_strike = row["STRIKE шорт"]
    short_price = row["Текущая премия шорт"]
    rate = 4.6
    sigma = row["IV short"] * 100
    days_to_expiration = row["Осталось дней до закрытия"]
    closing_days_array = [row["Осталось дней до закрытия"]]
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
        yahoo_stock,
    )
    return proba_50


def get_proba_50_strangle(row, yahoo_data):
    tick = row["Тикер"]
    yahoo_stock = yahoo_data[tick]
    current_price = yahoo_data[tick]["Close"].iloc[-1]
    call_short_strike = row["STRIKE CALL"]
    put_short_strike = row["STRIKE PUT"]
    call_short_price = row["Текущая премия колла"]
    put_short_price = row["Текущая премия пута"]
    rate = 4.6
    sigma = ((row["IV call"] + row["IV put"]) / 2) * 100
    days_to_expiration = row["Осталось дней до экспирации"]
    closing_days_array = [row["Осталось дней до экспирации"]]
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
        yahoo_stock,
    )
    return proba_50


if __name__ == "__main__":
    tables = [
        "SAXO_long_Naked_PUT",
        "SAXO_SHORT_NAKED_CALL",
        "STRANGL",
    ]  # , "SAXO_SHORT_NAKED_CALL"

    for table_name in tables:
        # # ================ раббота с таблицей============================================
        gc = gd.service_account(filename="Seetus.json")
        worksheet = gc.open("IBKR").worksheet(table_name)
        worksheet_df = pd.DataFrame(worksheet.get_all_records()).replace("", np.nan)
        print(f"==========  {table_name}  ===========")
        tickers_list = worksheet_df["Тикер"].values.tolist()
        worksheet_df_FORMULA = pd.DataFrame(
            worksheet.get_all_records(value_render_option="FORMULA")
        ).replace("", np.nan)

        # print("worksheet_df_FORMULA")
        # print(worksheet_df_FORMULA)

        yahoo_data = yf.download(tickers_list, group_by="ticker").dropna(
            axis=1, how="all"
        )
        yahoo_data.index = pd.to_datetime(yahoo_data.index)

        for i, row in worksheet_df.iterrows():
            try:
                tick = row["Тикер"]
                # скользящий тренд
                print(tick)
                print(yahoo_data[tick])
                if table_name == "SAXO_long_Naked_PUT":
                    montecarlo_touch = get_proba_50_put(row, yahoo_data)
                elif table_name == "SAXO_SHORT_NAKED_CALL":
                    montecarlo_touch = get_proba_50_call(row, yahoo_data)
                elif table_name == "STRANGL":
                    montecarlo_touch = get_proba_50_strangle(row, yahoo_data)
                worksheet_df_FORMULA["Montecarlo 50% touch"].iloc[i] = montecarlo_touch
            except:
                worksheet_df_FORMULA["Montecarlo 50% touch"].iloc[i] = "ERROR"
                pass

        worksheet_df_FORMULA = worksheet_df_FORMULA.fillna("'")
        # # # ===================================  запись в таблицу ================================================
        worksheet.update(
            "A1",
            [worksheet_df_FORMULA.columns.values.tolist()]
            + worksheet_df_FORMULA.values.tolist(),
            value_input_option="USER_ENTERED",
        )
