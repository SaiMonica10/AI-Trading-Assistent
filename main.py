import sys
from data.fetcher import get_stock_data, get_stock_info
from analysis.indicators import add_indicators, generate_signal
from ai.sentiment import get_news, analyze_with_ai


def run(symbol: str, period: str = "6mo"):
    print(f"\nAnalyzing {symbol}...\n")

    # Step 1 - Fetch price data
    df = get_stock_data(symbol, period)
    info = get_stock_info(symbol)

    # Step 2 - Calculate indicators and signal
    df = add_indicators(df)
    signal = generate_signal(df)

    # Step 3 - Fetch news and get AI summary
    headlines = get_news(info["name"])
    summary = analyze_with_ai(symbol, info["name"], signal, headlines)

    # Print results
    print("=" * 50)
    print(f"  {info['name']} ({symbol})")
    print(f"  Sector : {info['sector']}")
    print(f"  Price  : Rs. {signal['close']}")
    print(f"  Signal : {signal['verdict']}  (score: {signal['score']})")
    print(f"  RSI    : {signal['rsi']}")
    print(f"  SMA 20 : Rs. {signal['sma_20']}")
    print(f"  SMA 50 : Rs. {signal['sma_50']}")
    print("=" * 50)

    print("\nTechnical Signals:")
    for s in signal["signals"]:
        print(f"  - {s}")

    print("\nRecent News:")
    for h in headlines:
        print(f"  - {h}")

    print("\nAI Research Summary:")
    print("-" * 50)
    print(summary)
    print("-" * 50)


if __name__ == "__main__":
    # Default symbol, or pass one as argument: python main.py INFY.NS
    symbol = sys.argv[1] if len(sys.argv) > 1 else "RELIANCE.NS"
    run(symbol)
