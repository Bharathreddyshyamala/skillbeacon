import {
  NavLink,
  Outlet,
  useNavigate,
} from "react-router";

import { useAuth } from "./AuthContext";


export default function Layout() {
  const { user, logout } = useAuth();

  const navigate = useNavigate();


  async function handleLogout() {
    await logout();

    navigate(
      "/login",
      {
        replace: true,
      }
    );
  }




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