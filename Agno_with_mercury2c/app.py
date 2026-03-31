import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import yfinance as yf
from ddgs import DDGS

from agno.agent import Agent

# Load environment variables
load_dotenv()

# Mercury 2 client (OpenAI-compatible)
client = OpenAI(
    api_key=os.getenv("INCEPTION_API_KEY"),
    base_url="https://api.inceptionlabs.ai/v1",
)

# -----------------------------
# Custom tool 1: Stock data
# -----------------------------
def get_stock_data(ticker: str) -> str:
    """Fetch stock price, company info, and analyst recommendations for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        company_data = {
            "ticker": ticker,
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice", "N/A")),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "trailing_pe": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "recommendation_key": info.get("recommendationKey", "N/A"),
            "target_mean_price": info.get("targetMeanPrice", "N/A"),
            "business_summary": info.get("longBusinessSummary", "N/A"),
        }

        recommendations_summary = []
        try:
            recs = stock.recommendations
            if recs is not None and not recs.empty:
                recent_recs = recs.tail(5).reset_index()
                recommendations_summary = recent_recs.to_dict(orient="records")
        except Exception:
            recommendations_summary = []

        return json.dumps({
            "company_data": company_data,
            "analyst_recommendations": recommendations_summary
        }, indent=2, default=str)

    except Exception as e:
        return json.dumps({
            "error": str(e),
            "ticker": ticker
        }, indent=2)

# -----------------------------
# Custom tool 2: News search
# -----------------------------
def get_recent_news(query: str, max_results: int = 5) -> str:
    """Fetch recent web/news results using DDGS."""
    results = []
    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(query, max_results=max_results)
            for item in search_results:
                results.append({
                    "title": item.get("title", ""),
                    "body": item.get("body", ""),
                    "href": item.get("href", "")
                })
    except Exception as e:
        results.append({
            "title": "News fetch error",
            "body": str(e),
            "href": ""
        })

    return json.dumps(results, indent=2)

# -----------------------------
# Agno agent (tool orchestration only)
# -----------------------------
agent = Agent(
    tools=[get_stock_data, get_recent_news],
    markdown=True,
)

# -----------------------------
# Main flow
# -----------------------------
def main():
    ticker = "NVDA"

    print("🤖 Running Agno tools...\n")

    # Use Agno tools through the agent
    stock_payload = get_stock_data(ticker)
    news_payload = get_recent_news(
        "NVIDIA NVDA latest earnings AI chip demand analyst upgrades stock news",
        max_results=8
    )

    # Final Mercury 2 analysis
    prompt = f"""
You are a senior financial analyst.

Use the provided stock data, company information, analyst recommendations, and recent market news.
Always provide a clear BUY / HOLD / WAIT verdict with pros and cons.

Analyze NVIDIA (NVDA) and tell me if it's a good time to buy.

Stock Data:
{stock_payload}

Recent News:
{news_payload}

Respond in this format:
1. Company Overview
2. Current Valuation Snapshot
3. Analyst Sentiment
4. Recent News Impact
5. Pros
6. Cons
7. Final Verdict (BUY / HOLD / WAIT)
"""

    response = client.chat.completions.create(
        model="mercury-2",
        messages=[
            {"role": "system", "content": "You are an expert equity research analyst."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.4,
        max_tokens=1200
    )

    print("=" * 100)
    print(response.choices[0].message.content)
    print("=" * 100)

if __name__ == "__main__":
    main()