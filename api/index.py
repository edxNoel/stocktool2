import json
from flask import Flask, request, jsonify
import openai

app = Flask(__name__)

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise Exception("Set OPENAI_API_KEY in environment variables")

openai.api_key = OPENAI_API_KEY

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    ticker = data.get("ticker")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not ticker or not start_date or not end_date:
        return jsonify({"error": "Missing ticker/start_date/end_date"}), 400

    try:
        # Lazy import inside the function
        import yfinance as yf
        import pandas as pd

        stock = yf.Ticker(ticker)
        df = stock.history(start=start_date, end=end_date)
        if df.empty:
            return jsonify({"error": "No stock data found"}), 404

        prices = [{"date": str(i.date()), "close": float(row["Close"])} for i, row in df.iterrows()]

        # AI analysis
        ai_prompt = f"Analyze this stock data for {ticker} from {start_date} to {end_date}:\n{prices}"
        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": ai_prompt}],
            temperature=0.7
        )
        analysis = completion.choices[0].message.content

        return jsonify({"prices": prices, "analysis": analysis})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
