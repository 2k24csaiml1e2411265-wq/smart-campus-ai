import { useEffect, useState } from "react";
import { CampusAPI } from "../services/api.js";
import AnomalyCard from "../components/AnomalyCard.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { useAuth } from "../hooks/useAuth.jsx";
import { useLive } from "../components/Layout.jsx";

export default function Alerts() {
  const { session } = useAuth();
  const { lastEvent, tick } = useLive();
  const [rows, setRows] = useState([]);
  const [severity, setSeverity] = useState("");
  const [status, setStatus] = useState("");
  const [dept, setDept] = useState(session?.role === "department_manager" ? session.department_code || "" : "");
  const [error, setError] = useState("");

  const load = async () => {
    setError("");
    try {
      const { data } = await CampusAPI.anomalies({
        ...(severity ? { severity } : {}),
        ...(status ? { status } : {}),
        ...(dept ? { department: dept } : {}),
      });
      setRows(data);
    } catch {
      setError("Could not load anomalies.");
    }
  };

  useEffect(() => {
    load();
  }, [severity, status, dept, tick, lastEvent]);

  const act = async (id, next) => {
    try {
      await CampusAPI.updateAnomaly(id, next);
      load();
    } catch {
      setError("Update requires facility, department manager, or admin role.");
    }
  };

  const canAct = session && session.role !== "viewer";

  return (
    <div>
      <h1 className="mb-4 font-display text-3xl">Anomaly center</h1>
      <ErrorBanner message={error} onRetry={load} />
      <div className="mb-4 flex flex-wrap gap-2">
        <select className="card px-3 py-2 text-sm" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          <option value="">All severities</option>
          {["low", "medium", "high", "critical"].map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        <select className="card px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value)}>
          <option value="">All statuses</option>
          {["open", "acknowledged", "resolved"].map((s) => (
            <option key={s}>{s}</option>
          ))}
        </select>
        {session?.role !== "department_manager" ? (
          <input
            className="card px-3 py-2 text-sm uppercase"
            placeholder="Dept filter"
            value={dept}
            onChange={(e) => setDept(e.target.value.toUpperCase())}
          />
        ) : null}
      </div>
      <div className="card overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-stone-500">
            <tr>
              <th className="px-3 py-2">Severity</th>
              <th>Dept</th>
              <th>Metric</th>
              <th>Actual</th>
              <th>Expected</th>
              <th>Deviation</th>
              <th>AI score</th>
              <th>Reason</th>
              <th>Status</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {rows.length === 0 ? (
              <tr>
                <td className="px-3 py-6 text-stone-500" colSpan={10}>
                  No anomalies for this filter.
                </td>
              </tr>
            ) : null}
            {rows.map((r) => (
              <tr key={r.id} className="border-t border-stone-100 align-top dark:border-white/10">
                <td className="px-3 py-2">{r.severity}</td>
                <td>{r.department_code}</td>
                <td>{r.metric}</td>
                <td>{r.actual_value}</td>
                <td>{r.expected_value}</td>
                <td>{r.deviation_pct}%</td>
                <td>{r.anomaly_score}</td>
                <td className="max-w-xs whitespace-pre-line text-xs">{r.reason}</td>
                <td>{r.status}</td>
                <td className="space-x-1 py-2">
                  {canAct ? (
                    <>
                      <button type="button" className="text-xs underline" onClick={() => act(r.id, "acknowledged")}>
                        Acknowledge
                      </button>
                      <button type="button" className="text-xs underline" onClick={() => act(r.id, "resolved")}>
                        Mark resolved
                      </button>
                    </>
                  ) : null}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        {rows.slice(0, 4).map((r) => (
          <div key={r.id}>
            <AnomalyCard item={r} highlighted={lastEvent?.anomaly?.id === r.id} />
            <p className="mt-1 px-1 text-xs text-stone-500">Recommendation: {r.recommendation}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
