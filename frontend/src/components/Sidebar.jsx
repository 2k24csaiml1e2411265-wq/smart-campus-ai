import {
  Activity,
  Bell,
  Building2,
  Cpu,
  Gauge,
  LayoutDashboard,
  LineChart,
  Settings,
  FileText,
} from "lucide-react";
import { NavLink } from "react-router-dom";
import { canAccess, useAuth } from "../hooks/useAuth.jsx";

const LINKS = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/analytics", label: "Analytics", icon: LineChart },
  { to: "/departments", label: "Departments", icon: Building2 },
  { to: "/alerts", label: "Alerts", icon: Bell },
  { to: "/devices", label: "Devices", icon: Cpu },
  { to: "/forecast", label: "Forecast", icon: Gauge },
  { to: "/reports", label: "Reports", icon: FileText },
  { to: "/admin", label: "Admin", icon: Settings },
];

export default function Sidebar({ collapsed, onNavigate }) {
  const { session } = useAuth();
  const role = session?.role;

  const visible = LINKS.filter((l) => {
    if (!role) return l.to === "/dashboard" || l.to === "/analytics" || l.to === "/departments";
    return canAccess(role, l.to) || (role === "viewer" && ["/alerts"].includes(l.to));
  });

  return (
    <aside className={`${collapsed ? "hidden md:block md:w-16" : "fixed inset-y-16 left-3 z-20 w-56 md:static"} shrink-0`}>
      <nav className="card sticky top-20 space-y-1 p-2">
        {visible.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            onClick={onNavigate}
            className={({ isActive }) =>
              `flex items-center gap-2 rounded-xl px-3 py-2 text-sm transition-colors ${
                isActive
                  ? "bg-emerald-800 text-white"
                  : "text-stone-700 hover:bg-stone-100 dark:text-stone-200 dark:hover:bg-white/10"
              }`
            }
          >
            <l.icon size={16} />
            {!collapsed && <span>{l.label}</span>}
          </NavLink>
        ))}
        <div className="px-3 pt-3 text-[11px] leading-relaxed text-stone-500">
          <Activity size={12} className="mb-1 inline" /> DEMO/SIMULATED readings unless a live sensor feed is connected.
        </div>
      </nav>
    </aside>
  );
}
