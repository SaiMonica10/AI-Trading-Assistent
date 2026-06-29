import pandas as pd
import ta
from data.fetcher import get_stock_data


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    # --- Moving Averages ---
    # Average closing price over last 20 and 50 days
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()

    # --- RSI (Relative Strength Index) ---
    # Measures how fast price is rising or falling (0 to 100)
    # RSI > 70 = overbought (too hot, may fall), RSI < 30 = oversold (too low, may rise)
    df['RSI'] = ta.momentum.RSIIndicator(df['Close'], window=14).rsi()

    # --- MACD ---
    # Compares two EMAs (fast vs slow) to spot trend changes
    # When MACD line crosses above signal line = bullish
    macd = ta.trend.MACD(df['Close'])
    df['MACD'] = macd.macd()
    df['MACD_Signal'] = macd.macd_signal()
    df['MACD_Hist'] = macd.macd_diff()

    # --- Bollinger Bands ---
    # Upper/Lower bands = price range. If price touches upper band = overbought
    bb = ta.volatility.BollingerBands(df['Close'], window=20, window_dev=2)
    df['BB_Upper'] = bb.bollinger_hband()
    df['BB_Lower'] = bb.bollinger_lband()
    df['BB_Middle'] = bb.bollinger_mavg()

    # --- Volume Spike ---
    # If today's volume is 1.5x the 20-day average = unusual activity
    df['Volume_MA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Spike'] = df['Volume'] > (df['Volume_MA'] * 1.5)

    return df


def generate_signal(df: pd.DataFrame) -> dict:
    latest = df.iloc[-1]   # only look at today's (most recent) row
    signals = []
    score = 0              # positive = bullish, negative = bearish

    # --- RSI check ---
    if latest['RSI'] < 30:
        signals.append("RSI oversold - potential buy zone")
        score += 2
    elif latest['RSI'] > 70:
        signals.append("RSI overbought - potential sell zone")
        score -= 2
    else:
        signals.append(f"RSI neutral at {latest['RSI']:.1f}")

    # --- Moving Average trend check ---
    if latest['Close'] > latest['SMA_20'] > latest['SMA_50']:
        signals.append("Price above both MAs - uptrend")
        score += 2
    elif latest['Close'] < latest['SMA_20'] < latest['SMA_50']:
        signals.append("Price below both MAs - downtrend")
        score -= 2
    else:
        signals.append("Mixed MA signals - no clear trend")

    # --- MACD check ---
    if latest['MACD'] > latest['MACD_Signal']:
        signals.append("MACD bullish - momentum increasing")
        score += 1
    else:
        signals.append("MACD bearish - momentum weakening")
        score -= 1

    # --- Volume spike check ---
    if latest['Volume_Spike']:
        signals.append("Volume spike - strong move with conviction")

    # --- Final verdict ---
    if score >= 3:
        verdict = "BULLISH"
    elif score <= -3:
        verdict = "BEARISH"
    else:
        verdict = "NEUTRAL"

    return {
        "verdict": verdict,
        "score": score,
        "signals": signals,
        "rsi": round(latest['RSI'], 2),
        "close": round(latest['Close'], 2),
        "sma_20": round(latest['SMA_20'], 2),
        "sma_50": round(latest['SMA_50'], 2),
    }


if __name__ == "__main__":
    symbol = "RELIANCE.NS"
    print(f"Fetching data for {symbol}...\n")

    df = get_stock_data(symbol, period="6mo")
    df = add_indicators(df)

    print("=== Last 5 rows with indicators ===")
    print(df[['Close', 'SMA_20', 'SMA_50', 'RSI', 'MACD', 'Volume_Spike']].tail(5))

    print("\n=== Signal Analysis ===")
    signal = generate_signal(df)
    print(f"Verdict  : {signal['verdict']}  (score: {signal['score']})")
    print(f"Price    : Rs.{signal['close']}")
    print(f"RSI      : {signal['rsi']}")
    print(f"SMA 20   : Rs.{signal['sma_20']}")
    print(f"SMA 50   : Rs.{signal['sma_50']}")
    print("\nSignals detected:")
    for s in signal['signals']:
        print(f"  - {s}")
