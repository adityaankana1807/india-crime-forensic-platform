import { useEffect, useState } from "react";
import { getDatasets, getDatasetStats, uploadDataset } from "../api.js";

function formatBytes(n) {
  if (n < 1024) return `${n} B`;
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`;
  return `${(n / (1024 * 1024)).toFixed(2)} MB`;
}

export default function Datasets() {
  const [datasets, setDatasets] = useState([]);
  const [selected, setSelected] = useState(null);
  const [stats, setStats] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState(null);

  const refresh = () => getDatasets().then(setDatasets).catch((e) => setError(e.message));

  useEffect(() => { refresh(); }, []);

  const openDataset = (name) => {
    setSelected(name);
    setStats(null);
    getDatasetStats(name).then(setStats).catch((e) => setError(e.message));
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    setError(null);
    try {
      await uploadDataset(file);
      await refresh();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  };

  return (
    <div>
      <h1>Datasets</h1>
      <p className="subtitle">Browse real public crime datasets and generated synthetic multilingual datasets, or upload your own.</p>

      <div className="card">
        <h2>Upload a CSV dataset</h2>
        <input type="file" accept=".csv" onChange={handleUpload} disabled={uploading} />
        {uploading && <p className="muted">Uploading…</p>}
        {error && <div className="error">{error}</div>}
      </div>

      <div className="grid grid-2">
        <div className="card">
          <h2>All datasets ({datasets.length})</h2>
          <table>
            <thead><tr><th>Name</th><th>Category</th><th>Rows</th><th>Size</th></tr></thead>
            <tbody>
              {datasets.map((d) => (
                <tr key={d.name} className="dataset-row" onClick={() => openDataset(d.name)}>
                  <td>{d.name}</td>
                  <td><span className="tag">{d.category}</span></td>
                  <td>{d.rows.toLocaleString()}</td>
                  <td>{formatBytes(d.size_bytes)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="card">
          <h2>{selected ? `Preview: ${selected}` : "Select a dataset"}</h2>
          {!stats && selected && <p className="muted">Loading…</p>}
          {stats && (
            <>
              <div className="kv"><span className="k">Rows</span><span>{stats.rows.toLocaleString()}</span></div>
              <div className="kv"><span className="k">Columns</span><span>{stats.columns.length}</span></div>
              <div style={{ overflowX: "auto", marginTop: 12 }}>
                <table>
                  <thead>
                    <tr>{stats.columns.slice(0, 6).map((c) => <th key={c}>{c}</th>)}</tr>
                  </thead>
                  <tbody>
                    {stats.preview.slice(0, 8).map((row, i) => (
                      <tr key={i}>
                        {stats.columns.slice(0, 6).map((c) => (
                          <td key={c}>{String(row[c]).slice(0, 40)}</td>
                        ))}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
              {stats.columns.length > 6 && <p className="muted">Showing first 6 of {stats.columns.length} columns.</p>}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
