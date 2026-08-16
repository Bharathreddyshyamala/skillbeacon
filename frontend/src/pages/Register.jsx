import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router";
import { ApiError } from "../api";
import { useAuth } from "../useAuth";

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({
    email: "",
    password: "",
    confirm: "",
    role: "student",
  });
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  if (user) return <Navigate to="/app/dashboard" replace />;

  async function submit(event) {
    event.preventDefault();
    setError("");
    if (form.password !== form.confirm) {
      setError("Passwords do not match.");
      return;
    }
    setSaving(true);
    try {
      await register(form.email, form.password, form.role);
      navigate("/app/profile", { replace: true });
    } catch (err) {
      setError(
        err instanceof ApiError || err instanceof Error
          ? err.message
          : "Unable to register.",
      );
    } finally {
      setSaving(false);
    }
  }

  return (
    <main className="auth-page">
      <form className="glass-card auth-card auth-wide" onSubmit={submit}>
        <Link className="brand text-decoration-none" to="/">
          SkillBeacon
        </Link>
        <h1 className="h2 mt-4">Create an account</h1>
        <p className="text-secondary">
          Choose the role that matches how you will use SkillBeacon.
        </p>
        {error && <div className="alert alert-danger">{error}</div>}


        <label className="form-label">Role</label>
        <select
          className="form-select form-select-lg"
          value={form.role}
          onChange={(e) => setForm({ ...form, role: e.target.value })}
        >
          <option value="student">Student or graduate</option>
          <option value="employer">Employer</option>
          <option value="mentor">Mentor</option>
        </select>

        <label className="form-label mt-3">Email</label>
        <input
          className="form-control form-control-lg"
          type="email"
          required
          value={form.email}
          onChange={(e) => setForm({ ...form, email: e.target.value })}
        />

        <div className="row g-3 mt-1">
          <div className="col-md-6">
            <label className="form-label">Password</label>
            <input
              className="form-control"
              type="password"
              minLength="8"
              required
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
            />
          </div>
          <div className="col-md-6">
            <label className="form-label">Confirm password</label>
            <input
              className="form-control"
              type="password"
              minLength="8"
              required
              value={form.confirm}
              onChange={(e) => setForm({ ...form, confirm: e.target.value })}
            />
          </div>
        </div>
        <button
          className="btn btn-info btn-lg w-100 mt-4"
          disabled={saving}
        >
          {saving ? "Creating account..." : "Create account"}
        </button>
        <p className="text-center text-secondary mt-4 mb-0">
          Already registered? <Link to="/login">Log in</Link>
        </p>
      </form>
    </main>
  );
}
