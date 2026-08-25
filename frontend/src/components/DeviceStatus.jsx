const COLOR = {
  ONLINE: "bg-emerald-500",
  WARNING: "bg-amber-400",
  OFFLINE: "bg-stone-400",
};

export default function DeviceStatus({ devices = [], counts }) {
  return (
    <div className="card overflow-hidden">
      <div className="flex items-center justify-between p-4">
        <h3 className="font-display text-lg">Device heartbeat</h3>
        {counts ? (
          <div className="flex gap-2 text-xs">
            {Object.entries(counts).map(([k, v]) => (
              <span key={k} className="chip bg-stone-100 dark:bg-white/10">
                {k} {v}
              </span>
            ))}
          </div>
        ) : null}
      </div>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-stone-50 text-xs uppercase text-stone-500 dark:bg-white/5">
            <tr>
              <th className="px-4 py-2">Device ID</th>
              <th>Department</th>
              <th>Type</th>
              <th>Status</th>
              <th>Last seen</th>
              <th>Value</th>
              <th>Health</th>
            </tr>
          </thead>
          <tbody>
            {devices.map((d) => (
              <tr key={d.device_id} className="border-t border-stone-100 dark:border-white/10">
                <td className="px-4 py-2 font-mono text-xs">{d.device_id}</td>
                <td>{d.department_code}</td>
                <td>{d.device_type}</td>
                <td>
                  <span className="inline-flex items-center gap-1">
                    <span className={`h-2 w-2 rounded-full ${COLOR[d.status] || COLOR.OFFLINE}`} />
                    {d.status}
                  </span>
                </td>
                <td className="text-xs">{d.last_seen ? new Date(d.last_seen).toLocaleString() : "—"}</td>
                <td>{d.last_value ?? "—"}</td>
                <td>{d.health}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
