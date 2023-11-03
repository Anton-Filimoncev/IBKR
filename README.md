# IBKR

# $$$      BULL_PUT_VERTICAL      $$$
Updating google sheet for VERTICAL BULL PUT position, with some parameters:
## Probable statistical return (Вероятный статистический доход)


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
### Vega Risk (Interactive Broker)
### Imply Volatility Percentile (Interactive Broker)
### Imply VolatilityRegime (Interactive Broker)
### Imply VolatilityMedian (Interactive Broker)
### Imply Volatility (Interactive Broker)
### History Volatility 20 days (Interactive Broker)
### History Volatility 50 days
### History Volatility 100 days
### History Volatility Regime
### Vertical Skew Call (Interactive Broker)
### Vertical Skew Put (Interactive Broker)
### PCR Signal (Interactive Broker)
### MAX Pain Value (Interactive Broker)
### Imply Volatility Horizontal Skew (Interactive Broker)


# $$$      EXPECTED RETURN ETF STRANGL      $$$
Updating google sheet for EXPECTED RETURN ETF STRANGL position, with some parameters:
### Probable statistical return calculated by generated stock price between -50% and +100% prise in increments 10 cents

# $$$      IBRK_SCREENER      $$$
Updating google sheet for DIAGONAL BULL SPREAD, SCREW STRANGL, SHORT VERTICAL PUT SPREAD position, with some parameters:
### DIAGONAL BULL SPREAD
'Max_Pain'
'Margin'
'Rxpected_Return'
'ROI_Day'
'Rxpected_Return_Percent'
'Hist_Volatility'
'Hist_Vol_Stage'
'IV_Percentile'
'IV_Stage'
'Reward_Risk'
'PCR_Signal'
'Trend'
'Liquidity_Short'
'Liquidity_Long'
'RSI'
