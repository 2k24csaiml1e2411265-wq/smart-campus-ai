import { Area, CartesianGrid, ComposedChart, Line, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function ForecastChart({ data = [] }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 font-display text-lg">Energy Forecast</h3>
      <div className="h-72">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
            <XAxis dataKey="label" />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="upper_bound" stroke="none" fill="#99f6e4" fillOpacity={0.35} />
            <Area type="monotone" dataKey="lower_bound" stroke="none" fill="#f4f1ea" fillOpacity={1} />
            <Line type="monotone" dataKey="predicted_kwh" stroke="#0f766e" strokeWidth={2} dot={false} />
            <Line type="monotone" dataKey="actual" stroke="#b45309" strokeWidth={2} dot={false} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
      <p className="mt-2 text-xs text-stone-500">Shaded band is the model confidence interval (lower/upper bound).</p>
    </div>
  );
}
