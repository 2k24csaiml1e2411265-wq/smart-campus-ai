export default function GreenScore({ scores = [] }) {
  return (
    <div className="card p-4">
      <h3 className="mb-1 font-display text-lg">Green Score Leaderboard</h3>
      <p className="mb-3 text-xs text-stone-500">Normalized 0–99. Not ranked by raw kWh.</p>
      <ol className="space-y-2">
        {scores.map((s, i) => (
          <li key={s.code} className="flex items-center gap-3">
            <span className="w-6 text-sm text-stone-500">{i + 1}</span>
            <div className="min-w-0 flex-1">
              <div className="flex justify-between text-sm">
                <span className="font-medium">{s.code}</span>
                <span>{s.total_score}</span>
              </div>
              <div className="mt-1 h-1.5 overflow-hidden rounded-full bg-stone-200 dark:bg-white/10">
                <div className="h-full bg-emerald-700" style={{ width: `${Math.min(100, s.total_score)}%` }} />
              </div>
            </div>
          </li>
        ))}
      </ol>
    </div>
  );
}
