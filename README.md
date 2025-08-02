# Trading Bot

This project simulates algorithmic stock trading using technical indicators like **SMA** (Simple Moving Average) and **RSI** (Relative Strength Index). It allows for backtesting of strategies on real historical stock data using the Alpha Vantage API and evaluates performance using financial metrics.

## 📈 Features

- Real-time data fetching via [Alpha Vantage API](https://www.alphavantage.co/)
- SMA crossover strategy (short vs long window)
- RSI momentum filter
- Virtual trading with portfolio balance and share tracking
- Performance metrics: 
  - Final return
  - Max drawdown
  - Win rate
  - **Sharpe ratio**
- Visualizations:
  - Price with SMA signals
  - RSI plot
  - Portfolio value over time

## How It Works

1. Fetch intraday price data (default: `MSFT`, 60-minute candles)
2. Calculate SMA and RSI indicators
3. Generate buy/sell signals using crossover logic:
   - Buy when 20-SMA crosses above 50-SMA
   - Sell when 20-SMA crosses below 50-SMA
   - Optionally filter with RSI < 50 for stronger momentum
4. Simulate a portfolio with an initial balance of $10,000
5. Track and evaluate strategy performance


