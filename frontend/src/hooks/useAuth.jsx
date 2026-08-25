import { createContext, useContext, useMemo, useState } from "react";
import { CampusAPI } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(() => {
    const raw = localStorage.getItem("sca_session");
    return raw ? JSON.parse(raw) : null;
  });

  const value = useMemo(
    () => ({
      session,
      role: session?.role,
      login: async (email, password) => {
        const { data } = await CampusAPI.login(email, password);
        const next = { ...data };
        localStorage.setItem("sca_token", data.access_token);
        localStorage.setItem("sca_session", JSON.stringify(next));
        setSession(next);
        return next;
      },
      logout: () => {
        localStorage.removeItem("sca_token");
        localStorage.removeItem("sca_session");
        setSession(null);
      },
    }),
    [session]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  return useContext(AuthContext);
}

export function canAccess(role, path) {
  if (path === "/login") return true;
  if (!role) return path === "/dashboard" || path === "/";
  if (role === "admin") return true;
  if (role === "facility_manager") return path !== "/admin" || true;
  if (role === "department_manager") return !path.startsWith("/admin");
  if (role === "viewer") return ["/dashboard", "/", "/analytics"].includes(path) || path === "/departments";
  return true;
}
