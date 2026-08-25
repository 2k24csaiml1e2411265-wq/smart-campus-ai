import axios from "axios";

const baseURL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export const api = axios.create({
  baseURL,
  timeout: 12000,
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("sca_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export function getApiBase() {
  return baseURL;
}

export const CampusAPI = {
  health: () => api.get("/api/health"),
  login: (email, password) => api.post("/api/auth/login", { email, password }),
  dashboard: (period = "24h") => api.get("/api/dashboard", { params: { period } }),
  summary: (period) => api.get("/api/summary", { params: { period } }),
  departments: () => api.get("/api/departments"),
  department: (code, period) => api.get(`/api/departments/${code}`, { params: { period } }),
  scores: (period = "7d") => api.get("/api/scores", { params: { period } }),
  energyLatest: () => api.get("/api/energy/latest"),
  energyTrend: (dept, period) => api.get(`/api/energy/trend/${dept}`, { params: { period } }),
  energyHistory: (dept, page = 1) => api.get(`/api/energy/history/${dept}`, { params: { page } }),
  solarLatest: () => api.get("/api/solar/latest"),
  waterLatest: () => api.get("/api/water/latest"),
  anomalies: (params) => api.get("/api/anomalies", { params }),
  updateAnomaly: (id, status) => api.patch(`/api/anomalies/${id}`, { status }),
  forecasts: (department) => api.get("/api/forecasts", { params: { department } }),
  recommendations: () => api.get("/api/recommendations"),
  devices: () => api.get("/api/devices"),
  deviceStatus: () => api.get("/api/devices/status"),
  simulateAnomaly: (department = "ME") => api.post(`/api/simulator/anomaly?department=${department}`),
  retrain: () => api.post("/api/ml/retrain"),
  report: (period, fmt) =>
    api.post("/api/reports/generate", null, {
      params: { period, fmt },
      responseType: fmt === "json" ? "json" : "blob",
    }),
  export: (period, fmt) =>
    api.get("/api/export", { params: { period, fmt }, responseType: fmt === "json" ? "json" : "blob" }),
};
