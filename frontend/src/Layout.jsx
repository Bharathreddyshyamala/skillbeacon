import {
    NavLink,
    Outlet,
    useNavigate,
  } from "react-router";
  
  import { useAuth } from "./AuthContext";
  
  
  export default function Layout() {
    const { user, logout } = useAuth();
  
    const navigate = useNavigate();
  
  
    // =========================================================
    // Logout
    // =========================================================
  
    async function handleLogout() {
      await logout();
  
      navigate(
        "/login",
        {
          replace: true,
        }
      );
    }
  
  
    // =========================================================
    // Role Permissions
    // =========================================================
  
    // Student + Mentor can maintain
    // their personal Skill Passport.
    const canManageSkills =
      user?.role === "student" ||
      user?.role === "mentor";
  
  
    // Mentor + Admin can review
    // skill evidence.
    const canVerifyEvidence =
      user?.role === "mentor" ||
      user?.role === "admin";
  
  
    // Only students browse
    // published opportunities.
    const canBrowseOpportunities =
      user?.role === "student";
  
  
    // Step 17:
    // Only students can view and manage
    // their own applications.
    const canViewApplications =
      user?.role === "student";
  
  
    // Employers create/manage opportunities.
    // Admin also has access for moderation.
    const canManageOpportunities =
      user?.role === "employer" ||
      user?.role === "admin";
  
  
    return (
      <div className="app-shell">
  
        {/* =====================================================
            NAVBAR
        ====================================================== */}
  
        <nav className="navbar navbar-expand-lg navbar-dark app-navbar sticky-top">
  
          <div className="container">
  
  
            {/* =================================================
                BRAND
            ================================================== */}
  
            <NavLink
              className="navbar-brand brand"
              to="/app/dashboard"
            >
              SkillBeacon
            </NavLink>
  
  
            {/* =================================================
                MOBILE MENU BUTTON
            ================================================== */}
  
            <button
              className="navbar-toggler"
              type="button"
              data-bs-toggle="collapse"
              data-bs-target="#navMenu"
              aria-controls="navMenu"
              aria-expanded="false"
              aria-label="Toggle navigation"
            >
              <span className="navbar-toggler-icon" />
            </button>
  
  
            {/* =================================================
                NAVIGATION MENU
            ================================================== */}
  
            <div
              className="collapse navbar-collapse"
              id="navMenu"
            >
  
              <div className="navbar-nav me-auto">
  
  
                {/* =============================================
                    DASHBOARD
                    Available to every logged-in user
                ============================================== */}
  
                <NavLink
                  className="nav-link"
                  to="/app/dashboard"
                >
                  Dashboard
                </NavLink>
  
  
                {/* =============================================
                    PROFILE
                    Available to every logged-in user
                ============================================== */}
  
                <NavLink
                  className="nav-link"
                  to="/app/profile"
                >
                  Profile
                </NavLink>
  
  
                {/* =============================================
                    SKILLS
                    Student + Mentor only
                ============================================== */}
  
                {canManageSkills && (
                  <NavLink
                    className="nav-link"
                    to="/app/skills"
                  >
                    Skills
                  </NavLink>
                )}
  
  
                {/* =============================================
                    OPPORTUNITIES
                    Student only
                ============================================== */}
  
                {canBrowseOpportunities && (
                  <NavLink
                    className="nav-link"
                    to="/app/opportunities"
                  >
                    Opportunities
                  </NavLink>
                )}
  
  
                {/* =============================================
                    APPLICATIONS
                    Step 17
                    Student only
                ============================================== */}
  
                {canViewApplications && (
                  <NavLink
                    className="nav-link"
                    to="/app/applications"
                  >
                    Applications
                  </NavLink>
                )}
  
  
                {/* =============================================
                    MANAGE OPPORTUNITIES
                    Employer + Admin only
                ============================================== */}
  
                {canManageOpportunities && (
                  <NavLink
                    className="nav-link"
                    to="/app/opportunities/manage"
                  >
                    Manage Opportunities
                  </NavLink>
                )}
  
  
                {/* =============================================
                    VERIFICATIONS
                    Mentor + Admin only
                ============================================== */}
  
                {canVerifyEvidence && (
                  <NavLink
                    className="nav-link"
                    to="/app/verifications"
                  >
                    Verifications
                  </NavLink>
                )}
  
  
              </div>
  
  
              {/* =================================================
                  USER INFORMATION + LOGOUT
              ================================================== */}
  
              <div className="d-flex align-items-center gap-3">
  
                <span className="small text-secondary d-none d-md-inline">
  
                  {user?.email}
  
                  {" · "}
  
                  <span className="text-info text-capitalize">
                    {user?.role}
                  </span>
  
                </span>
  
  
                <button
                  className="btn btn-outline-light btn-sm"
                  type="button"
                  onClick={handleLogout}
                >
                  Log out
                </button>
  
              </div>
  
  
            </div>
  
          </div>
  
        </nav>
  
  
        {/* =====================================================
            PAGE CONTENT
        ====================================================== */}
  
        <main className="container py-5">
          <Outlet />
        </main>
  
      </div>
    );
  }