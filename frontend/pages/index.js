import { useState } from "react";

export default function Home() {
  const [ticker, setTicker] = useState("AAPL");
  const [startDate, setStartDate] = useState("2024-01-01");
  const [endDate, setEndDate] = useState("2024-12-31");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function handleAnalyze(e) {
    e?.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const resp = await fetch("/api/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ticker, start_date: startDate, end_date: endDate, summary: true })
      });
      if (!resp.ok) {
        const err = await resp.json().catch(()=>({detail: resp.statusText}));
        throw new Error(err.detail || resp.statusText);
      }
      const data = await resp.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main style={{ padding: 24, fontFamily: "system-ui, sans-serif" }}>
      <h1>AI Stock Analyzer (Basic)</h1>
      <form onSubmit={handleAnalyze} style={{ marginBottom: 20 }}>
        <label style={{ display: "block", marginBottom: 8 }}>
          Ticker: <input value={ticker} onChange={(e)=>setTicker(e.target.value)} />
        </label>
        <label style={{ display: "block", marginBottom: 8 }}>
          Start: <input type="date" value={startDate} onChange={e=>setStartDate(e.target.value)} />
        </label>
        <label style={{ display: "block", marginBottom: 8 }}>
          End: <input type="date" value={endDate} onChange={e=>setEndDate(e.target.value)} />
        </label>
        <button type="submit" disabled={loading}>{loading ? "Analyzing..." : "Analyze"}</button>
      </form>

      {error && <div style={{ color: "red" }}>Error: {error}</div>}

      {result && (
        <section style={{ marginTop: 24 }}>
          <h2>{result.ticker} — {result.start_date} → {result.end_date}</h2>
          <p><strong>AI summary:</strong> {result.summary || "No summary (set OPENAI_API_KEY to enable)"}</p>

          <h3>Data points (last 10)</h3>
          <ul>
            {result.datapoints.slice(-10).map(d => (
              <li key={d.date}>{d.date}: {d.close}</li>
            ))}
          </ul>
        </section>
      )}
    </main>
  );
}
