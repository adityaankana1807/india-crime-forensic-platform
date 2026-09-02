import { useEffect, useState } from "react";
import { getBehaviorProfile, getBehaviorProfiles, getBehaviorNarrative } from "../api.js";

export default function Behavior() {
  const [profiles, setProfiles] = useState([]);
  const [selected, setSelected] = useState(null);
  const [detail, setDetail] = useState(null);
  const [narrative, setNarrative] = useState(null);
  const [narrativeLoading, setNarrativeLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    getBehaviorProfiles().then(setProfiles).catch((e) => setError(e.message));
  }, []);

  const openProfile = (suspectId) => {
    setSelected(suspectId);
    setDetail(null);
    setNarrative(null);
    getBehaviorProfile(suspectId).then(setDetail).catch((e) => setError(e.message));
  };

  const runNarrative = async () => {
    setNarrativeLoading(true);
    try {
      const r = await getBehaviorNarrative(selected);
      setNarrative(r);
    } catch (e) {
      setError(e.message);
    } finally {
      setNarrativeLoading(false);
    }
  };

  return (
    <div>
      <h1>Criminal Behaviour Profiles</h1>
      <p className="subtitle">Modus-operandi consistency and escalation patterns across linked multi-incident suspect sequences in the synthetic crime-report dataset.</p>
      {error && <div className="error">{error}</div>}

      <div className="grid grid-2">
        <div className="card">
          <h2>Suspects ({profiles.length})</h2>
          <table>
            <thead><tr><th>ID</th><th>Incidents</th><th>MO</th><th>Escalating</th></tr></thead>
            <tbody>
              {profiles.map((p) => (
                <tr key={p.suspect_id} className="dataset-row" onClick={() => openProfile(p.suspect_id)}>
                  <td>{p.suspect_id}</td>
                  <td>{p.incident_count}</td>
                  <td>{p.dominant_crime_type} ({(p.mo_consistency * 100).toFixed(0)}%)</td>
                  <td>{p.escalating ? <span className="badge badge-high">yes</span> : <span className="badge badge-low">no</span>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h2>{selected ? `Profile: ${selected}` : "Select a suspect"}</h2>
          {detail && (
            <>
              <div className="kv"><span className="k">MO cluster</span><span>{detail.mo_cluster}</span></div>
              <div className="kv"><span className="k">Incident count</span><span>{detail.incident_count}</span></div>
              <div className="kv"><span className="k">MO consistency</span><span>{(detail.mo_consistency * 100).toFixed(0)}%</span></div>
              <div className="kv"><span className="k">Current threat level</span><span><span className={`badge badge-${detail.current_threat_level}`}>{detail.current_threat_level}</span></span></div>
              <div className="kv"><span className="k">Locations</span><span>{detail.locations_involved?.join(", ")}</span></div>

              <h2 style={{ marginTop: 16 }}>Timeline</h2>
              <table>
                <thead><tr><th>Date</th><th>Crime type</th><th>Threat</th><th>Location</th></tr></thead>
                <tbody>
                  {detail.incidents?.map((inc, i) => (
                    <tr key={i}>
                      <td>{inc.date}</td>
                      <td>{inc.crime_type}</td>
                      <td><span className={`badge badge-${inc.threat_level}`}>{inc.threat_level}</span></td>
                      <td>{inc.location}</td>
                    </tr>
                  ))}
                </tbody>
              </table>

              <button onClick={runNarrative} disabled={narrativeLoading}>{narrativeLoading ? "Generating…" : "Generate LLM behavioural narrative"}</button>
              {narrative && narrative.error && <p className="error">{narrative.error}</p>}
              {narrative && !narrative.error && (
                <div style={{ marginTop: 12 }}>
                  <div className="kv"><span className="k">Risk trajectory</span><span>{narrative.risk_trajectory}</span></div>
                  <p className="muted" style={{ marginTop: 8 }}>{narrative.narrative}</p>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
