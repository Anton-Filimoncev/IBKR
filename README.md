# IBKR

# $$$      BULL_PUT_VERTICAL      $$$
Updating google sheet for VERTICAL BULL PUT position, with some parameters:
## Probable statistical income (Вероятный статистический доход)


# $$$      CREDIT STRADDL      $$$
Updating google sheet for CREDIT STRADDL position, with some parameters:
### Trend 
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
### Imply Volatility PERCENTILE


# $$$      ETF      $$$
Updating google sheet for ETF, with some parameters:
### Vega_risk (Interactive Broker)
### Imply Volatility Percentile (Interactive Broker)
### Imply VolatilityRegime (Interactive Broker)
### Imply VolatilityMedian (Interactive Broker)
### Imply Volatility (Interactive Broker)
### History Volatility 20 days (Interactive Broker)
### History Volatility 50 days
### History Volatility 100 days
### History Volatility Regime
### vertical_skew_call (Interactive Broker)
### vertical_skew_put (Interactive Broker)
### pcr_signal (Interactive Broker)
### max_pain_value (Interactive Broker)
### iv_horizontal (Interactive Broker)
