import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { CampusAPI } from "../services/api.js";
import { useAuth } from "../hooks/useAuth.jsx";
import { useLive } from "../components/Layout.jsx";
import StatCard from "../components/StatCard.jsx";
import EnergyChart from "../components/EnergyChart.jsx";
import SolarChart from "../components/SolarChart.jsx";
import WaterChart from "../components/WaterChart.jsx";
import DepartmentTable from "../components/DepartmentTable.jsx";
import GreenScore from "../components/GreenScore.jsx";
import AnomalyCard from "../components/AnomalyCard.jsx";
import RecommendationCard from "../components/RecommendationCard.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { fmt } from "../utils/format.js";

function cacheKey(period) {
  return `sca_dashboard_cache_${period}`;
}

export default function Dashboard() {
  const { session } = useAuth();
  const navigate = useNavigate();
  const { status, lastEvent, tick } = useLive();
  const [period, setPeriod] = useState("24h");
  const [data, setData] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem(cacheKey("24h")) || "null");
    } catch {
      return null;
    }
  });
  const [error, setError] = useState("");
  const [retrying, setRetrying] = useState(false);
  const [loading, setLoading] = useState(!data);
  const [simulating, setSimulating] = useState(false);
  const [simMsg, setSimMsg] = useState("");
  const [simError, setSimError] = useState("");
  const [highlightDept, setHighlightDept] = useState(null);

  const load = useCallback(async () => {
    setError("");
    setRetrying(true);
    try {
      const { data: payload } = await CampusAPI.dashboard(period);
      setData(payload);
      localStorage.setItem(cacheKey(period), JSON.stringify(payload));
      setLoading(false);
    } catch {
      setLoading(false);
      setError("Backend unavailable. Retrying… Showing last cached snapshot if available.");
    } finally {
      setRetrying(false);
    }
  }, [period]);

  useEffect(() => {
    try {
      const cached = JSON.parse(localStorage.getItem(cacheKey(period)) || "null");
      if (cached) setData(cached);
    } catch {
      /* ignore */
    }
    setLoading(true);
    load();
  }, [load, period]);

  useEffect(() => {
    if (tick > 0) load();
  }, [tick, load]);

  useEffect(() => {
    if (!lastEvent) return;
    if (lastEvent.type === "energy") {
      if (lastEvent.anomaly?.department) setHighlightDept(lastEvent.anomaly.department);
      else if (lastEvent.department) setHighlightDept(lastEvent.department);
      load();
    }
  }, [lastEvent, load]);

  const simulate = async () => {
    setSimMsg("");
    setSimError("");
    if (!session) {
      navigate("/login", { state: { from: "/dashboard" } });
      return;
    }
    setSimulating(true);
    try {
      const { data: ev } = await CampusAPI.simulateAnomaly("ME");
      const anomaly = ev.event?.anomaly;
      const dept = anomaly?.department || ev.event?.department || "ME";
      setHighlightDept(dept);
      setSimMsg(
        anomaly
          ? `Anomaly recorded for ${dept}: actual ${anomaly.actual} vs expected ${anomaly.expected} (${anomaly.severity}).`
          : `Injected DEMO reading for ${dept}. Refreshing dashboard…`
      );
      await load();
    } catch (err) {
      const statusCode = err.response?.status;
      if (statusCode === 401 || statusCode === 403) {
        setSimError("Sign in as admin or facility manager to simulate an anomaly.");
      } else {
        setSimError("Simulation failed. The backend did not accept the request.");
      }
    } finally {
      setSimulating(false);
    }
  };

  const s = data?.summary || {};
  const highlight = highlightDept || lastEvent?.anomaly?.department || lastEvent?.department;
  const offline = status === "OFFLINE" || (Boolean(error) && !data);
  const empty = !loading && data && !(s.sample_count > 0 || (data.energy_by_department || []).length);

  return (
    <div>
      <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-3xl">Campus operations</h1>
          <p className="text-sm text-stone-500">
            LAST UPDATED {data?.last_updated ? new Date(data.last_updated).toLocaleString() : "—"}
            {offline ? " · OFFLINE MODE" : ""}
            {session ? ` · ${session.email}` : " · public aggregated view"}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {["24h", "7d", "30d"].map((p) => (
            <button
              key={p}
              type="button"
              onClick={() => setPeriod(p)}
              className={`rounded-lg px-3 py-1.5 text-sm ${period === p ? "bg-emerald-800 text-white" : "card px-3"}`}
            >
              {p}
            </button>
          ))}
          <button
            type="button"
            onClick={simulate}
            disabled={simulating}
            className="rounded-lg bg-rose-700 px-3 py-1.5 text-sm text-white disabled:opacity-60"
          >
            {simulating ? "Simulation in progress…" : "Simulate Anomaly"}
          </button>
        </div>
      </div>
      <ErrorBanner message={error} onRetry={load} />
      {simError ? <ErrorBanner message={simError} /> : null}
      {simMsg ? <p className="mb-3 text-sm text-emerald-800 dark:text-emerald-300">{simMsg}</p> : null}
      {loading ? <p className="text-sm text-stone-500">{retrying ? "Retrying…" : "Loading campus metrics…"}</p> : null}
      {empty ? <p className="text-sm text-stone-500">No readings in this window yet. Keep the simulator running or widen the period.</p> : null}
      <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-6">
        <StatCard label="Total Energy" value={fmt(s.total_energy_kwh)} unit="kWh" />
        <StatCard label="Solar Generation" value={fmt(s.total_solar_kwh)} unit="kWh" accent="amber" />
        <StatCard label="Solar Share" value={fmt((s.solar_share || 0) * 100, 1)} unit="%" accent="amber" />
        <StatCard label="Water Used" value={fmt(s.total_water_litres, 0)} unit="L" accent="sky" />
        <StatCard
          label="CO2 Avoided"
          value={fmt(s.co2_avoided_kg)}
          unit="kg"
          hint={`Factor ${s.co2_factor_kg_per_kwh ?? "—"} kg/kWh`}
        />
        <StatCard label="Active Anomalies" value={fmt(s.anomalies, 0)} accent="rose" />
      </div>
      <div className="mt-4 grid gap-4 xl:grid-cols-3">
        <div className="xl:col-span-2">
          <DepartmentTable rows={data?.energy_by_department || []} highlight={highlight} />
        </div>
        <GreenScore scores={data?.scores || []} />
      </div>
      <div className="mt-4 grid gap-4 xl:grid-cols-3">
        <EnergyChart data={data?.energy_trend || []} />
        <SolarChart data={data?.solar_trend || []} />
        <WaterChart data={data?.water_trend || []} />
      </div>
      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div>
          <h2 className="mb-2 font-display text-xl">Active Alerts</h2>
          <div className="space-y-3">
            {(data?.alerts || []).length === 0 ? (
              <p className="text-sm text-stone-500">No open anomalies in this window.</p>
            ) : null}
            {(data?.alerts || []).map((a) => (
              <AnomalyCard key={a.id} item={a} highlighted={highlight === a.department_code} />
            ))}
          </div>
        </div>
        <div>
          <h2 className="mb-2 font-display text-xl">AI Recommendations</h2>
          <div className="space-y-3">
            {(data?.recommendations || []).length === 0 ? (
              <p className="text-sm text-stone-500">Recommendations appear when anomalies are detected.</p>
            ) : null}
            {(data?.recommendations || []).map((r, i) => (
              <RecommendationCard key={i} item={r} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
