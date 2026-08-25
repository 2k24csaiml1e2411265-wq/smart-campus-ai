import { useEffect, useState } from "react";
import { CampusAPI } from "../services/api.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { fmt } from "../utils/format.js";
import { useAuth } from "../hooks/useAuth.jsx";

export default function Departments() {
  const { session } = useAuth();
  const [rows, setRows] = useState([]);
  const [selected, setSelected] = useState(session?.department_code || null);
  const [detail, setDetail] = useState(null);
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const { data } = await CampusAPI.departments();
      const scoped =
        session?.role === "department_manager" && session.department_code
          ? data.filter((d) => d.code === session.department_code)
          : data;
      setRows(scoped);
      if (scoped[0] && !selected) setSelected(scoped[0].code);
    } catch {
      setError("Could not load departments.");
    }
  };

  useEffect(() => {
    load();
  }, []);

  useEffect(() => {
    if (!selected) return;
    CampusAPI.department(selected, "7d")
      .then(({ data }) => setDetail(data))
      .catch(() => setError("Unknown or unavailable department."));
  }, [selected]);

  const score = detail?.score;
  const summary = detail?.summary || {};

  return (
    <div>
      <h1 className="mb-4 font-display text-3xl">Departments</h1>
      <ErrorBanner message={error} onRetry={load} />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="card overflow-hidden lg:col-span-1">
          {rows.map((d) => (
            <button
              key={d.code}
              type="button"
              onClick={() => setSelected(d.code)}
              className={`block w-full border-b border-stone-100 px-4 py-3 text-left dark:border-white/10 ${selected === d.code ? "bg-emerald-50 dark:bg-emerald-900/30" : ""}`}
            >
              <div className="font-medium">{d.code}</div>
              <div className="text-xs text-stone-500">{d.name}</div>
            </button>
          ))}
        </div>
        <div className="card p-5 lg:col-span-2">
          {!detail ? (
            <p className="text-sm text-stone-500">Select a department.</p>
          ) : (
            <>
              <h2 className="font-display text-2xl">{detail.department.name}</h2>
              <p className="text-sm text-stone-500">
                {detail.department.building} · {fmt(detail.department.floor_area, 0)} m² · {detail.department.student_count} students · {detail.department.staff_count} staff
              </p>
              <div className="mt-4 grid grid-cols-2 gap-3 md:grid-cols-4">
                <div>
                  <div className="text-xs text-stone-500">Energy 7d</div>
                  <div className="text-xl">{fmt(summary.total_energy_kwh)}</div>
                </div>
                <div>
                  <div className="text-xs text-stone-500">Solar</div>
                  <div className="text-xl">{fmt(summary.total_solar_kwh)}</div>
                </div>
                <div>
                  <div className="text-xs text-stone-500">Water</div>
                  <div className="text-xl">{fmt(summary.total_water_litres, 0)}</div>
                </div>
                <div>
                  <div className="text-xs text-stone-500">Green score</div>
                  <div className="text-xl">{score?.total_score ?? "—"}</div>
                </div>
              </div>
              {score ? (
                <div className="mt-4 grid grid-cols-2 gap-2 text-sm md:grid-cols-3">
                  <div>Energy efficiency {score.energy_efficiency}</div>
                  <div>Energy reduction {score.energy_reduction}</div>
                  <div>Solar {score.solar_score}</div>
                  <div>Water {score.water_score}</div>
                  <div>Anomaly {score.anomaly_score}</div>
                  <div>Consistency {score.consistency_score}</div>
                  <div>kWh / student {score.kwh_per_student}</div>
                  <div>kWh / m² {score.kwh_per_sqm}</div>
                </div>
              ) : null}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
