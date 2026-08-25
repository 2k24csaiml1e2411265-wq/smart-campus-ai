import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

export default function DepartmentTable({ rows = [], highlight }) {
  return (
    <div className="card p-4">
      <h3 className="mb-3 font-display text-lg">Energy by Department</h3>
      <div className="h-56">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={rows}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
            <XAxis dataKey="code" />
            <YAxis />
            <Tooltip />
            <Bar dataKey="energy_kwh" fill="#0f766e" radius={[6, 6, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-3 overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="text-xs uppercase text-stone-500">
            <tr>
              <th className="py-2">Dept</th>
              <th>Energy</th>
              <th>Solar</th>
              <th>Water</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <tr key={r.code} className={highlight === r.code ? "bg-rose-100/70 dark:bg-rose-500/20" : ""}>
                <td className="py-1.5 font-medium">{r.code}</td>
                <td>{r.energy_kwh} kWh</td>
                <td>{r.solar_kwh} kWh</td>
                <td>{r.water_litres} L</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
