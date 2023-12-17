from numba import jit
from .MonteCarlo_CALENDAR import monteCarlo
from .MonteCarloCALENDAR_RETURN import monteCarlo_return
import time
from .BlackScholes import blackScholesCall
import numpy as np


def bsm_debit(sim_price, strikes, rate, time_fraction_short, time_fraction_long, sigma_short, sigma_long):
    P_short_cals = blackScholesCall(sim_price, strikes[0], rate, time_fraction_short, sigma_short)
    P_long_cals = blackScholesCall(sim_price, strikes[1], rate, time_fraction_long, sigma_long)

    credit = P_long_cals - P_short_cals
    debit = P_long_cals - P_short_cals
    # debit = P_long_puts - P_short_puts

    return debit


def callCalendar(underlying, sigma_short, sigma_long, rate, trials, days_to_expiration_short,
                days_to_expiration_long, closing_days_array, percentage_array, call_long_strike,
                call_long_price, call_short_strike, call_short_price, yahoo_stock):
    # Data Verification
    if call_long_price <= call_short_price:
        raise ValueError("Long price cannot be less than or equal to Short price")

    # if short_strike >= long_strike:
    #     raise ValueError("Short strike cannot be greater than or equal to Long strike")

    for closing_days in closing_days_array:
        if closing_days > days_to_expiration_short:
            raise ValueError("Closing days cannot be beyond Days To Expiration.")

    if len(closing_days_array) != len(percentage_array):
        raise ValueError("closing_days_array and percentage_array sizes must be equal.")

    # SIMULATION
    initial_debit = call_long_price - call_short_price  # Debit paid from opening trade
    # initial_credit = -1 * initial_debit
    initial_credit = call_short_price - call_long_price

    percentage_array = [x / 100 for x in percentage_array]
    max_profit = initial_debit
    min_profit = [max_profit * x for x in percentage_array]

    strikes = [call_short_strike, call_long_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_days_array = np.array(closing_days_array)
    min_profit = np.array(min_profit)

    try:
        pop, pop_error, avg_dtc, avg_dtc_error = monteCarlo(underlying, rate, sigma_short, sigma_long,
                                                            days_to_expiration_short, days_to_expiration_long,
                                                            closing_days_array, trials, initial_credit, min_profit,
                                                            strikes, bsm_debit, yahoo_stock)
    except RuntimeError as err:
        print(err.args)

    # expected_profit = monteCarlo_return(underlying, rate, sigma_short, sigma_long,
    #                                                         days_to_expiration_short, days_to_expiration_long,
    #                                                         closing_days_array, trials, initial_credit, min_profit,
    #                                                         strikes, bsm_debit, yahoo_stock)


    response = {
        "pop": pop,
         "pop_error": pop_error,
        "avg_dtc": avg_dtc,
        "avg_dtc_error": avg_dtc_error
    }
    print(response)

    return pop[0] / 100, avg_dtc
