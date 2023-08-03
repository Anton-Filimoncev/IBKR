from ETF_table_UPDATER_TECH import *
from ETF_table_UPDATER_STRATEGIST import *
from ETF_table_UPDATER_MARKET_DATA import *
from ETF_table_UPDATER_IB import *
from ETF_table_UPDATER_GURU import *

# TREND,
# RSI,
# SMA 20,
# SMA 100
print('run_tech')
# run_tech()


# O_S WEIGHT PCR SIGNAL,
# O_S Plot Link,
# IV O_S
print('run_strategist')
# run_strategist()


# MAX PAIN month,
# WEIGHT PCR SIGNAL,
# WEIGHT PCR sparkline
print('run_market_data')
start_row = 0 # начать со строки - номер строки в таблице+2
run_market_data(start_row) # для проверки MAX PAIN заменить: max_pain_check=True


# VEGA RISK month
# IV % year, IV DIA year, IV median 6 m, IV ATM,
# HV 20, HV 50, HV 100, HV DIA
# Horizontal scew (IV 1 month - 2 month)
print('run_ib')
# start_row = 0 # начать со строки - номер строки в таблице+2
# run_ib(start_row)


# Dividend Yield
# Dividend Yield Median
print('run_guru')
# start_row = 0 # начать со строки - номер строки в таблице+2
# run_guru(start_row)