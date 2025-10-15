from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import yfinance as yf
import openai
import os

app = FastAPI(title="AI Stock Analyzer")

# Use environment variable for OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.post("/api/analyze")
async def analyze_stock(request: dict):
    try:
        ticker = request.get("ticker", "").strip().upper()
        start_date = request.get("start_date", "2024-01-01")
        end_date = request.get("end_date", "2024-10-01")

        if not ticker:
            raise HTTPException(status_code=400, detail="Ticker is required")

        # Safe yfinance call with progress=False to avoid Vercel issues
        try:
            data = yf.download(ticker, start=start_date, end=end_date, progress=False)
        except Exception as yf_err:
            return JSONResponse(
                status_code=500,
                content={"error": f"Failed to fetch data from Yahoo Finance: {yf_err}"}
            )

        if data.empty:
            return JSONResponse(
                status_code=404,
                content={"error": f"No price data found for {ticker} in the given date range."}
            )

        summary = (
            f"{ticker} closed at {round(data['Close'][-1], 2)} on the last date. "
            f"Highest close: {round(data['Close'].max(), 2)}; "
            f"Lowest close: {round(data['Close'].min(), 2)}."
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

    except Exception as e:
        # Catch-all for unexpected errors
        raise HTTPException(status_code=500, detail=str(e))
