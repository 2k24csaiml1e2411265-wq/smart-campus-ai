import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function EnergyChart({ data = [] }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 font-display text-lg">24-hour Energy Trend</h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
            <XAxis dataKey="timestamp" tickFormatter={(v) => String(v).slice(11, 16) || String(v).slice(0, 10)} />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="energy_kwh" stroke="#115e59" fill="#99f6e4" fillOpacity={0.45} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
