import { useState } from "react";
import { analyzeNlp } from "../api.js";

const SAMPLES = [
  { label: "English", text: "Someone broke into the house near Andheri and stole a mobile phone and gold jewellery." },
  { label: "Hindi", text: "संदिग्ध ने दिल्ली के पास एक घर में जबरन प्रवेश किया और सोने के गहने ले गया।" },
  { label: "Bengali", text: "সন্দেহভাজন কলকাতার কাছে একটি বাড়িতে জোর করে ঢুকে সোনার গহনা নিয়ে গেছে।" },
  { label: "Marathi", text: "संशयिताने पुणे जवळील घरात जबरदस्तीने प्रवेश करून रोख रक्कम नेली." },
  { label: "Tamil", text: "சென்னை அருகே ஒரு வீட்டில் நுழைந்து தங்க நகைகள் எடுத்துச் சென்றார்." },
  { label: "Telugu", text: "హైదరాబాద్ సమీపంలోని ఇంట్లోకి బలవంతంగా ప్రవేశించి నగదు తీసుకెళ్లాడు." },
];

export default function NlpAnalysis() {
  const [text, setText] = useState(SAMPLES[0].text);
  const [translateTo, setTranslateTo] = useState("en");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const run = async () => {
    setLoading(true);
    setError(null);
    try {
      const r = await analyzeNlp(text, translateTo);
      setResult(r);
    } catch (e) {
      setError(e.response?.data?.detail?.[0]?.msg || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Multilingual NLP Analysis</h1>
      <p className="subtitle">Detects language, classifies crime type &amp; threat level, and translates crime report text.</p>

      <div className="card">
        <h2>Input text</h2>
        <textarea value={text} onChange={(e) => setText(e.target.value)} />
        <div style={{ margin: "10px 0" }}>
          {SAMPLES.map((s) => (
            <span key={s.label} className="tag" style={{ cursor: "pointer" }} onClick={() => setText(s.text)}>
              {s.label} sample
            </span>
          ))}
        </div>
        <label className="muted">Translate to</label>
        <select value={translateTo} onChange={(e) => setTranslateTo(e.target.value)}>
          <option value="en">English</option>
          <option value="hi">Hindi</option>
          <option value="bn">Bengali</option>
          <option value="mr">Marathi</option>
          <option value="ta">Tamil</option>
          <option value="te">Telugu</option>
          <option value="">No translation</option>
        </select>
        <br />
        <button onClick={run} disabled={loading || !text.trim()}>{loading ? "Analyzing…" : "Analyze"}</button>
        {error && <div className="error">{error}</div>}
      </div>

      {result && (
        <div className="card">
          <h2>Result</h2>
          <div className="kv"><span className="k">Detected language</span><span>{result.detected_language_name} ({result.detected_language}) · {(result.language_confidence * 100).toFixed(1)}%</span></div>
          <div className="kv"><span className="k">Crime type</span><span>{result.crime_type}</span></div>
          <div className="kv"><span className="k">Threat level</span><span><span className={`badge badge-${result.threat_level}`}>{result.threat_level}</span> ({(result.threat_level_confidence * 100).toFixed(1)}% conf.)</span></div>
          {result.translated_text && (
            <div className="kv"><span className="k">Translated text</span><span>{result.translated_text}</span></div>
          )}
          <div className="kv">
            <span className="k">Risk keywords</span>
            <span>{result.keyword_flags.length ? result.keyword_flags.map((k) => <span key={k} className="tag">{k}</span>) : "none"}</span>
          </div>
        </div>
      )}
    </div>
  );
}
