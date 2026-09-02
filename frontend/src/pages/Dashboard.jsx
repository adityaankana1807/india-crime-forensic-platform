import { useEffect, useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { getDatasets, getTrends } from "../api.js";

const THREAT_COLORS = { low: "#3fa554", medium: "#e8c547", high: "#f0873c", critical: "#ef5757" };
const PALETTE = ["#4f8cff", "#22c3a6", "#f0a83c", "#ef5757", "#a06cf5", "#38bdf8", "#e8c547", "#3fa554", "#f472b6", "#94a3b8"];

export default function Dashboard() {
  const [datasets, setDatasets] = useState([]);
  const [trends, setTrends] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([getDatasets(), getTrends()])
      .then(([ds, tr]) => {
        setDatasets(ds);
        setTrends(tr);
      })
      .catch((e) => setError(e.message));
  }, []);

  const totalRows = datasets.reduce((sum, d) => sum + d.rows, 0);
  const byTypeData = trends ? Object.entries(trends.by_crime_type).map(([name, value]) => ({ name, value })) : [];
  const byThreatData = trends ? Object.entries(trends.by_threat_level).map(([name, value]) => ({ name, value })) : [];

  return (
    <div>
      <h1>Platform Overview</h1>
      <p className="subtitle">AI-driven multilingual crime behaviour &amp; digital-forensic evidence analysis for India — real NCRB statistics plus synthetic reports in English, Hindi, Bengali, Marathi, Tamil &amp; Telugu</p>
      {error && <div className="error">{error}</div>}

      <div className="grid grid-3">
        <div className="card">
          <div className="stat">{datasets.length}</div>
          <div className="stat-label">Datasets loaded</div>
        </div>
        <div className="card">
          <div className="stat">{totalRows.toLocaleString()}</div>
          <div className="stat-label">Total records</div>
        </div>
        <div className="card">
          <div className="stat">6</div>
          <div className="stat-label">Languages supported</div>
        </div>
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>Crime records by type (synthetic hotspot dataset)</h2>
          {byTypeData.length > 0 && (
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={byTypeData} layout="vertical" margin={{ left: 30 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#262e45" />
                <XAxis type="number" stroke="#8b93ab" fontSize={12} />
                <YAxis type="category" dataKey="name" stroke="#8b93ab" fontSize={11} width={100} />
                <Tooltip contentStyle={{ background: "#1a2033", border: "1px solid #262e45" }} />
                <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                  {byTypeData.map((_, i) => (
                    <Cell key={i} fill={PALETTE[i % PALETTE.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>

        <div className="card">
          <h2>Threat level distribution</h2>
          {byThreatData.length > 0 && (
            <ResponsiveContainer width="100%" height={260}>
              <PieChart>
                <Pie data={byThreatData} dataKey="value" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2}>
                  {byThreatData.map((d, i) => (
                    <Cell key={i} fill={THREAT_COLORS[d.name] || "#8b93ab"} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ background: "#1a2033", border: "1px solid #262e45" }} />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      <div className="card">
        <h2>Datasets</h2>
        <table>
          <thead>
            <tr><th>Name</th><th>Category</th><th>Rows</th><th>Columns</th></tr>
          </thead>
          <tbody>
            {datasets.map((d) => (
              <tr key={d.name}>
                <td>{d.name}</td>
                <td><span className="tag">{d.category}</span></td>
                <td>{d.rows.toLocaleString()}</td>
                <td>{d.columns.length}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
