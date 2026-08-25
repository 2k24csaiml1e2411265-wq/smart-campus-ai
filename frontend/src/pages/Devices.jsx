import { useEffect, useState } from "react";
import { CampusAPI } from "../services/api.js";
import DeviceStatus from "../components/DeviceStatus.jsx";
import ErrorBanner from "../components/ErrorBanner.jsx";

export default function Devices() {
  const [payload, setPayload] = useState({ devices: [], counts: {} });
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const { data } = await CampusAPI.deviceStatus();
      setPayload(data);
    } catch {
      setError("Could not load device status.");
    }
  };

  useEffect(() => {
    load();
    const id = setInterval(load, 20000);
    return () => clearInterval(id);
  }, []);

  return (
    <div>
      <h1 className="mb-2 font-display text-3xl">Devices</h1>
      <p className="mb-4 text-sm text-stone-500">Simulated meters and environmental sensors. Status is derived from last heartbeat.</p>
      <ErrorBanner message={error} onRetry={load} />
      <DeviceStatus devices={payload.devices || []} counts={payload.counts} />
    </div>
  );
}
