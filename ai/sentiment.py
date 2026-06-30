import os
import requests
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")


def get_news(company_name: str) -> list[str]:
    """Fetch real news headlines for a company using GNews API."""
    api_key = os.getenv("GNEWS_API_KEY")
    url = (
        f"https://gnews.io/api/v4/search"
        f"?q={company_name}&lang=en&max=5&token={api_key}"
    )
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        articles = data.get("articles", [])
        return [a["title"] for a in articles]
    except Exception:
        return ["No news available at the moment."]


def analyze_with_ai(symbol: str, company_name: str, signal: dict, headlines: list[str]) -> str:
    """Send stock data + news to Gemini and get a plain-English summary."""

    headlines_text = "\n".join([f"- {h}" for h in headlines]) if headlines else "No news available."

    prompt = f"""You are a stock research analyst. Analyze this data and give a clear, beginner-friendly research summary.

STOCK: {company_name} ({symbol})
CURRENT PRICE: Rs.{signal['close']}
TECHNICAL VERDICT: {signal['verdict']} (score: {signal['score']})
RSI: {signal['rsi']}

TECHNICAL SIGNALS:
{chr(10).join(signal['signals'])}

RECENT NEWS HEADLINES:
{headlines_text}

Provide:
1. Overall Outlook (1 sentence)
2. Key Strengths (2-3 bullet points)
3. Key Risks (2-3 bullet points)
4. Sentiment from News (positive/negative/mixed with brief reason)
5. Bottom Line (1-2 sentences for a retail investor)

Keep it simple. No jargon. Do not use special characters or symbols."""

    response = model.generate_content(prompt)
    return response.text


if __name__ == "__main__":
    from data.fetcher import get_stock_data
    from analysis.indicators import add_indicators, generate_signal

    symbol = "RELIANCE.NS"
    company_name = "Reliance Industries"

    print(f"Fetching data for {symbol}...")
    df = get_stock_data(symbol, period="6mo")
    df = add_indicators(df)
    signal = generate_signal(df)

    print("Fetching news headlines...")
    headlines = get_news(company_name)

    print("\n=== News Headlines ===")
    for h in headlines:
        print(f"  - {h}")

    print("\n=== AI Research Summary ===\n")
    summary = analyze_with_ai(symbol, company_name, signal, headlines)
    print(summary)
