import os
from flask import Flask, request, jsonify
import yfinance as yf
import openai

# Initialize Flask
app = Flask(__name__)

# Make sure your OpenAI API key is set in environment variables
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    ticker = data.get("ticker")
    start_date = data.get("start_date")
    end_date = data.get("end_date")

    if not ticker or not start_date or not end_date:
        return jsonify({"error": "ticker, start_date, and end_date are required"}), 400

    try:
        # Fetch historical stock data
        stock = yf.Ticker(ticker)
        hist = stock.history(start=start_date, end=end_date)

        if hist.empty:
            return jsonify({"error": "No data found for this ticker/date range"}), 404

        # Convert to list of dicts
        prices = [{"date": str(index.date()), "close": round(row["Close"], 2)} for index, row in hist.iterrows()]

        # Optionally, send prices to OpenAI for some AI analysis
        # Example: summarize trends
        summary_prompt = f"Analyze the following stock prices for {ticker} and summarize trends:\n{prices}"
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": summary_prompt}],
            temperature=0.7,
            max_tokens=200
        )

        ai_summary = response.choices[0].message["content"]

        return jsonify({
            "prices": prices,
            "ai_summary": ai_summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Vercel requires this for serverless function
def handler(event, context):
    from werkzeug.datastructures import Headers
    from werkzeug.wrappers import Request, Response

    @Request.application
    def application(request):
        with app.app_context():
            return app.full_dispatch_request()

    return Response.from_app(application, event, context)
