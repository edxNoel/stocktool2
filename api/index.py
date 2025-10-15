# api/index.py
import os
from fastapi import FastAPI, HTTPException
import requests


app = FastAPI()
ALPHA_KEY = os.getenv("ALPHA_VANTAGE_KEY")

@app.post("/api/analyze")
async def analyze(ticker: str, start_date: str, end_date: str):
    # Alpha Vantage daily historical data endpoint
    url = f"https://www.alphavantage.co/query"
    params = {
        "function": "TIME_SERIES_DAILY_ADJUSTED",
        "symbol": ticker,
        "outputsize": "full",
        "apikey": ALPHA_KEY
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch data from Alpha Vantage")

    data = response.json()
    if "Time Series (Daily)" not in data:
        raise HTTPException(status_code=404, detail="No price data found for ticker / date range")

    # Filter by date range
    time_series = data["Time Series (Daily)"]
    filtered = {date: info for date, info in time_series.items() if start_date <= date <= end_date}
    if not filtered:
        raise HTTPException(status_code=404, detail="No price data found in the specified range")

    # Convert to list of closing prices
    closing_prices = [{ "date": date, "close": float(info["4. close"]) } for date, info in filtered.items()]

    return {
        "ticker": ticker,
        "prices": closing_prices
    }
