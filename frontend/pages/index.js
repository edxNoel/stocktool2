import { useState } from "react";
import axios from "axios";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from "chart.js";
import { Line } from "react-chartjs-2";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

export default function App() {
  const [ticker, setTicker] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [prices, setPrices] = useState([]);
  const [aiSummary, setAiSummary] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setPrices([]);
    setAiSummary("");

    try {
      const response = await axios.post("/api/analyze", {
        ticker,
        start_date: startDate,
        end_date: endDate,
      });

      setPrices(response.data.prices);
      setAiSummary(response.data.ai_summary);
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.error || "Error fetching stock data");
      setLoading(false);
    }
  };

  const chartData = {
    labels: prices.map((p) => p.date),
    datasets: [
      {
        label: `${ticker.toUpperCase()} Close Price`,
        data: prices.map((p) => p.close),
        fill: false,
        borderColor: "#2563EB",
        tension: 0.3,
      },
    ],
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-blue-100 via-white to-pink-100 p-6 flex flex-col items-center">
      <h1 className="text-4xl font-bold mb-6 text-gray-800">
        AI Stock Analyzer
      </h1>

      <div className="flex flex-wrap gap-3 mb-6">
        <input
          type="text"
          placeholder="Ticker (AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          className="p-3 rounded shadow border border-gray-300"
        />
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="p-3 rounded shadow border border-gray-300"
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="p-3 rounded shadow border border-gray-300"
        />
        <button
          onClick={handleAnalyze}
          className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {prices.length > 0 && (
        <div className="w-full max-w-4xl bg-white p-6 rounded shadow mb-6">
          <Line data={chartData} />
        </div>
      )}

      {aiSummary && (
        <div className="w-full max-w-4xl bg-white p-6 rounded shadow">
          <h2 className="text-2xl font-semibold mb-3">AI Summary</h2>
          <p className="text-gray-700 whitespace-pre-line">{aiSummary}</p>
        </div>
      )}
    </div>
  );
}
