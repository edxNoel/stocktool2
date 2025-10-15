from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime
import yfinance as yf
import os

try:
    import openai
except Exception:
    openai = None

app = FastAPI()

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if OPENAI_API_KEY and openai is not None:
    openai.api_key = OPENAI_API_KEY

class AnalyzeRequest(BaseModel):
    ticker: str
    start_date: str  # YYYY-MM-DD
    end_date: str    # YYYY-MM-DD
    summary: bool = True

class AnalyzeResponse(BaseModel):
    ticker: str
    start_date: str
    end_date: str
    datapoints: list
    summary: str | None = None

def fetch_price_history(ticker, start_date, end_date):
    ticker_obj = yf.Ticker(ticker)
    df = ticker_obj.history(start=start_date, end=end_date)
    if df is None or df.empty:
        return None
    rows = []
    for idx, row in df.iterrows():
        rows.append({
            "date": idx.strftime("%Y-%m-%d"),
            "open": float(row["Open"]),
            "high": float(row["High"]),
            "low": float(row["Low"]),
            "close": float(row["Close"]),
            "volume": int(row["Volume"]),
        })
    return rows

@app.post("/api/analyze", response_model=AnalyzeResponse)
async def analyze(req: AnalyzeRequest):
    # validate dates
    try:
        sd = datetime.fromisoformat(req.start_date)
        ed = datetime.fromisoformat(req.end_date)
    except Exception:
        raise HTTPException(status_code=400, detail="Bad date format, use YYYY-MM-DD")

    data = fetch_price_history(req.ticker, req.start_date, req.end_date)
    if data is None:
        raise HTTPException(status_code=404, detail="No price data found for ticker / date range")

    summary_text = None
    if req.summary and OPENAI_API_KEY and openai is not None:
        try:
            sample = data[-30:] if len(data) > 30 else data
            prompt = (
                f"Summarize key price movement patterns for {req.ticker} between {req.start_date} and {req.end_date}.\n"
                f"Use the following last {len(sample)} data points (date,close):\n"
            )
            prompt += "\n".join(f"{d['date']}: {d['close']}" for d in sample)
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role":"user","content": prompt}],
                max_tokens=200,
                temperature=0.0,
            )
            summary_text = resp["choices"][0]["message"]["content"].strip()
        except Exception as e:
            summary_text = f"AI summary failed: {str(e)}"

    return AnalyzeResponse(
        ticker=req.ticker.upper(),
        start_date=req.start_date,
        end_date=req.end_date,
        datapoints=data,
        summary=summary_text
    )
