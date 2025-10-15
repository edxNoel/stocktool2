# backend/api/index.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
import os
print("ALPHA_VANTAGE_API_KEY:", os.environ.get("ALPHA_VANTAGE_API_KEY"))
app = FastAPI()

# Request schema must match the frontend keys exactly
class AnalyzeRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str

ALPHA_VANTAGE_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY")
if not ALPHA_VANTAGE_KEY:
    raise Exception("Please set ALPHA_VANTAGE_API_KEY in your environment variables")

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    ticker = req.ticker.upper()
    start_date = req.start_date
    end_date = req.end_date

    url = (
        f"https://www.alphavantage.co/query"
        f"?function=TIME_SERIES_DAILY_ADJUSTED"
        f"&symbol={ticker}"
        f"&outputsize=full"
        f"&apikey={ALPHA_VANTAGE_KEY}"
    )

    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=500, detail="Failed to fetch data from Alpha Vantage")

    data = response.json()
    if "Time Series (Daily)" not in data:
        raise HTTPException(status_code=422, detail="Invalid ticker or no data returned")

    # Extract and filter by date range
    time_series = data["Time Series (Daily)"]
    prices = []
    for date, daily_data in sorted(time_series.items()):
        if start_date <= date <= end_date:
            prices.append({
                "date": date,
                "close": float(daily_data["4. close"])
            })

    if not prices:
        raise HTTPException(status_code=422, detail="No price data found for ticker/date range")

    return {"prices": prices}
