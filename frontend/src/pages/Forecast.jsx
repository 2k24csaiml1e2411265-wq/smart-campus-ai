import { useEffect, useMemo, useState } from "react";
import { CampusAPI } from "../services/api.js";
import ForecastChart from "../components/ForecastChart.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { fmt } from "../utils/format.js";
import { useAuth } from "../hooks/useAuth.jsx";

export default function Forecast() {
  const { session } = useAuth();
  const locked = session?.role === "department_manager" ? session.department_code : null;
  const [dept, setDept] = useState(locked || "CSE");
  const [departments, setDepartments] = useState([]);
  const [rows, setRows] = useState([]);
  const [latest, setLatest] = useState(null);
  const [trend, setTrend] = useState([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    CampusAPI.departments()
      .then(({ data }) => setDepartments(locked ? data.filter((d) => d.code === locked) : data))
      .catch(() => setError("Could not load departments."));
  }, [locked]);

  const load = async () => {
    setError("");
    setLoading(true);
    try {
      const [f, e, t] = await Promise.all([
        CampusAPI.forecasts(dept),
        CampusAPI.energyLatest(),
        CampusAPI.energyTrend(dept, "24h"),
      ]);
      const list = (f.data || []).filter((r) => r.department_code === dept);
      setRows(list);
      setLatest((e.data || []).find((r) => r.department === dept) || null);
      setTrend(t.data || []);
    } catch {
      setError("Forecast service unavailable.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, [dept]);

  const chart = useMemo(() => {
    const lastActual = trend.length ? trend[trend.length - 1].energy_kwh : latest?.energy_kwh;
    return rows.map((r) => ({
      label: `+${r.horizon_hours}h`,
      predicted_kwh: r.predicted_kwh,
      lower_bound: r.lower_bound,
      upper_bound: r.upper_bound,
      actual: lastActual,
    }));
  }, [rows, trend, latest]);

  const peak = rows.reduce((a, b) => (!a || b.predicted_kwh > a.predicted_kwh ? b : a), null);
  const low = rows.reduce((a, b) => (!a || b.predicted_kwh < a.predicted_kwh ? b : a), null);
  const next = rows.find((r) => r.horizon_hours === 1) || rows[0];

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl">Energy Forecast</h1>
          <p className="text-sm text-stone-500">
            Next 24 hours · {next?.model_name || "model pending"} · confidence {next ? Math.round((next.confidence || 0) * 100) : "—"}%
          </p>
        </div>
        <select className="card px-3 py-2" value={dept} onChange={(e) => setDept(e.target.value)} disabled={Boolean(locked)}>
          {(departments.length ? departments : [{ code: dept }]).map((d) => (
            <option key={d.code} value={d.code}>
              {d.code}
            </option>
          ))}
        </select>
      </div>
      <ErrorBanner message={error} onRetry={load} />
      {loading ? <p className="mb-3 text-sm text-stone-500">Loading forecast…</p> : null}
      <div className="mb-4 grid gap-3 md:grid-cols-4">
        <div className="card p-4">
          <div className="text-xs text-stone-500">{dept} · Current</div>
          <div className="font-display text-2xl">{fmt(latest?.energy_kwh)} kWh</div>
        </div>
        <div className="card p-4">
          <div className="text-xs text-stone-500">Forecast</div>
          <div className="font-display text-2xl">{fmt(next?.predicted_kwh)} kWh</div>
        </div>
        <div className="card p-4">
          <div className="text-xs text-stone-500">Expected Peak</div>
          <div className="font-display text-2xl">
            {peak ? new Date(peak.forecast_for).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-xs text-stone-500">Expected low</div>
          <div className="font-display text-2xl">
            {low ? new Date(low.forecast_for).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "—"}
          </div>
        </div>
      </div>
      <ForecastChart data={chart} />
      <p className="mt-2 text-xs text-stone-500">Actual vs predicted uses the latest meter reading as the actual series reference. Band is lower/upper bound from the model.</p>
    </div>
  );
}
