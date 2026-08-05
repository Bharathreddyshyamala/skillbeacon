import {
    useEffect,
    useState,
  } from "react";

  import {
    apiRequest,
  } from "../api";


  export default function ChallengeSubmissions() {

    const [items, setItems] =
      useState([]);

    const [loading, setLoading] =
      useState(true);

    const [error, setError] =
      useState("");


    async function loadData() {

      setLoading(true);
      setError("");


      try {

        const response =
          await apiRequest(
            "/challenge-submissions/me?limit=100"
          );


        setItems(
          Array.isArray(
            response?.items
          )
            ? response.items
            : []
        );


      } catch (requestError) {

        setError(
          requestError.message ||
          "Unable to load submissions."
        );

      } finally {

        setLoading(false);

      }
    }


    useEffect(() => {

      loadData();

    }, []);


    return (
      <>

        <div className="mb-4">

          <p className="text-info fw-semibold text-uppercase">
            Challenges
          </p>

          <h1 className="display-6 fw-bold">
            My Challenge Submissions
          </h1>

        </div>


        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}


        {loading && (
          <p className="text-secondary">
            Loading submissions...
          </p>
        )}


        {!loading &&
          items.length === 0 && (

          <div className="glass-card">
            No challenge submissions yet.
          </div>

        )}


        {items.map(
          (item) => (

            <div
              key={item.id}
              className="glass-card mb-4"
            >

              <h2 className="h5">
                {item.challenge_title}
              </h2>


              <p className="text-secondary">
                {item.company_name}
              </p>


              <span className="badge text-bg-info text-capitalize">
                {
                  item.status.replaceAll(
                    "_",
                    " "
                  )
                }
              </span>


              {item.repository_url && (

                <p className="mt-3">

                  <a
                    href={item.repository_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Repository
                  </a>

                </p>

              )}


              {item.demo_url && (

                <p>

                  <a
                    href={item.demo_url}
                    target="_blank"
                    rel="noreferrer"
                  >
                    Demo
                  </a>

                </p>

              )}


              {item.score !== null &&
                item.score !== undefined && (

                <p>
                  <strong>
                    Score:
                  </strong>

                  {" "}

                  {item.score}/100
                </p>

              )}


              {item.employer_feedback && (

                <div className="alert alert-secondary">

                  <strong>
                    Employer Feedback
                  </strong>

                  <p className="mb-0 mt-2">
                    {item.employer_feedback}
                  </p>

                </div>

              )}

            </div>

          )
        )}

      </>
    );
  }