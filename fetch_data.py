import requests
import pandas as pd
import os
from dotenv import load_dotenv

# Alpha Vantage API key
load_dotenv()
API_KEY = os.getenv("ALPHA_API_KEY")
BASE_URL = "https://www.alphavantage.co/query"

def fetch_intraday(symbol="AAPL", interval ="60min", outputsize="full"):
    params = {
        "function": "TIME_SERIES_INTRADAY",
        "symbol": symbol,
        "interval": interval,
        "apikey": API_KEY,
        "outputsize": outputsize
    }
    response = requests.get(BASE_URL, params = params)
    data = response.json()
    time_series_key = next((key for key in data if "Time Series" in key), None)
    if not time_series_key or time_series_key not in data:
        print("Error: Could not find time series data in response:")
        print(data)
        return None

    # extract + format
    time_series_key = next((key for key in data if "Time Series" in key), None)
    df = pd.DataFrame.from_dict(data[time_series_key], orient="index")
    df = df.astype(float)
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)
    df = df.between_time("09:30", "16:00")
    return df

if __name__ == "__main__":
    df = fetch_intraday("MSFT")
    print(df.head())