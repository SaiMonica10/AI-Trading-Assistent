import yfinance as yf
import pandas as pd

def get_stock_data(symbol: str, period: str = "6mo") -> pd.DataFrame:
    """
    Fetch historical OHLCV data for a stock.
    period options: 1mo, 3mo, 6mo, 1y, 2y.
    """
    ticker = yf.Ticker(symbol)
    df = ticker.history(period=period)
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]
    df.index = pd.to_datetime(df.index)
    return df

def get_stock_info(symbol: str) -> dict:
    """Get company name, sector, market cap."""
    ticker = yf.Ticker(symbol)
    info = ticker.info
    return {
        "name": info.get("longName", symbol),
        "sector": info.get("sector", "Unknown"),
        "market_cap": info.get("marketCap", 0),
        "pe_ratio": info.get("trailingPE", None),
        "52w_high": info.get("fiftyTwoWeekHigh", None),
        "52w_low": info.get("fiftyTwoWeekLow", None),
    }

# Test it
if __name__ == "__main__":
    df = get_stock_data("RELIANCE.NS")   # .NS = NSE India
    print(df.tail(10))
    print(get_stock_info("RELIANCE.NS"))