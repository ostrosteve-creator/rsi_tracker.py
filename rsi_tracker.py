import yfinance as yf
import pandas as pd

TICKERS = ["SMH", "SOXX", "INTC", "NVDA", "AMD", "AVGO"]
PERIOD = "5y"

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1 / window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, adjust=False).mean()

    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def signal_from_rsi(rsi):
    if rsi >= 90:
        return "EXTREME historical danger zone"
    elif rsi >= 85:
        return "Extreme / parabolic risk"
    elif rsi >= 75:
        return "Very overbought"
    elif rsi >= 70:
        return "Overbought"
    elif rsi <= 30:
        return "Oversold"
    return "Neutral"

rows = []

for ticker in TICKERS:
    print(f"Downloading {ticker}...")

    data = yf.download(ticker, period=PERIOD, auto_adjust=True, progress=False)

    if data.empty:
        print(f"No data returned for {ticker}")
        continue

    close = data["Close"]

    # Fix if yfinance returns a weird 2D column
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]

    daily_rsi = calculate_rsi(close).dropna()
    weekly_rsi = calculate_rsi(close.resample("W-FRI").last()).dropna()
    monthly_rsi = calculate_rsi(close.resample("M").last()).dropna()

    if daily_rsi.empty or weekly_rsi.empty or monthly_rsi.empty:
        print(f"Not enough RSI data for {ticker}")
        continue

    rows.append({
        "Ticker": ticker,
        "Daily RSI": round(float(daily_rsi.iloc[-1]), 2),
        "Weekly RSI": round(float(weekly_rsi.iloc[-1]), 2),
        "Monthly RSI": round(float(monthly_rsi.iloc[-1]), 2),
        "Signal": signal_from_rsi(float(monthly_rsi.iloc[-1]))
    })

results = pd.DataFrame(rows)

print("\n=== RSI SUMMARY ===")
print(results)
print("Rows collected:", len(rows))

results.to_csv("rsi_output.csv", index=False)
print("Saved rsi_output.csv")
