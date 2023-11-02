# IBKR

$$$      BULL_PUT_VERTICAL      $$$
Updating google sheet for VERTICAL BULL PUT position, with some parameters:
-- Probable statistical income (Вероятный статистический доход)


$$$      CREDIT STRADDL      $$$
Updating google sheet for CREDIT STRADDL position, with some parameters:
-- Trend 
    if current_price > SMA_100 and current_price > SMA_20 and SMA_20 > SMA_100:
        trend = 'Strong Uptrend'
    if current_price > SMA_100 and current_price > SMA_20 and SMA_20 < SMA_100:
        trend = 'Uptrend'
    if current_price > SMA_100 and current_price < SMA_20 and SMA_20:
        trend = 'Weak Uptrend'
    if current_price < SMA_100 and current_price < SMA_20 and SMA_20 < SMA_100:
        trend = 'Strong Downtrend'
    if current_price < SMA_100 and current_price < SMA_20 and SMA_20 > SMA_100:
        trend = 'Downtrend'
    if current_price < SMA_100 and current_price > SMA_20:
        trend = 'Weak downtrend'
-- Imply Volatility PERCENTILE


$$$      ETF      $$$
Updating google sheet for VERTICAL BULL PUT position, with some parameters:
-- Probable statistical income (Вероятный статистический доход)
