import { NavLink, Route, Routes } from "react-router-dom";
import CrimeAnalysis from "./pages/CrimeAnalysis.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Datasets from "./pages/Datasets.jsx";
import Forensics from "./pages/Forensics.jsx";
import NlpAnalysis from "./pages/NlpAnalysis.jsx";

const links = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/datasets", label: "Datasets" },
  { to: "/nlp", label: "Multilingual NLP" },
  { to: "/forensics", label: "Forensic Evidence" },
  { to: "/crime-analysis", label: "Crime Behaviour" },
];

export default function App() {
  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          Crime &amp; Forensic<br /><span>Analysis Platform</span>
        </div>
        <nav className="nav">
          {links.map((l) => (
            <NavLink key={l.to} to={l.to} end={l.end} className={({ isActive }) => (isActive ? "active" : "")}>
              {l.label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/datasets" element={<Datasets />} />
          <Route path="/nlp" element={<NlpAnalysis />} />
          <Route path="/forensics" element={<Forensics />} />
          <Route path="/crime-analysis" element={<CrimeAnalysis />} />
        </Routes>
      </main>
    </div>
  );
}
