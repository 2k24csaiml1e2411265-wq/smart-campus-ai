export default function RecommendationCard({ item }) {
  if (!item) return null;
  return (
    <div className="card p-4">
      <div className="text-[11px] uppercase tracking-wide text-emerald-800 dark:text-emerald-300">{item.type || "ACTION"}</div>
      <div className="mt-1 font-medium">{item.title}</div>
      <p className="mt-1 text-sm text-stone-600 dark:text-stone-300">{item.recommendation}</p>
      {item.department ? <div className="mt-2 text-xs text-stone-500">{item.department}</div> : null}
    </div>
  );
}
