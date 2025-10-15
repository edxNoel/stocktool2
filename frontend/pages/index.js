"use client";

import { useState } from "react";
import axios from "axios";
import ReactFlow, { MiniMap, Controls, Background } from "react-flow-renderer";

export default function App() {
  const [ticker, setTicker] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState("");

  const handleAnalyze = async () => {
    setLoading(true);
    setNodes([]);
    setEdges([]);
    setAnalysis("");

    try {
      const response = await axios.post("http://localhost:5000/api/analyze", {
        ticker,
        start_date: startDate,
        end_date: endDate,
      });

      const prices = response.data.prices;

      if (!prices || prices.length === 0) {
        alert("No data found for this ticker/date range");
        setLoading(false);
        return;
      }

      const newNodes = prices.map((p, i) => ({
        id: `${i}`,
        position: { x: i * 120, y: Math.random() * 200 },
        data: { label: `${p.date}\n$${p.close}` },
      }));

      setNodes(newNodes);
      setAnalysis(response.data.analysis);
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert("Error fetching stock data");
      setLoading(false);
    }
  };

  return (
    <div className="h-screen flex flex-col items-center bg-gradient-to-r from-blue-100 via-white to-pink-100 p-4">
      <h1 className="text-3xl font-bold mb-4 text-gray-800">AI Stock Node Analyzer</h1>
      <div className="flex gap-2 mb-6">
        <input
          type="text"
          placeholder="Ticker (AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value)}
          className="p-2 rounded shadow border border-gray-300"
        />
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="p-2 rounded shadow border border-gray-300"
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="p-2 rounded shadow border border-gray-300"
        />
        <button
          onClick={handleAnalyze}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 transition"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      <div className="flex-1 w-full rounded shadow bg-white p-4">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <MiniMap />
          <Controls />
          <Background color="#aaa" gap={16} />
        </ReactFlow>
      </div>

      {analysis && (
        <div className="mt-4 p-4 w-full max-w-4xl rounded shadow bg-gray-50">
          <h2 className="text-xl font-semibold mb-2">AI Analysis</h2>
          <p>{analysis}</p>
        </div>
      )}
    </div>
  );
}
