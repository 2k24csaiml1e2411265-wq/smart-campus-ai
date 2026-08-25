import { Line, LineChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function SolarChart({ data = [] }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 font-display text-lg">Solar Generation</h3>
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
            <XAxis dataKey="timestamp" tickFormatter={(v) => String(v).slice(11, 16)} />
            <YAxis />
            <Tooltip />
            <Line type="monotone" dataKey="solar_kwh" stroke="#ca8a04" strokeWidth={2} dot={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
