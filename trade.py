import pandas as pd
import matplotlib.pyplot as plt
from fetch_data import fetch_intraday

#indicators
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
    sharpe_ratio = (avg_return /std_return) * (252*6) ** 0.5
    return sharpe_ratio

def calculate_ema(data, short_window=20, long_window=50):
    data['EMA_short'] = data['4. close'].ewm(span = short_window, adjust=False).mean()
    data['EMA_long'] = data['4. close'].ewm(span = long_window, adjust=False).mean()
    return data

# strat
def get_crossover_signals(data):
    buy = []
    sell = []
    for i in range(1, len(data)):
        prev_short = data['SMA'].iloc[i - 1]
        prev_long = data['SMA_50'].iloc[i - 1]
        curr_short = data['SMA'].iloc[i]
        curr_long = data['SMA_50'].iloc[i]
        if prev_short < prev_long and curr_short > curr_long:
            buy.append(data.index[i])
        elif prev_short > prev_long and curr_short < curr_long:
            sell.append(data.index[i])
    return buy, sell


#simulate portfolio
def portfolio(data, buy, sell, initial_balance=10000):
    balance = initial_balance
    shares = 0
    trade_log = []
    portfolio_values = []
    for time in data.index:
        price = data.loc[time, '4. close']
        if time in buy:
            shares = int(balance // price)
            cost = shares * price
            balance -= cost
            trade_log.append((time, 'buy', price, shares))
        elif time in sell and shares > 0:
            revenue = shares * price
            balance += revenue
            trade_log.append((time, 'sell', price, shares))
            shares = 0
        portfolio_value = balance + shares * price
        portfolio_values.append((time, portfolio_value))
    return trade_log, portfolio_values


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
    print(f"\nPortfolio Evaluation")
    print(f"Final Portfolio Value: ${final_value:,.2f}")
    print(f"Total Return: {total_return:.2f}%")
    print(f"Max Drawdown: {max_drawdown:.2f}%")
    print(f"Total Trades: {total_trades}")
    print(f"Win Rate: {win_rate:.2f}%\n")
    print(f"Sharpe Ratio: {sharpe:.2f}")


# viz
def plot_sma(data, symbol="MSFT", buy=[], sell=[]):
    plt.figure(figsize=(14, 6))
    plt.plot(data.index, data['4. close'], label='Close Price', color='black')
    plt.plot(data.index, data['SMA'], label='SMA (20)', color='blue')
    plt.plot(data.index, data['SMA_50'], label='SMA (50)', color='orange')
    plt.scatter(buy, data.loc[buy, '4. close'], marker='^', color='green', label='Buy Signal', s=100)
    plt.scatter(sell, data.loc[sell, '4. close'], marker='v', color='red', label='Sell Signal', s=100)
    plt.title(f"{symbol} Close Price with SMA Signals")
    plt.xlabel("date")
    plt.ylabel("price (USD)")
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
    symbol = "MSFT"
    df = fetch_intraday(symbol)
    if df is not None:
        df = calculate_sma(df)
        df = calculate_rsi(df)
        buy, sell = get_crossover_signals(df)
        print(f"buy signals: {len(buy)} | sell signals: {len(sell)}")
        trades, portfolio_values = portfolio(df, buy, sell)
        for entry in trades:
            print(entry)
        evaluate_portfolio(trades, portfolio_values, initial_balance=10000)
        plot_sma(df, symbol=symbol, buy=buy, sell=sell)
        plot_portfolio(portfolio_values)
        plot_rsi(df)
    else:
        print("couldn't fetch data.")


if __name__ == "__main__":
    main()
