import {
  useEffect,
  useState,
} from "react";

import {
  NavLink,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router";

import { useAuth } from "./AuthContext";

import {
  apiRequest,
} from "./api";


export default function Layout() {
  const { user, logout } = useAuth();

  const navigate = useNavigate();

  const location = useLocation();

  const [
    unreadNotifications,
    setUnreadNotifications,
  ] = useState(0);


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


  // Mentor can verify skill evidence.
  const canVerifyEvidence =
    user?.role === "mentor";


  // Only students browse published opportunities.
  const canBrowseOpportunities =
    user?.role === "student";


  // Only students can view and manage
  // their own applications.
  const canViewApplications =
    user?.role === "student";


  // Employers create and manage opportunities.
  const canManageOpportunities =
    user?.role === "employer";


  // Students and mentors use mentorship features.
  const canUseMentorships =
    user?.role === "student" ||
    user?.role === "mentor";


  // Students browse and submit employer challenges.
  const canBrowseChallenges =
    user?.role === "student";


  // Employers create and manage challenges.
  const canManageChallenges =
    user?.role === "employer";


  // Notifications are available to every
  // authenticated user, regardless of role.
  const canViewNotifications =
    Boolean(user);


  // =========================================================
  // Notifications
  // =========================================================

  async function loadUnreadNotifications() {
    if (!user) {
      setUnreadNotifications(0);
      return;
    }

    try {
      const result = await apiRequest(
        "/notifications/unread-count"
      );

      setUnreadNotifications(
        result?.unread_count || 0
      );

    } catch (error) {
      // Do not break the main layout if the
      // notification endpoint is temporarily unavailable.
      console.error(
        "Failed to load unread notifications:",
        error
      );

      setUnreadNotifications(0);
    }
  }


  useEffect(
    () => {
      if (!user) {
        setUnreadNotifications(0);
        return;
      }

      loadUnreadNotifications();

      // Refresh periodically so notifications created
      // while the user remains on the same page can appear.
      const intervalId = window.setInterval(
        () => {
          loadUnreadNotifications();
        },
        30000
      );

      return () => {
        window.clearInterval(
          intervalId
        );
      };
    },
    [
      user,
      location.pathname,
    ]
  );


  return (
    <div className="app-shell">


      <nav className="navbar navbar-expand-lg navbar-dark app-navbar sticky-top">

        <div className="container">


          <NavLink
            className="navbar-brand brand"
            to="/app/dashboard"
          >
            SkillBeacon
          </NavLink>


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


          <div
            className="collapse navbar-collapse"
            id="navMenu"
          >

            <div className="navbar-nav me-auto">


              <NavLink
                className="nav-link"
                to="/app/dashboard"
              >
                Dashboard
              </NavLink>


              <NavLink
                className="nav-link"
                to="/app/profile"
              >
                Profile
              </NavLink>


              {canManageSkills && (
                <NavLink
                  className="nav-link"
                  to="/app/skills"
                >
                  Skills
                </NavLink>
              )}


              {canBrowseOpportunities && (
                <NavLink
                  className="nav-link"
                  to="/app/opportunities"
                >
                  Opportunities
                </NavLink>
              )}


              {canViewApplications && (
                <NavLink
                  className="nav-link"
                  to="/app/applications"
                >
                  Applications
                </NavLink>
              )}


              {canUseMentorships && (
                <NavLink
                  className="nav-link"
                  to="/app/mentorships"
                >
                  Mentorship
                </NavLink>
              )}


              {canBrowseChallenges && (
                <NavLink
                  className="nav-link"
                  to="/app/challenges"
                >
                  Challenges
                </NavLink>
              )}


              {canManageOpportunities && (
                <NavLink
                  className="nav-link"
                  to="/app/opportunities/manage"
                >
                  Manage Opportunities
                </NavLink>
              )}


              {canManageChallenges && (
                <NavLink
                  className="nav-link"
                  to="/app/challenges/manage"
                >
                  Manage Challenges
                </NavLink>
              )}


              {canVerifyEvidence && (
                <NavLink
                  className="nav-link"
                  to="/app/verifications"
                >
                  Verifications
                </NavLink>
              )}


              {canViewNotifications && (
                <NavLink
                  className="nav-link d-flex align-items-center"
                  to="/app/notifications"
                >
                  <span>
                    Notifications
                  </span>

                  {unreadNotifications > 0 && (
                    <span
                      className="badge rounded-pill bg-danger ms-2"
                      title={`${unreadNotifications} unread notification${
                        unreadNotifications !== 1
                          ? "s"
                          : ""
                      }`}
                    >
                      {
                        unreadNotifications > 99
                          ? "99+"
                          : unreadNotifications
                      }
                    </span>
                  )}
                </NavLink>
              )}


            </div>


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


      <main className="container py-5">
        <Outlet />
      </main>

    </div>
  );
}