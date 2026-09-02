import { useEffect, useState } from "react";
import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getHotspots, getTrends } from "../api.js";

export default function CrimeAnalysis() {
  const [hotspots, setHotspots] = useState(null);
  const [trends, setTrends] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([getHotspots(), getTrends()])
      .then(([h, t]) => { setHotspots(h); setTrends(t); })
      .catch((e) => setError(e.message));
  }, []);

  const monthly = trends ? Object.entries(trends.by_month).map(([month, count]) => ({ month, count })) : [];

  return (
    <div>
      <h1>Crime Behaviour Analysis</h1>
      <p className="subtitle">Geospatial hotspot clustering (DBSCAN) and temporal trend analysis over the synthetic crime-hotspot dataset.</p>
      {error && <div className="error">{error}</div>}

      <div className="card">
        <h2>Monthly crime volume</h2>
        {monthly.length > 0 && (
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={monthly}>
              <CartesianGrid strokeDasharray="3 3" stroke="#262e45" />
              <XAxis dataKey="month" stroke="#8b93ab" fontSize={11} />
              <YAxis stroke="#8b93ab" fontSize={12} />
              <Tooltip contentStyle={{ background: "#1a2033", border: "1px solid #262e45" }} />
              <Line type="monotone" dataKey="count" stroke="#4f8cff" strokeWidth={2} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      <div className="card">
        <h2>
          Detected hotspot clusters
          {hotspots && <span className="muted"> — {hotspots.cluster_count} clusters across {hotspots.total_points.toLocaleString()} points ({hotspots.noise_points} noise points)</span>}
        </h2>
        {hotspots && (
          <table>
            <thead>
              <tr><th>City</th><th>Size</th><th>Center (lat, lon)</th><th>Dominant crime type</th><th>High-threat share</th></tr>
            </thead>
            <tbody>
              {hotspots.clusters.map((c) => (
                <tr key={c.cluster_id}>
                  <td>{c.dominant_city}</td>
                  <td>{c.size}</td>
                  <td>{c.center_lat}, {c.center_lon}</td>
                  <td>{c.dominant_crime_type}</td>
                  <td>{(c.high_threat_share * 100).toFixed(1)}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      <div className="card">
        <h2>By city</h2>
        {trends && (
          <table>
            <thead><tr><th>City</th><th>Records</th></tr></thead>
            <tbody>
              {Object.entries(trends.by_city).sort((a, b) => b[1] - a[1]).map(([city, count]) => (
                <tr key={city}><td>{city}</td><td>{count}</td></tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
