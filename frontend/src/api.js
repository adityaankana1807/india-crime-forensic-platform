import axios from "axios";

const api = axios.create({ baseURL: "/api" });

export const getDatasets = () => api.get("/datasets").then((r) => r.data);
export const getDatasetStats = (name, previewRows = 10) =>
  api.get(`/datasets/${encodeURIComponent(name)}/stats`, { params: { preview_rows: previewRows } }).then((r) => r.data);
export const uploadDataset = (file) => {
  const form = new FormData();
  form.append("file", file);
  return api.post("/datasets/upload", form, { headers: { "Content-Type": "multipart/form-data" } }).then((r) => r.data);
};

export const analyzeNlp = (text, translateTo) =>
  api.post("/nlp/analyze", { text, translate_to: translateTo || null }).then((r) => r.data);

export const analyzeForensics = (text, source) =>
  api.post("/forensics/analyze", { text, source: source || "unspecified" }).then((r) => r.data);

export const getHotspots = (epsKm = 5, minSamples = 10) =>
  api.get("/crime-analysis/hotspots", { params: { eps_km: epsKm, min_samples: minSamples } }).then((r) => r.data);
export const getTrends = () => api.get("/crime-analysis/trends").then((r) => r.data);

export default api;
