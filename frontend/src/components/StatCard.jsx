export default function StatCard({ label, value, unit, hint, accent = "emerald" }) {
  const tones = {
    emerald: "from-emerald-700/10 to-transparent",
    amber: "from-amber-600/10 to-transparent",
    sky: "from-sky-600/10 to-transparent",
    rose: "from-rose-600/10 to-transparent",
  };
  return (
    <div className={`card relative overflow-hidden p-4 bg-gradient-to-br ${tones[accent] || tones.emerald}`}>
      <div className="text-xs uppercase tracking-wide text-stone-500">{label}</div>
      <div className="mt-1 font-display text-2xl">
        {value}
        {unit ? <span className="ml-1 text-sm font-sans text-stone-500">{unit}</span> : null}
      </div>
      {hint ? <div className="mt-1 text-xs text-stone-500">{hint}</div> : null}
    </div>
  );
}
