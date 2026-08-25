import { Outlet } from "react-router-dom";
import { createContext, useContext, useEffect, useState } from "react";
import Navbar from "./Navbar.jsx";
import Sidebar from "./Sidebar.jsx";
import { useRealtime } from "../hooks/useRealtime.js";
import { CampusAPI } from "../services/api.js";

const LiveCtx = createContext({
  status: "CONNECTING",
  campus: "PSIT Kanpur",
  dataMode: "DEMO",
  lastEvent: null,
  tick: 0,
});
export const useLive = () => useContext(LiveCtx);

export default function Layout() {
  const [dark, setDark] = useState(() => localStorage.getItem("sca_theme") === "dark");
  const [collapsed, setCollapsed] = useState(false);
  const [meta, setMeta] = useState({ campus: "PSIT Kanpur", dataMode: "DEMO" });
  const [lastEvent, setLastEvent] = useState(null);
  const [tick, setTick] = useState(0);

  const status = useRealtime((ev) => {
    if (ev?.type === "poll") {
      setTick((n) => n + 1);
      return;
    }
    if (ev?.type && ev.type !== "hello") setLastEvent(ev);
  });

  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    localStorage.setItem("sca_theme", dark ? "dark" : "light");
  }, [dark]);

  useEffect(() => {
    CampusAPI.health()
      .then(({ data }) =>
        setMeta({ campus: data.campus || "PSIT Kanpur", dataMode: data.data_mode || "DEMO" })
      )
      .catch(() => {});
  }, []);

  const displayStatus = status === "LIVE" ? "LIVE" : status;

  return (
    <LiveCtx.Provider value={{ status: displayStatus, lastEvent, tick, ...meta }}>
      <div className="app-shell min-h-screen">
        <Navbar
          dark={dark}
          onToggleTheme={() => setDark((v) => !v)}
          onMenu={() => setCollapsed((v) => !v)}
          liveStatus={displayStatus}
          campus={meta.campus}
          dataMode={meta.dataMode}
        />
        <div className="mx-auto flex max-w-[1600px] gap-4 px-3 pb-8 pt-4 md:px-6">
          <Sidebar collapsed={collapsed} onNavigate={() => setCollapsed(true)} />
          <main className="min-w-0 flex-1 animate-fade">
            <Outlet />
          </main>
        </div>
      </div>
    </LiveCtx.Provider>
  );
}
