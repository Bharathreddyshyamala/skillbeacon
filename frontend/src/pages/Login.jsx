import { useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router";
import { ApiError } from "../api";
import { useAuth } from "../useAuth";

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  if (user) return <Navigate to="/app/dashboard" replace />;

  async function submit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    try {
      await login(form.email, form.password);
      navigate(location.state?.from || "/app/dashboard", { replace: true });
    } catch (err) {
      setError(
        err instanceof ApiError || err instanceof Error
          ? err.message
          : "Unable to log in.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="glass-card auth-card" onSubmit={submit}>
        <Link className="brand text-decoration-none" to="/">
          SkillBeacon
        </Link>
        <h1 className="h2 mt-4">Welcome back</h1>
        <p className="text-secondary">Log in to continue to your dashboard.</p>
        {error && <div className="alert alert-danger">{error}</div>}


        <label className="form-label">Email</label>
        <input
          className="form-control form-control-lg"
          type="email"
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />
        <label className="form-label mt-3">Password</label>
        <input
          className="form-control form-control-lg"
          type="password"
          required
          value={form.password}
          onChange={(e) => setForm({ ...form, password: e.target.value })}
        />
        <button
          className="btn btn-info btn-lg w-100 mt-4"
          disabled={saving}
        >
          {saving ? "Logging in..." : "Log in"}
        </button>
        <p className="text-center text-secondary mt-4 mb-0">
          No account? <Link to="/register">Register</Link>
        </p>
      </form>
    </main>
  );
}
