import { Area, AreaChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function WaterChart({ data = [] }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 font-display text-lg">Water Consumption</h3>
      <div className="h-52">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.25} />
            <XAxis dataKey="timestamp" tickFormatter={(v) => String(v).slice(11, 16)} />
            <YAxis />
            <Tooltip />
            <Area type="monotone" dataKey="water_litres" stroke="#0369a1" fill="#7dd3fc" fillOpacity={0.35} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
