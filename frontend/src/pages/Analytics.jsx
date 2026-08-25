import { useEffect, useState } from "react";
import { CampusAPI } from "../services/api.js";
import EnergyChart from "../components/EnergyChart.jsx";
import SolarChart from "../components/SolarChart.jsx";
import WaterChart from "../components/WaterChart.jsx";
import DepartmentTable from "../components/DepartmentTable.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { downloadBlob, fmt } from "../utils/format.js";

function periodFromCustom(from, to) {
  if (!from || !to) return "7d";
  const days = (new Date(to) - new Date(from)) / 86400000;
  if (days <= 1) return "24h";
  if (days <= 7) return "7d";
  return "30d";
}

export default function Analytics() {
  const [period, setPeriod] = useState("7d");
  const [customFrom, setCustomFrom] = useState("");
  const [customTo, setCustomTo] = useState("");
  const [dash, setDash] = useState(null);
  const [summary, setSummary] = useState(null);
  const [water, setWater] = useState([]);
  const [solar, setSolar] = useState([]);
  const [scores, setScores] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async (p = period) => {
    setError("");
    setLoading(true);
    try {
      const [d, s, w, so, sc] = await Promise.all([
        CampusAPI.dashboard(p),
        CampusAPI.summary(p),
        CampusAPI.waterLatest(),
        CampusAPI.solarLatest(),
        CampusAPI.scores(p === "24h" ? "7d" : p),
      ]);
      setDash(d.data);
      setSummary(s.data);
      setWater(w.data || []);
      setSolar(so.data || []);
      setScores(sc.data || []);
    } catch {
      setError("Could not load analytics. Backend unavailable.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load(period);
  }, [period]);

  const applyCustom = () => {
    const mapped = periodFromCustom(customFrom, customTo);
    setPeriod(mapped);
  };

  const exportCsv = async () => {
    try {
      const res = await CampusAPI.export(period, "csv");
      downloadBlob(res.data, `campus-analytics-${period}.csv`);
    } catch {
      setError("CSV export requires a signed-in facility or admin account.");
    }
  };

  const s = summary || {};
  const trees = ((s.co2_avoided_kg || 0) / 21).toFixed(1);

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
        <h1 className="font-display text-3xl">Analytics</h1>
        <div className="flex flex-wrap items-center gap-2">
          {["24h", "7d", "30d"].map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPeriod(p)}
              className={`rounded-lg px-3 py-1.5 text-sm ${period === p ? "bg-emerald-800 text-white" : "card px-3"}`}
            >
              {p === "24h" ? "Today" : p === "7d" ? "7 Days" : "30 Days"}
            </button>
          ))}
          <input type="date" className="card px-2 py-1.5 text-sm" value={customFrom} onChange={(e) => setCustomFrom(e.target.value)} />
          <input type="date" className="card px-2 py-1.5 text-sm" value={customTo} onChange={(e) => setCustomTo(e.target.value)} />
          <button type="button" onClick={applyCustom} className="rounded-lg border border-stone-300 px-3 py-1.5 text-sm dark:border-white/20">
            Custom
          </button>
          <button type="button" onClick={exportCsv} className="rounded-lg border border-stone-300 px-3 py-1.5 text-sm dark:border-white/20">
            CSV export
          </button>
        </div>
      </div>
      <p className="mb-3 text-xs text-stone-500">
        Summary windows are calculated as {period} ({s.start ? new Date(s.start).toLocaleString() : "—"} — {s.end ? new Date(s.end).toLocaleString() : "—"}). Custom dates map to the nearest API window (24h / 7d / 30d).
      </p>
      <ErrorBanner message={error} onRetry={() => load(period)} />
      {loading ? <p className="mb-3 text-sm text-stone-500">Loading analytics…</p> : null}

      <h2 className="mb-2 font-display text-xl">Energy Analytics</h2>
      <EnergyChart data={dash?.energy_trend || []} />

      <h2 className="mb-2 mt-6 font-display text-xl">Solar Analytics</h2>
      <SolarChart data={dash?.solar_trend || []} />
      <div className="mt-2 overflow-x-auto text-sm">
        <table className="w-full">
          <thead className="text-xs uppercase text-stone-500">
            <tr>
              <th className="py-1 text-left">Dept</th>
              <th>kWh</th>
              <th>Irradiance</th>
            </tr>
          </thead>
          <tbody>
            {solar.map((r) => (
              <tr key={r.department}>
                <td>{r.department}</td>
                <td className="text-center">{r.solar_kwh}</td>
                <td className="text-center">{r.irradiance}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h2 className="mb-2 mt-6 font-display text-xl">Water Analytics</h2>
      <WaterChart data={dash?.water_trend || []} />
      <div className="mt-2 grid gap-2 md:grid-cols-3">
        {water.map((r) => (
          <div key={r.department} className="card p-3 text-sm">
            <div className="font-medium">{r.department}</div>
            <div>{fmt(r.water_litres)} L · flow {r.flow_rate} · pressure {r.pressure}</div>
          </div>
        ))}
      </div>

      <h2 className="mb-2 mt-6 font-display text-xl">Carbon Analytics</h2>
      <div className="grid gap-3 md:grid-cols-3">
        <div className="card p-4">
          <div className="text-xs text-stone-500">CO2 avoided ({period})</div>
          <div className="font-display text-2xl">{fmt(s.co2_avoided_kg)} kg</div>
          <div className="text-xs text-stone-500">Factor {s.co2_factor_kg_per_kwh} kg/kWh · {s.co2_factor_source}</div>
        </div>
        <div className="card p-4">
          <div className="text-xs text-stone-500">Solar contribution</div>
          <div className="font-display text-2xl">{fmt((s.solar_share || 0) * 100)}%</div>
        </div>
        <div className="card p-4">
          <div className="text-xs text-stone-500">Estimated equivalent</div>
          <div className="font-display text-2xl">~{trees} trees/yr</div>
          <div className="text-xs text-stone-500">Illustrative (21 kg CO2 / tree / year). Not a campus measurement.</div>
        </div>
      </div>

      <h2 className="mb-2 mt-6 font-display text-xl">Department Comparison</h2>
      <DepartmentTable rows={dash?.energy_by_department || []} />
      <div className="mt-3 overflow-x-auto card">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-stone-500">
            <tr>
              <th className="px-3 py-2">Dept</th>
              <th>Total</th>
              <th>Efficiency</th>
              <th>Solar</th>
              <th>Water</th>
              <th>kWh/student</th>
            </tr>
          </thead>
          <tbody>
            {scores.map((r) => (
              <tr key={r.code} className="border-t border-stone-100 dark:border-white/10">
                <td className="px-3 py-2">{r.code}</td>
                <td>{r.total_score}</td>
                <td>{r.energy_efficiency}</td>
                <td>{r.solar_score}</td>
                <td>{r.water_score}</td>
                <td>{r.kwh_per_student}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
