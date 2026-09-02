import { useState } from "react";
import { analyzeForensics } from "../api.js";

const SAMPLE = "User contacted john.doe@example.com from IP 192.168.1.44 on 2024-06-12, chat log: 'bring a knife and meet near Andheri station, don't tell anyone.'";

export default function Forensics() {
  const [text, setText] = useState(SAMPLE);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await analyzeForensics(text);
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Digital-Forensic Evidence Analysis</h1>
      <p className="subtitle">Extracts entities (emails, IPs, phone numbers, URLs, dates), flags risk keywords, and computes an integrity hash for a piece of digital evidence.</p>

      <div className="card">
        <h2>Evidence text (chat log, email, transcript…)</h2>
        <textarea value={text} onChange={(e) => setText(e.target.value)} />
        <button onClick={run} disabled={loading || !text.trim()}>{loading ? "Analyzing…" : "Analyze evidence"}</button>
        {error && <div className="error">{error}</div>}
      </div>

      {result && (
        <div className="grid grid-2">
          <div className="card">
            <h2>Risk assessment</h2>
            <div className="kv"><span className="k">Risk level</span><span><span className={`badge badge-${result.risk_level}`}>{result.risk_level}</span></span></div>
            <div className="kv"><span className="k">Risk score</span><span>{result.risk_score} / 100</span></div>
            <div className="kv"><span className="k">Detected language</span><span>{result.detected_language}</span></div>
            <div className="kv">
              <span className="k">Risk keywords</span>
              <span>{result.risk_keywords.length ? result.risk_keywords.map((k) => <span key={k} className="tag">{k}</span>) : "none"}</span>
            </div>
            <div className="kv"><span className="k">SHA-256</span><span style={{ fontSize: 11, wordBreak: "break-all" }}>{result.sha256}</span></div>
          </div>

          <div className="card">
            <h2>Extracted entities</h2>
            {Object.entries(result.entities).map(([key, values]) => (
              <div className="kv" key={key}>
                <span className="k">{key.replace("_", " ")}</span>
                <span>{values.length ? values.map((v) => <span key={v} className="tag">{v}</span>) : "—"}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
