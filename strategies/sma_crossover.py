def sma_crossover_strategy(data):
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
