"use client";

import { useState } from "react";
import axios from "axios";
import ReactFlow, { MiniMap, Controls, Background } from "react-flow-renderer";

export default function Home() {
  const [ticker, setTicker] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [nodes, setNodes] = useState([]);
  const [edges, setEdges] = useState([]);
  const [analysis, setAnalysis] = useState("");
  const [loading, setLoading] = useState(false);

  const handleAnalyze = async () => {
    setLoading(true);
    setNodes([]);
    setEdges([]);
    setAnalysis("");

    try {
      const { data } = await axios.post("/api/analyze", {
        ticker,
        start_date: startDate,
        end_date: endDate,
      });

      const prices = data.prices;

      if (!prices || prices.length === 0) {
        alert("No data found for this ticker/date range");
        setLoading(false);
        return;
      }

      const newNodes = prices.map((p, i) => ({
        id: `${i}`,
        position: { x: i * 130, y: Math.random() * 180 },
        data: { label: `${p.date}\n$${p.close.toFixed(2)}` },
      }));

      setNodes(newNodes);
      setAnalysis(data.analysis);
      setLoading(false);
    } catch (err) {
      console.error(err);
      alert("Error fetching stock data");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center bg-gradient-to-tr from-indigo-50 via-white to-pink-50 p-6">
      {/* Header */}
      <h1 className="text-4xl md:text-5xl font-extrabold mb-6 text-indigo-900 text-center drop-shadow-md">
        AI Stock Node Analyzer
      </h1>

      {/* Input Panel */}
      <div className="flex flex-col md:flex-row gap-3 mb-6 w-full max-w-4xl">
        <input
          type="text"
          placeholder="Ticker (AAPL)"
          value={ticker}
          onChange={(e) => setTicker(e.target.value.toUpperCase())}
          className="flex-1 p-3 rounded-lg shadow-md border border-gray-300 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
        />
        <input
          type="date"
          value={startDate}
          onChange={(e) => setStartDate(e.target.value)}
          className="p-3 rounded-lg shadow-md border border-gray-300 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
        />
        <input
          type="date"
          value={endDate}
          onChange={(e) => setEndDate(e.target.value)}
          className="p-3 rounded-lg shadow-md border border-gray-300 focus:ring-2 focus:ring-indigo-400 focus:outline-none"
        />
        <button
          onClick={handleAnalyze}
          className="bg-indigo-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-indigo-700 transition shadow-lg"
        >
          {loading ? "Analyzing..." : "Analyze"}
        </button>
      </div>

      {/* Node Visualization */}
      <div className="flex-1 w-full max-w-6xl h-[500px] rounded-2xl shadow-xl bg-white border border-gray-200 overflow-hidden mb-6">
        <ReactFlow nodes={nodes} edges={edges} fitView>
          <MiniMap nodeStrokeColor={(n) => "#4F46E5"} nodeColor={(n) => "#C7D2FE"} />
          <Controls />
          <Background color="#E5E7EB" gap={16} />
        </ReactFlow>
      </div>

      {/* AI Analysis Panel */}
      {analysis && (
        <div className="w-full max-w-4xl p-6 bg-gradient-to-br from-indigo-50 to-white rounded-2xl shadow-xl border border-gray-200">
          <h2 className="text-2xl font-bold mb-3 text-indigo-900">AI Analysis</h2>
          <p className="text-gray-700 whitespace-pre-wrap">{analysis}</p>
        </div>
      )}
    </div>
  );
}
