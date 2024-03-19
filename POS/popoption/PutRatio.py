from numba import jit
from .MonteCarloRATIO import monteCarlo
from .MonteCarloRATIO_RETURN import monteCarlo_return
import time
from .BlackScholes import blackScholesPut
import numpy as np


def bsm_debit(sim_price, strikes, rate, time_fraction, sigma_long, sigma_short1, sigma_short2):
    P_short_puts1 = blackScholesPut(sim_price, strikes[0], rate, time_fraction, sigma_short1)
    P_short_puts2 = blackScholesPut(sim_price, strikes[1], rate, time_fraction, sigma_short2)
    P_long_puts = blackScholesPut(sim_price, strikes[2], rate, time_fraction, sigma_long)

    debit = P_long_puts - (P_short_puts1 + P_short_puts2)
    # debit = P_long_puts - P_short_puts

    return debit


def putRatio(underlying, sigma_long, sigma_short1, sigma_short2, rate, trials, days_to_expiration, closing_days_array,
        percentage_array, put_long_strike, put_short_strike1, put_short_strike2, total_prime, yahoo_stock,):

    if len(closing_days_array) != len(percentage_array):
        raise ValueError("closing_days_array and percentage_array sizes must be equal.")

    # SIMULATION
    initial_debit = total_prime  # Debit paid from opening trade
    # initial_credit = -1 * initial_debit
    initial_credit = total_prime

    percentage_array = [x / 100 for x in percentage_array]
    max_profit = initial_debit
    min_profit = [max_profit * x for x in percentage_array]

    strikes = [put_short_strike1, put_short_strike2, put_long_strike]

    # LISTS TO NUMPY ARRAYS CUZ NUMBA HATES LISTS
    strikes = np.array(strikes)
    closing_days_array = np.array(closing_days_array)
    min_profit = np.array(min_profit)

    try:
        pop, pop_error, avg_dtc, avg_dtc_error, cvar = monteCarlo(underlying, rate, sigma_long, sigma_short1, sigma_short2,
                                                            days_to_expiration,
                                                            closing_days_array, trials, initial_credit, min_profit,
                                                            strikes, bsm_debit, yahoo_stock)
    except RuntimeError as err:
        print(err.args)

    expected_profit = monteCarlo_return(underlying, rate, sigma_long, sigma_short1, sigma_short2,
                                                            days_to_expiration,
                                                            closing_days_array, trials, initial_credit, min_profit,
                                                            strikes, bsm_debit, yahoo_stock)

    response = {
        "pop": pop,
        'cvar': cvar,
        'exp_return': expected_profit,
        "pop_error": pop_error,
        "avg_dtc": avg_dtc,
        "avg_dtc_error": avg_dtc_error
    }

    return pop[0] / 100, cvar*100, expected_profit*100
