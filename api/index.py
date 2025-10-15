from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yfinance as yf
import openai
import os

app = FastAPI()

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/api/analyze")
async def analyze_stock(request: dict):
    try:
        ticker = request.get("ticker")
        start_date = request.get("start_date")
        end_date = request.get("end_date")

        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")

        data = yf.download(ticker, start=start_date, end=end_date)
        if data.empty:
            raise HTTPException(status_code=404, detail="No data found")

        summary = (
            f"{ticker} closed at {round(data['Close'][-1], 2)} on the last date. "
            f"Highest close: {round(data['Close'].max(), 2)}; "
            f"Lowest close: {round(data['Close'].min(), 2)}."
        )

        # Optional AI summary
        ai_summary = None
        if openai.api_key:
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

        return JSONResponse({
            "ticker": ticker,
            "summary": summary,
            "ai_summary": ai_summary,
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
