export function fmt(n, digits = 1) {
  if (n == null || Number.isNaN(n)) return "—";
  return Number(n).toLocaleString(undefined, { maximumFractionDigits: digits });
}

export function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

export function statusTone(status) {
  if (status === "LIVE" || status === "CONNECTED") return "bg-emerald-500";
  if (status === "DEGRADED") return "bg-amber-400";
  return "bg-slate-400";
}
