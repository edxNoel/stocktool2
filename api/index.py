from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import requests
import os
import openai

app = FastAPI(title="AI Stock Analyzer")

openai.api_key = os.getenv("OPENAI_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY", "demo")  # replace demo with your key

@app.post("/api/analyze")
async def analyze_stock(request: dict):
    ticker = request.get("ticker", "").strip().upper()
    if not ticker:
        raise HTTPException(status_code=400, detail="Ticker is required")

    # Use FMP historical price API
    start_date = request.get("start_date", "2024-01-01")
    end_date = request.get("end_date", "2024-10-01")
    
    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start_date}&to={end_date}&apikey={FMP_API_KEY}"
    
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": f"FMP request failed: {str(e)}"})
    
    if not data.get("historical"):
        return JSONResponse(
            status_code=404,
            content={"error": f"No price data found for {ticker} in the given date range."}
        )
    
    historical = data["historical"]
    close_prices = [day["close"] for day in historical]
    summary = (
        f"{ticker} closed at {close_prices[0]} on the first date. "
        f"Highest close: {max(close_prices)}; Lowest close: {min(close_prices)}."
    )
    
    ai_summary = None
    if openai.api_key:
        try:
            prompt = (
                f"Provide a brief investment-style summary for {ticker} "
                f"based on the following data: {summary}"
            )
            resp = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=120,
            )
            ai_summary = resp.choices[0].message.content
        except Exception as e:
            ai_summary = f"AI summary failed: {str(e)}"

    return JSONResponse({
        "ticker": ticker,
        "summary": summary,
        "ai_summary": ai_summary
    })
