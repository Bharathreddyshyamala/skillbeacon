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

import { useAuth } from "./useAuth";

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


  async function handleLogout() {
    await logout();

    navigate(
      "/login",
      {
        replace: true,
      }
    );
  }


  /*
   * Role-based navigation permissions
   */

  const canManageSkills =
    user?.role === "student" ||
    user?.role === "mentor";

  const canVerifyEvidence =
    user?.role === "mentor";

  const canBrowseOpportunities =
    user?.role === "student";

  const canViewApplications =
    user?.role === "student";

  const canManageOpportunities =
    user?.role === "employer";

  const canUseMentorships =
    user?.role === "student" ||
    user?.role === "mentor";

  const canBrowseChallenges =
    user?.role === "student";

  const canManageChallenges =
    user?.role === "employer";

  const canUseAdmin =
    user?.role === "admin";

  const canViewProfile =
    user?.role === "student" ||
    user?.role === "mentor" ||
    user?.role === "employer";

  const canViewNotifications =
    Boolean(user);


  /*
   * Notifications
   */

  async function loadUnreadNotifications() {
    if (!user) {
      setUnreadNotifications(0);
      return;
    }

    try {
      const result =
        await apiRequest(
          "/notifications/unread-count"
        );

      setUnreadNotifications(
        result?.unread_count || 0
      );
    } catch (error) {
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

      const intervalId =
        window.setInterval(
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

      <nav
        className="
          navbar
          navbar-expand-lg
          navbar-dark
          app-navbar
          sticky-top
        "
      >

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
            className="
              collapse
              navbar-collapse
            "
            id="navMenu"
          >

            <div className="navbar-nav me-auto">

              {/* Common Dashboard */}

              <NavLink
                className="nav-link"
                to="/app/dashboard"
              >
                Dashboard
              </NavLink>


              {/* Profile */}

              {canViewProfile && (
                <NavLink
                  className="nav-link"
                  to="/app/profile"
                >
                  Profile
                </NavLink>
              )}


              {/* Skills */}

              {canManageSkills && (
                <NavLink
                  className="nav-link"
                  to="/app/skills"
                >
                  Skills
                </NavLink>
              )}


              {/* Student Opportunities */}

              {canBrowseOpportunities && (
                <NavLink
                  className="nav-link"
                  to="/app/opportunities"
                >
                  Opportunities
                </NavLink>
              )}


              {/* Student Applications */}

              {canViewApplications && (
                <NavLink
                  className="nav-link"
                  to="/app/applications"
                >
                  Applications
                </NavLink>
              )}


              {/* Mentorship */}

              {canUseMentorships && (
                <NavLink
                  className="nav-link"
                  to="/app/mentorships"
                >
                  Mentorship
                </NavLink>
              )}


              {/* Student Challenges */}

              {canBrowseChallenges && (
                <NavLink
                  className="nav-link"
                  to="/app/challenges"
                >
                  Challenges
                </NavLink>
              )}


              {/* Employer Opportunities */}

              {canManageOpportunities && (
                <NavLink
                  className="nav-link"
                  to="/app/opportunities/manage"
                >
                  Manage Opportunities
                </NavLink>
              )}


              {/* Employer Challenges */}

              {canManageChallenges && (
                <NavLink
                  className="nav-link"
                  to="/app/challenges/manage"
                >
                  Manage Challenges
                </NavLink>
              )}


              {/* Mentor Evidence Verification */}

              {canVerifyEvidence && (
                <NavLink
                  className="nav-link"
                  to="/app/verifications"
                >
                  Verifications
                </NavLink>
              )}


              {/* ====================== */}
              {/* ADMIN NAVIGATION */}
              {/* ====================== */}

              {canUseAdmin && (
                <NavLink
                  className="nav-link"
                  to="/app/admin"
                >
                  Admin
                </NavLink>
              )}


              {canUseAdmin && (
                <NavLink
                  className="nav-link"
                  to="/app/admin/users"
                >
                  Users
                </NavLink>
              )}


              {canUseAdmin && (
                <NavLink
                  className="nav-link"
                  to="/app/admin/content"
                >
                  Moderation
                </NavLink>
              )}


              {canUseAdmin && (
                <NavLink
                  className="nav-link"
                  to="/app/admin/audit-logs"
                >
                  Audit Logs
                </NavLink>
              )}


              {canUseAdmin && (
                <NavLink
                  className="nav-link"
                  to="/app/admin/sample-data"
                >
                  Sample Data
                </NavLink>
              )}


              {/* NEW: External Job Ingestion */}

              {canUseAdmin && (
                <NavLink
                  className="nav-link"
                  to="/app/admin/job-ingestion"
                >
                  Job Ingestion
                </NavLink>
              )}


              {/* Notifications */}

              {canViewNotifications && (
                <NavLink
                  className="
                    nav-link
                    d-flex
                    align-items-center
                  "
                  to="/app/notifications"
                >

                  <span>
                    Notifications
                  </span>

                  {unreadNotifications > 0 && (
                    <span
                      className="
                        badge
                        rounded-pill
                        bg-danger
                        ms-2
                      "
                      title={
                        `${unreadNotifications} unread notification${
                          unreadNotifications !== 1
                            ? "s"
                            : ""
                        }`
                      }
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


            {/* Logged-in user */}

            <div
              className="
                d-flex
                align-items-center
                gap-3
              "
            >

              <span
                className="
                  small
                  text-secondary
                  d-none
                  d-md-inline
                "
              >

                {user?.email}

                {" · "}

                <span
                  className="
                    text-info
                    text-capitalize
                  "
                >
                  {user?.role}
                </span>

              </span>


              <button
                className="
                  btn
                  btn-outline-light
                  btn-sm
                "
                type="button"
                onClick={
                  handleLogout
                }
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