from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import os
import openai
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # replace * with your frontend URL in production
    allow_methods=["*"],
    allow_headers=["*"],
)

openai.api_key = os.environ.get("OPENAI_API_KEY")
if not openai.api_key:
    raise Exception("Please set OPENAI_API_KEY in environment variables")

class AnalyzeRequest(BaseModel):
    ticker: str
    start_date: str
    end_date: str

@app.post("/api/analyze")
async def analyze_stock(req: AnalyzeRequest):
    # Fetch stock data
    try:
        stock = yf.Ticker(req.ticker)
        hist = stock.history(start=req.start_date, end=req.end_date)
        if hist.empty:
            raise HTTPException(status_code=404, detail="No stock data found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Convert to list of prices
    prices = [{"date": str(idx.date()), "close": float(row["Close"])} for idx, row in hist.iterrows()]

    # Use OpenAI to generate insight
    try:
        prompt = f"Analyze the following stock price data and summarize trends:\n{prices}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        analysis = response.choices[0].message.content
    except Exception as e:
        analysis = f"OpenAI analysis failed: {e}"

    return {"prices": prices, "analysis": analysis}
