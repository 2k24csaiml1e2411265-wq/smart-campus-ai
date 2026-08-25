import { Leaf, Menu, Moon, Sun } from "lucide-react";
import { Link } from "react-router-dom";
import { useAuth } from "../hooks/useAuth.jsx";
import { statusTone } from "../utils/format.js";

export default function Navbar({
  dark,
  onToggleTheme,
  onMenu,
  liveStatus = "LIVE",
  campus = "PSIT Kanpur",
  dataMode = "DEMO",
}) {
  const { session, logout } = useAuth();
  const label = liveStatus === "LIVE" ? "LIVE" : liveStatus === "CONNECTING" ? "CONNECTING" : liveStatus;

  return (
    <header className="sticky top-0 z-30 border-b border-stone-200/70 bg-[#f4f1ea]/90 backdrop-blur dark:border-white/10 dark:bg-canopy-950/80">
      <div className="mx-auto flex max-w-[1600px] items-center justify-between gap-3 px-3 py-3 md:px-6">
        <div className="flex items-center gap-3">
          <button type="button" className="rounded-lg p-2 hover:bg-stone-200/60 md:hidden" onClick={onMenu} aria-label="Menu">
            <Menu size={18} />
          </button>
          <Link to="/dashboard" className="flex items-center gap-2">
            <span className="grid h-9 w-9 place-items-center rounded-xl bg-emerald-800 text-white">
              <Leaf size={18} />
            </span>
            <div>
              <div className="font-display text-lg leading-none">Smart Campus AI</div>
              <div className="text-[11px] text-stone-500 dark:text-stone-400">Energy, Water & Sustainability Intelligence</div>
            </div>
          </Link>
        </div>
        <div className="hidden items-center gap-4 md:flex">
          <div className="flex items-center gap-2 text-sm" title="WebSocket LIVE; polling fallback when DEGRADED">
            <span className={`h-2.5 w-2.5 rounded-full ${statusTone(liveStatus)} ${liveStatus === "LIVE" ? "animate-pulse" : ""}`} />
            <span className="font-medium">{label}</span>
          </div>
          <div className="text-sm text-stone-600 dark:text-stone-300">
            Current campus: <span className="font-medium text-emerald-800 dark:text-emerald-300">{campus}</span>
          </div>
          <span className="chip bg-amber-100 text-amber-900 dark:bg-amber-500/20 dark:text-amber-200">{dataMode} DATA</span>
        </div>
        <div className="flex items-center gap-2">
          <button type="button" onClick={onToggleTheme} className="rounded-lg p-2 hover:bg-stone-200/70 dark:hover:bg-white/10" aria-label="Toggle theme">
            {dark ? <Sun size={16} /> : <Moon size={16} />}
          </button>
          {session ? (
            <div className="flex items-center gap-2">
              <div className="hidden text-right text-xs sm:block">
                <div className="font-medium">{session.email}</div>
                <div className="uppercase text-stone-500">{session.role?.replaceAll("_", " ")}</div>
              </div>
              <button type="button" onClick={logout} className="rounded-lg border border-stone-300 px-3 py-1.5 text-sm dark:border-white/20">
                Sign out
              </button>
            </div>
          ) : (
            <Link to="/login" className="rounded-lg bg-emerald-800 px-3 py-1.5 text-sm text-white">
              Sign in
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
