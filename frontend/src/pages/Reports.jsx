import { useState } from "react";
import { CampusAPI } from "../services/api.js";
import ErrorBanner from "../components/ErrorBanner.jsx";
import { downloadBlob } from "../utils/format.js";

export default function Reports() {
  const [period, setPeriod] = useState("7d");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const run = async (fmt) => {
    setBusy(true);
    setError("");
    try {
      const res = await CampusAPI.report(period, fmt);
      if (fmt === "json") {
        downloadBlob(new Blob([JSON.stringify(res.data, null, 2)], { type: "application/json" }), `campus-${period}.json`);
      } else {
        const name = fmt === "pdf" ? `smart-campus-${period}.pdf` : `campus-${period}.csv`;
        downloadBlob(res.data, name);
      }
    } catch {
      setError("Report generation failed. Sign in as facility manager or admin.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-2xl">
      <h1 className="mb-2 font-display text-3xl">Reports</h1>
      <p className="mb-4 text-sm text-stone-500">Sustainability pack for the selected window: energy, solar, water, CO2 avoided, Green Score, anomalies.</p>
      <ErrorBanner message={error} />
      <label className="text-sm">
        Period
        <select className="card ml-2 px-3 py-2" value={period} onChange={(e) => setPeriod(e.target.value)}>
          <option value="24h">24 hours</option>
          <option value="7d">7 days</option>
          <option value="30d">30 days</option>
        </select>
      </label>
      <div className="mt-4 flex flex-wrap gap-2">
        <button type="button" disabled={busy} onClick={() => run("pdf")} className="rounded-lg bg-emerald-800 px-4 py-2 text-white">
          Download PDF
        </button>
        <button type="button" disabled={busy} onClick={() => run("csv")} className="rounded-lg border border-stone-300 px-4 py-2 dark:border-white/20">
          CSV
        </button>
        <button type="button" disabled={busy} onClick={() => run("json")} className="rounded-lg border border-stone-300 px-4 py-2 dark:border-white/20">
          JSON
        </button>
      </div>
    </div>
  );
}
