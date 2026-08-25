import { useEffect, useState } from "react";
import { CampusAPI } from "../services/api.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { useLive } from "../components/Layout.jsx";
import { downloadBlob } from "../utils/format.js";

export default function Admin() {
  const { lastEvent } = useLive();
  const [health, setHealth] = useState(null);
  const [department, setDepartment] = useState("ME");
  const [departments, setDepartments] = useState([]);
  const [devices, setDevices] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [period, setPeriod] = useState("7d");

  const refreshHealth = () =>
    CampusAPI.health()
      .then(({ data }) => setHealth(data))
      .catch(() => setError("Health endpoint unreachable."));

  const load = () => {
    refreshHealth();
    CampusAPI.departments()
      .then(({ data }) => setDepartments(data))
      .catch(() => {});
    CampusAPI.devices()
      .then(({ data }) => setDevices(data))
      .catch(() => {});
  };

  useEffect(() => {
    load();
  }, []);

  const simulate = async () => {
    setError("");
    try {
      const { data } = await CampusAPI.simulateAnomaly(department);
      setMessage(`Anomaly injected for ${department}. Alert id ${data.event?.anomaly?.id ?? "pending"}.`);
      refreshHealth();
    } catch (err) {
      setError(err.response?.data?.detail || "Simulate anomaly failed.");
    }
  };

  const retrain = async () => {
    try {
      const { data } = await CampusAPI.retrain();
      setMessage(data.trained ? "Models retrained from current history." : data.reason || "Retrain skipped.");
    } catch {
      setError("Retrain requires admin role and sufficient history.");
    }
  };

  const exportFmt = async (fmt) => {
    try {
      const res = await CampusAPI.report(period, fmt);
      if (fmt === "json") {
        downloadBlob(new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" }), `campus-${period}.json`);
      } else {
        downloadBlob(res.data, fmt === "pdf" ? `smart-campus-${period}.pdf` : `campus-${period}.csv`);
      }
    } catch {
      setError("Export failed.");
    }
  };

  return (
    <div>
      <h1 className="mb-2 font-display text-3xl">Admin</h1>
      <p className="mb-4 text-sm text-stone-500">
        Demo controls. The IoT simulator is a separate process; health.simulator reflects last ingest. Thresholds are applied in the ML pipeline, not as unrestricted raw kWh ranks.
      </p>
      <ErrorBanner message={error} onRetry={load} />
      {message ? <p className="mb-3 text-sm text-emerald-800 dark:text-emerald-300">{message}</p> : null}
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="card p-4">
          <h2 className="font-display text-lg">System health</h2>
          {health ? (
            <dl className="mt-2 grid grid-cols-2 gap-2 text-sm">
              <div>API {health.api}</div>
              <div>Database {health.database}</div>
              <div>MQTT {health.mqtt}</div>
              <div>ML {health.ml}</div>
              <div>Simulator {health.simulator}</div>
              <div>Last data {health.last_data_timestamp || "—"}</div>
            </dl>
          ) : (
            <p className="text-sm text-stone-500">Loading health…</p>
          )}
        </div>
        <div className="card space-y-3 p-4">
          <h2 className="font-display text-lg">Demo scenario</h2>
          <p className="text-sm text-stone-500">Generate abnormal energy → store reading → Isolation Forest → alert, explanation, recommendation.</p>
          <select className="card px-3 py-2" value={department} onChange={(e) => setDepartment(e.target.value)}>
            {departments.map((d) => (
              <option key={d.code}>{d.code}</option>
            ))}
          </select>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={simulate} className="rounded-lg bg-rose-700 px-4 py-2 text-white">
              Simulate Anomaly
            </button>
            <button type="button" onClick={retrain} className="rounded-lg border border-stone-300 px-4 py-2 dark:border-white/20">
              Retrain models
            </button>
          </div>
          {lastEvent?.anomaly ? (
            <div className="rounded-xl bg-rose-50 p-3 text-sm dark:bg-rose-500/10">
              Live: {lastEvent.anomaly.department} score {lastEvent.anomaly.anomaly_score}
            </div>
          ) : null}
        </div>
        <div className="card p-4">
          <h2 className="font-display text-lg">Departments</h2>
          <ul className="mt-2 max-h-56 overflow-auto text-sm">
            {departments.map((d) => (
              <li key={d.code} className="border-b border-stone-100 py-1 dark:border-white/10">
                {d.code} · {d.building} · {d.student_count} students · {d.active ? "active" : "inactive"}
              </li>
            ))}
          </ul>
        </div>
        <div className="card p-4">
          <h2 className="font-display text-lg">Devices</h2>
          <p className="text-xs text-stone-500">{devices.length} registered meters / sensors</p>
          <ul className="mt-2 max-h-56 overflow-auto font-mono text-xs">
            {devices.slice(0, 20).map((d) => (
              <li key={d.device_id}>
                {d.device_id} {d.status}
              </li>
            ))}
          </ul>
        </div>
        <div className="card space-y-2 p-4 lg:col-span-2">
          <h2 className="font-display text-lg">Export & reports</h2>
          <select className="card px-3 py-2" value={period} onChange={(e) => setPeriod(e.target.value)}>
            <option value="24h">24h</option>
            <option value="7d">7d</option>
            <option value="30d">30d</option>
          </select>
          <div className="flex flex-wrap gap-2">
            <button type="button" onClick={() => exportFmt("pdf")} className="rounded-lg bg-emerald-800 px-3 py-2 text-white">
              PDF
            </button>
            <button type="button" onClick={() => exportFmt("csv")} className="rounded-lg border px-3 py-2">
              CSV
            </button>
            <button type="button" onClick={() => exportFmt("json")} className="rounded-lg border px-3 py-2">
              JSON
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
