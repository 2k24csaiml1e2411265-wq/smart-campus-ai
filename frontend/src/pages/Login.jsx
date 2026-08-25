import { useLocation, useNavigate } from "react-router-dom";
import { useState } from "react";
import { useAuth } from "../hooks/useAuth.jsx";
import { Leaf } from "lucide-react";

const ACCOUNTS = [
  ["admin@psit.ac.in", "admin123", "Admin"],
  ["facility@psit.ac.in", "facility123", "Facility manager"],
  ["cse.manager@psit.ac.in", "manager123", "CSE department manager"],
  ["viewer@psit.ac.in", "viewer123", "Viewer"],
];

export default function Login() {
  const { login } = useAuth();
  const nav = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState("admin@psit.ac.in");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const onSubmit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      await login(email, password);
      nav(location.state?.from || "/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Sign-in failed. Check credentials or backend availability.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="grid min-h-screen place-items-center bg-[#f4f1ea] px-4 dark:bg-canopy-950">
      <form onSubmit={onSubmit} className="card w-full max-w-md p-8">
        <div className="mb-6 flex items-center gap-3">
          <span className="grid h-10 w-10 place-items-center rounded-xl bg-emerald-800 text-white">
            <Leaf size={18} />
          </span>
          <div>
            <h1 className="font-display text-2xl">Smart Campus AI</h1>
            <p className="text-sm text-stone-500">PSIT Kanpur · demo accounts</p>
          </div>
        </div>
        <label className="text-sm">
          Email
          <input className="mt-1 mb-3 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 dark:border-white/15 dark:bg-canopy-900" value={email} onChange={(e) => setEmail(e.target.value)} />
        </label>
        <label className="text-sm">
          Password
          <input type="password" className="mt-1 mb-4 w-full rounded-lg border border-stone-300 bg-white px-3 py-2 dark:border-white/15 dark:bg-canopy-900" value={password} onChange={(e) => setPassword(e.target.value)} />
        </label>
        {error ? <p className="mb-3 text-sm text-rose-700">{error}</p> : null}
        <button disabled={busy} className="w-full rounded-lg bg-emerald-800 py-2 text-white disabled:opacity-60">
          {busy ? "Signing in…" : "Sign in"}
        </button>
        <ul className="mt-5 space-y-1 text-xs text-stone-500">
          {ACCOUNTS.map(([e, p, r]) => (
            <li key={e}>
              <button type="button" className="underline" onClick={() => { setEmail(e); setPassword(p); }}>
                {r}
              </button>
              : {e}
            </li>
          ))}
        </ul>
      </form>
    </div>
  );
}
