const SEV = {
  low: "bg-stone-200 text-stone-800",
  medium: "bg-amber-100 text-amber-900",
  high: "bg-orange-100 text-orange-900",
  critical: "bg-rose-100 text-rose-900",
};

export default function AnomalyCard({ item, highlighted }) {
  if (!item) return null;
  const dev =
    item.deviation_pct ??
    (item.expected_value ? ((item.actual_value - item.expected_value) / item.expected_value) * 100 : 0);
  return (
    <div className={`card p-4 ${highlighted ? "ring-2 ring-rose-500" : ""}`}>
      <div className="flex items-center justify-between gap-2">
        <span className={`chip ${SEV[item.severity] || SEV.medium}`}>{item.severity}</span>
        <span className="text-xs text-stone-500">{item.department_code}</span>
      </div>
      <div className="mt-2 text-sm font-medium">
        {item.metric} · actual {item.actual_value} / expected {item.expected_value}
      </div>
      <div className="text-xs text-stone-500">Deviation {Number(dev).toFixed(1)}%</div>
      <p className="mt-2 whitespace-pre-line text-sm text-stone-700 dark:text-stone-300">{item.reason}</p>
    </div>
  );
}
