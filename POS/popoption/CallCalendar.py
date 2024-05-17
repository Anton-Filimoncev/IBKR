from numba import jit
from .MonteCarloCALENDAR import monteCarlo
from .MonteCarloCALENDAR_RETURN import monteCarlo_return
import time
from .BlackScholes import blackScholesCall
import numpy as np


def bsm_debit(sim_price, strikes, rate, time_fraction_short, time_fraction_long, sigma_short, sigma_long, short_count,
              long_count):
    P_short_cals = blackScholesCall(sim_price, strikes[0], rate, time_fraction_short, sigma_short)
    P_long_cals = blackScholesCall(sim_price, strikes[1], rate, time_fraction_long, sigma_long)

    debit = (P_long_cals*long_count) - (P_short_cals*short_count)

    return debit


def callCalendar(underlying, sigma_short, sigma_long, rate, trials, days_to_expiration_short,
                days_to_expiration_long, closing_days_array, percentage_array, call_long_strike,
                call_long_price, call_short_strike, call_short_price, yahoo_stock, short_count, long_count):
    # Data Verification
    # if call_long_price <= call_short_price:
    #     raise ValueError("Long price cannot be less than or equal to Short price")
    #
    # # if short_strike >= long_strike:
    # #     raise ValueError("Short strike cannot be greater than or equal to Long strike")
    #
    # for closing_days in closing_days_array:
    #     if closing_days > days_to_expiration_short:
    #         raise ValueError("Closing days cannot be beyond Days To Expiration.")

    if len(closing_days_array) != len(percentage_array):
        raise ValueError("closing_days_array and percentage_array sizes must be equal.")

    # SIMULATION
    initial_debit = abs((call_long_price*long_count) - (call_short_price*short_count))  # Debit paid from opening trade
    # initial_credit = -1 * initial_debit
    initial_credit = (call_short_price*short_count) - (call_long_price*long_count)
    max_profit = initial_debit
    percentage_type = 'Initial'

    if short_count > long_count:
        max_profit = (0.2 * call_short_strike) * (short_count-long_count)
        percentage_type = 'Margin'
        print('Margin!!!!!!!')

    percentage_array = [x / 100 for x in percentage_array]

    min_profit = [max_profit * x for x in percentage_array]

    strikes = [call_short_strike, call_long_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_days_array = np.array(closing_days_array)
    min_profit = np.array(min_profit)

    try:
        pop, pop_error, avg_dtc, avg_dtc_error, cvar = monteCarlo(underlying, rate, sigma_short, sigma_long,
                                                            days_to_expiration_short, days_to_expiration_long,
                                                            closing_days_array, trials, initial_credit, min_profit,
                                                            strikes, bsm_debit, yahoo_stock, short_count, long_count)
    except RuntimeError as err:
        print(err.args)

    expected_profit = monteCarlo_return(underlying, rate, sigma_short, sigma_long,
                                                            days_to_expiration_short, days_to_expiration_long,
                                                            closing_days_array, trials, initial_credit, min_profit,
                                                            strikes, bsm_debit, yahoo_stock, short_count, long_count)


    response = {
        "pop": pop,
        'cvar': cvar,
        'exp_return': expected_profit,
        "pop_error": pop_error,
        "avg_dtc": avg_dtc,
        "avg_dtc_error": avg_dtc_error
    }

    return response
