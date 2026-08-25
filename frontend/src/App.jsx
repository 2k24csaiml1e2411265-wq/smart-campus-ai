import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import { canAccess, useAuth } from "./hooks/useAuth.jsx";
import Admin from "./pages/Admin.jsx";
import Alerts from "./pages/Alerts.jsx";
import Analytics from "./pages/Analytics.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Departments from "./pages/Departments.jsx";
import Devices from "./pages/Devices.jsx";
import Forecast from "./pages/Forecast.jsx";
import Login from "./pages/Login.jsx";
import Reports from "./pages/Reports.jsx";

function Guard({ children, roles }) {
  const { session } = useAuth();
  const location = useLocation();
  if (!session) return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  if (roles && !roles.includes(session.role)) return <Navigate to="/dashboard" replace />;
  if (!canAccess(session.role, location.pathname) && location.pathname.startsWith("/admin")) {
    return <Navigate to="/dashboard" replace />;
  }
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/departments" element={<Departments />} />
        <Route
          path="/alerts"
          element={
            <Guard roles={["admin", "facility_manager", "department_manager", "viewer"]}>
              <Alerts />
            </Guard>
          }
        />
        <Route
          path="/devices"
          element={
            <Guard roles={["admin", "facility_manager", "department_manager"]}>
              <Devices />
            </Guard>
          }
        />
        <Route
          path="/forecast"
          element={
            <Guard roles={["admin", "facility_manager", "department_manager"]}>
              <Forecast />
            </Guard>
          }
        />
        <Route
          path="/reports"
          element={
            <Guard roles={["admin", "facility_manager", "department_manager"]}>
              <Reports />
            </Guard>
          }
        />
        <Route
          path="/admin"
          element={
            <Guard roles={["admin"]}>
              <Admin />
            </Guard>
          }
        />
      </Route>
    </Routes>
  );
}
