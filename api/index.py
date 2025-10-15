# api/index.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests
import os
import openai
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)

# Initialize FastAPI
app = FastAPI()

# Environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")
FMP_API_KEY = os.getenv("FMP_API_KEY", "demo")

@app.post("/api/analyze")
async def analyze_stock(request: Request):
    try:
        # Read JSON payload
        payload = await request.json()
        logging.info(f"Payload received: {payload}")

        ticker = payload.get("ticker", "").strip().upper()
        start_date = payload.get("start_date", "2024-01-01")
        end_date = payload.get("end_date", "2024-10-01")

        if not ticker:
            return JSONResponse(status_code=400, content={"error": "Ticker is required"})

        # Fetch stock data from FMP
        url = f"https://financialmodelingprep.com/api/v3/historical-price-full/{ticker}?from={start_date}&to={end_date}&apikey={FMP_API_KEY}"
        try:
            resp = requests.get(url, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            logging.info(f"FMP response: {data}")
        except requests.exceptions.RequestException as e:
            logging.error(f"FMP request failed: {e}")
            return JSONResponse(status_code=502, content={"error": f"FMP request failed: {str(e)}"})

        if not data.get("historical"):
            return JSONResponse(status_code=404, content={"error": f"No price data for {ticker} in the given date range"})

        # Extract prices
        close_prices = [day["close"] for day in data["historical"]]
        summary = f"{ticker} stock from {start_date} to {end_date}: first close={close_prices[0]}, high={max(close_prices)}, low={min(close_prices)}"

        # Generate AI summary if OpenAI key exists
        ai_summary = None
        if openai.api_key:
            try:
                prompt = f"Summarize the stock performance: {summary}"
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=120
                )
                ai_summary = response.choices[0].message.content
            except Exception as e:
                logging.error(f"OpenAI request failed: {e}")
                ai_summary = f"AI summary failed: {str(e)}"

        return {"ticker": ticker, "summary": summary, "ai_summary": ai_summary}

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return JSONResponse(status_code=500, content={"error": f"Unexpected server error: {str(e)}"})
