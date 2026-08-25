import { useEffect, useRef, useState } from "react";
import { getApiBase } from "../services/api";

export function useRealtime(onEvent) {
  const [status, setStatus] = useState("CONNECTING");
  const retry = useRef(0);
  const cb = useRef(onEvent);
  cb.current = onEvent;

  useEffect(() => {
    let ws;
    let poll;
    let stopped = false;

    const connect = () => {
      const http = getApiBase();
      const url = http.replace(/^http/, "ws") + "/api/ws";
      try {
        ws = new WebSocket(url);
      } catch {
        setStatus("DEGRADED");
        return;
      }
      ws.onopen = () => {
        retry.current = 0;
        setStatus("LIVE");
      };
      ws.onmessage = (ev) => {
        try {
          cb.current?.(JSON.parse(ev.data));
        } catch {
          /* ignore */
        }
      };
      ws.onclose = () => {
        if (stopped) return;
        setStatus(retry.current > 2 ? "DEGRADED" : "CONNECTING");
        retry.current += 1;
        setTimeout(connect, Math.min(8000, 1000 * retry.current));
      };
      ws.onerror = () => {
        setStatus("DEGRADED");
        ws.close();
      };
    };

    connect();
    poll = setInterval(() => {
      if (status === "OFFLINE") return;
      cb.current?.({ type: "poll" });
    }, 20000);

    const onOffline = () => setStatus("OFFLINE");
    const onOnline = () => setStatus("CONNECTING");
    window.addEventListener("offline", onOffline);
    window.addEventListener("online", onOnline);

    return () => {
      stopped = true;
      ws?.close();
      clearInterval(poll);
      window.removeEventListener("offline", onOffline);
      window.removeEventListener("online", onOnline);
    };
  }, []);

  return status;
}
