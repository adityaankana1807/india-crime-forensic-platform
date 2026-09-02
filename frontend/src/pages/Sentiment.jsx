import { useState } from "react";
import { analyzeSentiment } from "../api.js";

const SAMPLE = "Message: 'I think I'm being followed near Andheri, I'm really scared, please help me.'";

const TONE_COLORS = { threatening: "critical", deceptive: "high", distressed: "medium", neutral: "low" };

export default function Sentiment() {
  const [text, setText] = useState(SAMPLE);
  const [useLlm, setUseLlm] = useState(true);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await analyzeSentiment(text, useLlm);
      setResult(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Sentiment &amp; Emotional-Tone Analysis</h1>
      <p className="subtitle">Classifies evidence text into deceptive / threatening / neutral / distressed tone — a TF-IDF baseline, cross-checked against Claude when available.</p>

      <div className="card">
        <h2>Evidence text</h2>
        <textarea value={text} onChange={(e) => setText(e.target.value)} />
        <label className="muted" style={{ display: "block", marginTop: 10 }}>
          <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} style={{ marginRight: 6 }} />
          Cross-check with LLM (Claude)
        </label>
        <button onClick={run} disabled={loading || !text.trim()}>{loading ? "Analyzing…" : "Analyze sentiment"}</button>
        {error && <div className="error">{error}</div>}
      </div>

      {result && (
        <div className="grid grid-2">
          <div className="card">
            <h2>Baseline (TF-IDF + LogisticRegression)</h2>
            <div className="kv">
              <span className="k">Tone</span>
              <span><span className={`badge badge-${TONE_COLORS[result.baseline.tone] || "medium"}`}>{result.baseline.tone}</span></span>
            </div>
            <div className="kv"><span className="k">Confidence</span><span>{(result.baseline.confidence * 100).toFixed(1)}%</span></div>
          </div>

          <div className="card">
            <h2>LLM (Claude)</h2>
            {!result.llm && <p className="muted">Not available — set ANTHROPIC_API_KEY on the backend, or the request opted out.</p>}
            {result.llm && (
              <>
                <div className="kv">
                  <span className="k">Tone</span>
                  <span><span className={`badge badge-${TONE_COLORS[result.llm.tone] || "medium"}`}>{result.llm.tone}</span></span>
                </div>
                <div className="kv"><span className="k">Intensity</span><span>{result.llm.intensity} / 5</span></div>
                <div className="kv"><span className="k">Rationale</span><span>{result.llm.rationale}</span></div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
