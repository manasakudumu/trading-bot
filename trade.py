import pandas as pd
import matplotlib.pyplot as plt
from fetch_data import fetch_intraday
from strategies.sma_crossover import sma_crossover_strategy
from strategies.ema_crossover import ema_crossover_strategy
import argparse
import logging 


parser = argparse.ArgumentParser(description="Backtest SMA/EMA strategy on a stock.")
parser.add_argument("--symbol",        type=str,   required=True)
parser.add_argument("--strategy",     choices=["sma","ema","both"], default="both")
parser.add_argument("--stoploss",     type=float, default=0.05, help="Stop-loss %")
parser.add_argument("--no-stoploss",  action="store_true", help="Disable stop-loss")
parser.add_argument("--trailing",     action="store_true", help="Enable trailing stop")
parser.add_argument("--initial",      type=float, default=10000)
args = parser.parse_args()

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

#  calculate strategies
def calculate_sma(data, window=20):
    data['SMA'] = data['4. close'].rolling(window=window).mean()
    data['SMA_50'] = data['4. close'].rolling(window=50).mean()
    return data

def calculate_rsi(data, window=20):
    delta = data['4. close'].diff()
    gain = delta.where(delta > 0, 0).rolling(window).mean()
    loss = -delta.where(delta < 0, 0).rolling(window).mean()
    rs = gain / loss
    data['RSI'] = 100 - (100 / (1 + rs))
    return data

def calculate_sharpe(portfolio_values):
    values = pd.Series([val for _, val in portfolio_values])
    returns = values.pct_change().dropna()
    avg_return = returns.mean()
    std_return = returns.std()
    sharpe_ratio = (avg_return / std_return) * (252 * 6) ** 0.5
    return sharpe_ratio

# calculate exponential moving averages
def calculate_ema(data, short_window=20, long_window=50):
    data['EMA_short'] = data['4. close'].ewm(span=short_window, adjust=False).mean()
    data['EMA_long'] = data['4. close'].ewm(span=long_window, adjust=False).mean()
    return data

# # Generate SMA crossover signals
# def get_crossover_signals(data):
#     buy = []
#     sell = []
#     for i in range(1, len(data)):
#         prev_short = data['SMA'].iloc[i - 1]
#         prev_long = data['SMA_50'].iloc[i - 1]
#         curr_short = data['SMA'].iloc[i]
#         curr_long = data['SMA_50'].iloc[i]
#         if prev_short < prev_long and curr_short > curr_long:
#             buy.append(data.index[i])
#         elif prev_short > prev_long and curr_short < curr_long:
#             sell.append(data.index[i])
#     return buy, sell

# simulate portfolio with stop-loss
def portfolio(data, buy, sell, initial_balance=10000, stop_loss=0.01, enable_stop=True,trailing=False):
    balance = initial_balance
    shares = 0
    trade_log = []
    portfolio_values = []
    stop_price = None
    for t in data.index:
        price = data.at[t, "4. close"]
        if t in buy:
            shares = int(balance // price)
            balance -= shares * price
            trade_log.append((t, "buy", price, shares))
            if enable_stop:
                stop_price = price * (1 - stop_loss)
        elif t in sell and shares > 0:
            balance += shares * price
            trade_log.append((t, "sell", price, shares))
            shares = 0
            stop_price = None
        elif enable_stop and shares > 0 and stop_price is not None:
            if trailing:
                stop_price = max(stop_price, price * (1 - stop_loss))
            if price < stop_price:
                logger.info(f"Stop-loss triggered at {t}: exited at {price:.2f}")
                balance += shares * price
                trade_log.append((t, "stop_loss", price, shares))
                shares = 0
                stop_price = None
        portfolio_values.append((t, balance + shares * price))
    return trade_log, portfolio_values

# evaluate portfolio performance
def evaluate_portfolio(trades, portfolio_values, initial_balance):
    final_value = portfolio_values[-1][1]
    total_return = (final_value - initial_balance) / initial_balance * 100
    portfolio_series = pd.Series([val for _, val in portfolio_values])
    peak = portfolio_series.cummax()
    drawdown = (portfolio_series - peak) / peak
    max_drawdown = drawdown.min() * 100
    wins = 0
    losses = 0
    for i in range(1, len(trades), 2):
        buy_price = trades[i - 1][2]
        sell_price = trades[i][2]
        if sell_price > buy_price:
            wins += 1
        else:
            losses += 1
    total_trades = wins + losses
    win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0
    sharpe = calculate_sharpe(portfolio_values)
    print("\nPortfolio Evaluation")
    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%\n")
    print(f"Sharpe Ratio: {sharpe:.2f}")

# plot strategy buy/sell signals
def plot_strategy_signals(data, symbol, buy, sell, strategy_name="Strategy"):
    plt.figure(figsize=(14, 6))
    plt.plot(data.index, data['4. close'], label='Close Price', color='black')
    plt.scatter(buy, data.loc[buy, '4. close'], marker='^', color='green', label='Buy Signal', s=100)
    plt.scatter(sell, data.loc[sell, '4. close'], marker='v', color='red', label='Sell Signal', s=100)
    plt.title(f"{symbol} Close Price with {strategy_name} Signals")
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_portfolio(portfolio_values):
    times, values = zip(*portfolio_values)
    plt.figure(figsize=(12, 5))
    plt.plot(times, values, label='Portfolio Value ($)', color='purple')
    plt.title("Simulated Portfolio Value Over Time")
    plt.xlabel("Date")
    plt.ylabel("USD")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_rsi(data):
    plt.figure(figsize=(12, 3))
    plt.plot(data.index, data['RSI'], label='RSI', color='purple')
    plt.axhline(70, linestyle='--', color='red', alpha=0.5, label='overbought (70)')
    plt.axhline(30, linestyle='--', color='green', alpha=0.5, label='oversold (30)')
    plt.title("RSI indicator")
    plt.xlabel("date")
    plt.ylabel("RSI")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    symbol = args.symbol.upper()
    strategy = args.strategy.lower()
    stop_loss_pct = args.stoploss
    initial_balance = args.initial

    print(f"\n{symbol}")
    df = fetch_intraday(symbol)
    if df is None:
        print(f"couldn't fetch data for {symbol}")
        return
    df = calculate_sma(df)
    df = calculate_ema(df)
    df = calculate_rsi(df)
    if strategy in ["sma", "both"]:
        print("\nSMA crossover strategy")
        sma_buy, sma_sell = sma_crossover_strategy(df)
        sma_trades, sma_portfolio = portfolio(df, sma_buy, sma_sell, initial_balance, stop_loss_pct)
        evaluate_portfolio(sma_trades, sma_portfolio, initial_balance)
        plot_strategy_signals(df, symbol, sma_buy, sma_sell, strategy_name="SMA Crossover")
        plot_portfolio(sma_portfolio)
    if strategy in ["ema", "both"]:
        print("\nEMA crossover strategy")
        ema_buy, ema_sell = ema_crossover_strategy(df)
        ema_trades, ema_portfolio = portfolio(df, ema_buy, ema_sell, initial_balance, stop_loss_pct)
        evaluate_portfolio(ema_trades, ema_portfolio, initial_balance)
        plot_strategy_signals(df, symbol, ema_buy, ema_sell, strategy_name="EMA Crossover")
        plot_portfolio(ema_portfolio)

    plot_rsi(df)

if __name__ == "__main__":
    main()