import {
  useEffect,
  useState,
} from "react";

import {
  apiRequest,
} from "../../api";


export default function AdminDashboard() {

  const [
    dashboard,
    setDashboard,
  ] = useState(null);


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState("");


  async function loadDashboard() {

    setLoading(true);

    setError("");


    try {

      const response =
        await apiRequest(
          "/admin/dashboard"
        );


      setDashboard(
        response
      );

    } catch (
      requestError
    ) {

      setError(
        requestError.message
        || "Unable to load admin dashboard."
      );

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    loadDashboard();

  }, []);


  const cards = dashboard
    ? [
        {
          label: "Total Users",
          value:
            dashboard.total_users,
        },

        {
          label: "Students",
          value:
            dashboard.students,
        },

        {
          label: "Mentors",
          value:
            dashboard.mentors,
        },

        {
          label: "Employers",
          value:
            dashboard.employers,
        },

        {
          label: "Active Users",
          value:
            dashboard.active_users,
        },

        {
          label: "Inactive Users",
          value:
            dashboard.inactive_users,
        },

        {
          label: "Skills",
          value:
            dashboard.total_skills,
        },

        {
          label: "Opportunities",
          value:
            dashboard.total_opportunities,
        },

        {
          label: "Open Opportunities",
          value:
            dashboard.open_opportunities,
        },

        {
          label: "Applications",
          value:
            dashboard.total_applications,
        },

        {
          label: "Mentorships",
          value:
            dashboard.total_mentorships,
        },

        {
          label: "Active Mentorships",
          value:
            dashboard.active_mentorships,
        },

        {
          label: "Challenges",
          value:
            dashboard.total_challenges,
        },

        {
          label: "Open Challenges",
          value:
            dashboard.open_challenges,
        },

        {
          label: "Challenge Submissions",
          value:
            dashboard.challenge_submissions,
        },
      ]
    : [];


  return (
    <>

      <div className="mb-4">

        <p className="text-info fw-semibold text-uppercase">
          Administration
        </p>


        <h1 className="display-6 fw-bold">
          Admin Dashboard
        </h1>


        <p className="text-secondary">
          Monitor users, opportunities,
          applications, mentorships,
          and challenges across SkillBeacon.
        </p>

      </div>


      {error && (

        <div className="alert alert-danger">
          {error}
        </div>

      )}


      {loading && (

        <p className="text-secondary">
          Loading platform statistics...
        </p>

      )}


      {
        !loading &&
        dashboard && (

          <div className="row g-4">

            {cards.map(
              (card) => (

                <div
                  key={
                    card.label
                  }
                  className="col-sm-6 col-lg-4 col-xl-3"
                >

                  <div className="glass-card h-100">

                    <p className="text-secondary small mb-2">
                      {card.label}
                    </p>


                    <p className="display-6 fw-bold mb-0">
                      {card.value}
                    </p>

                  </div>

                </div>

              )
            )}

          </div>

        )
      }

    </>
  );
}