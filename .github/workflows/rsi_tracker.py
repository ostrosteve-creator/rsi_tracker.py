
import yfinance as yf
import pandas as pd

# Tickers you care about
TICKERS = ["SMH", "SOXX", "INTC", "NVDA", "AMD", "AVGO"]

# How much history to pull
PERIOD = "5y"

def calculate_rsi(prices, window=14):
    delta = prices.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.ewm(alpha=1/window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def signal_from_rsi(rsi):
    if rsi >= 90:
        return "🚨 EXTREME (historical danger zone)"
    elif rsi >= 85:
        return "Extreme / parabolic risk"
    elif rsi >= 75:
        return "Very overbought"
    elif rsi >= 70:
        return "Overbought"
    elif rsi <= 30:
        return "Oversold"
    else:
        return "Neutral"

rows = []

for ticker in TICKERS:
    try:
        data = yf.download(ticker, period=PERIOD, auto_adjust=True, progress=False)

        if data.empty:
            print(f"No data for {ticker}")
            continue

        daily_close = data["Close"]
        weekly_close = daily_close.resample("W-FRI").last()
        monthly_close = daily_close.resample("ME").last()

        daily_rsi = calculate_rsi(daily_close).iloc[-1]
        weekly_rsi = calculate_rsi(weekly_close).iloc[-1]
        monthly_rsi = calculate_rsi(monthly_close).iloc[-1]

        rows.append({
            "Ticker": ticker,
            "Daily RSI": round(float(daily_rsi), 2),
            "Weekly RSI": round(float(weekly_rsi), 2),
            "Monthly RSI": round(float(monthly_rsi), 2),
            "Signal": signal_from_rsi(monthly_rsi)
        })

        # 🔥 Your key alert (what you care about)
        if monthly_rsi >= 90:
            print(f"🚨 {ticker} MONTHLY RSI ABOVE 90 — EXTREME CONDITION")

    except Exception as e:
        print(f"Error processing {ticker}: {e}")

# Output results
results = pd.DataFrame(rows)
print("\n=== RSI SUMMARY ===")
print(results)

# Save to file (this is what GitHub uploads)
results.to_csv("rsi_output.csv", index=False)
