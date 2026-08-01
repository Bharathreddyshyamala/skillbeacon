import { NavLink, Outlet, useNavigate } from "react-router";
import { useAuth } from "./AuthContext";

export default function Layout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function handleLogout() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <div className="app-shell">
      <nav className="navbar navbar-expand-lg navbar-dark app-navbar sticky-top">
        <div className="container">
          <NavLink className="navbar-brand brand" to="/app/dashboard">SkillBeacon</NavLink>
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navMenu">
            <span className="navbar-toggler-icon" />
          </button>
          <div className="collapse navbar-collapse" id="navMenu">
            <div className="navbar-nav me-auto">
              <NavLink className="nav-link" to="/app/dashboard">Dashboard</NavLink>
              <NavLink className="nav-link" to="/app/profile">Profile</NavLink>
            </div>
            <div className="d-flex align-items-center gap-3">
              <span className="small text-secondary d-none d-md-inline">
                {user?.email} · <span className="text-info text-capitalize">{user?.role}</span>
              </span>
              <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>Log out</button>
            </div>
          </div>
        </div>
      </nav>
      <main className="container py-5"><Outlet /></main>
    </div>
  );
}
