import {
    useEffect,
    useState,
  } from "react";

  import {
    useParams,
  } from "react-router";

  import {
    apiRequest,
    jsonBody,
  } from "../api";


  const NEXT_STATUSES = {
    submitted: [
      "under_review",
    ],

    under_review: [
      "accepted",
      "rejected",
    ],

    accepted: [],

    rejected: [],
  };


  export default function EmployerChallengeSubmissions() {

    const {
      challengeId,
    } = useParams();


    const [items, setItems] =
      useState([]);

    const [scores, setScores] =
      useState({});

    const [feedback, setFeedback] =
      useState({});

    const [statusFilter, setStatusFilter] =
      useState("");

    const [error, setError] =
      useState("");

    const [message, setMessage] =
      useState("");


    async function loadData() {

      setError("");


      try {

        const params =
          new URLSearchParams();


        params.set(
          "limit",
          "100"
        );


        if (statusFilter) {

          params.set(
            "status",
            statusFilter
          );

        }


        const response =
          await apiRequest(
            `/challenges/${challengeId}/submissions?${params.toString()}`
          );


        const loaded =
          Array.isArray(
            response?.items
          )
            ? response.items
            : [];


        setItems(
          loaded
        );


        const scoreValues = {};
        const feedbackValues = {};


        loaded.forEach(
          (item) => {

            scoreValues[
              item.id
            ] =
              item.score ?? "";

            feedbackValues[
              item.id
            ] =
              item.employer_feedback
              || "";

          }
        );


        setScores(
          scoreValues
        );

        setFeedback(
          feedbackValues
        );


      } catch (requestError) {

        setError(
          requestError.message ||
          "Unable to load submissions."
        );

      }
    }


    useEffect(() => {

      loadData();

    }, [
      statusFilter,
    ]);


    async function review(
      submissionId,
      newStatus,
    ) {

      setError("");
      setMessage("");


      try {

        await apiRequest(
          `/challenge-submissions/${submissionId}/review`,
          {
            method: "PATCH",

            body: jsonBody({
              status:
                newStatus,

              score:
                scores[submissionId]
                === ""
                  ? null
                  : Number(
                      scores[
                        submissionId
                      ]
                    ),

              employer_feedback:
                feedback[
                  submissionId
                ]?.trim()
                || null,
            }),
          }
        );


        setMessage(
          "Submission updated."
        );


        await loadData();


      } catch (requestError) {

        setError(
          requestError.message ||
          "Unable to review submission."
        );

      }
    }


    return (
      <>

        <div className="mb-4">

          <p className="text-info fw-semibold text-uppercase">
            Employer
          </p>

          <h1 className="display-6 fw-bold">
            Challenge Submissions
          </h1>

        </div>


        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}


        {message && (
          <div className="alert alert-success">
            {message}
          </div>
        )}


        <div className="glass-card mb-4">

          <label className="form-label">
            Filter Status
          </label>

          <select
            className="form-select"
            style={{
              maxWidth: "300px",
            }}
            value={statusFilter}
            onChange={(event) =>
              setStatusFilter(
                event.target.value
              )
            }
          >

            <option value="">
              All
            </option>

            <option value="submitted">
              Submitted
            </option>

            <option value="under_review">
              Under Review
            </option>

            <option value="accepted">
              Accepted
            </option>

            <option value="rejected">
              Rejected
            </option>

          </select>

        </div>


        {items.length === 0 && (

          <div className="glass-card">
            No submissions found.
          </div>

        )}


        {items.map(
          (item) => {

            const nextStatuses =
              NEXT_STATUSES[
                item.status
              ] || [];


            return (

              <div
                key={item.id}
                className="glass-card mb-4"
              >

                <div className="d-flex justify-content-between">

                  <div>

                    <h2 className="h5">
                      {item.student_name}
                    </h2>

                    <p className="text-secondary">
                      {item.student_email}
                    </p>

                  </div>


                  <span className="badge text-bg-info text-capitalize">
                    {
                      item.status.replaceAll(
                        "_",
                        " "
                      )
                    }
                  </span>

                </div>


                {item.submission_text && (

                  <div className="mb-3">

                    <h3 className="h6">
                      Solution
                    </h3>

                    <p>
                      {item.submission_text}
                    </p>

                  </div>

                )}


                {item.repository_url && (

                  <p>

                    <a
                      href={item.repository_url}
                      target="_blank"
                      rel="noreferrer"
                    >
                      Open Repository
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
                      Open Demo
                    </a>

                  </p>

                )}


                <h3 className="h6">
                  Candidate Skills
                </h3>


                <div className="d-flex flex-wrap gap-2 mb-4">

                  {(item.profile_snapshot
                      ?.skills || []
                  ).map(
                    (skill) => (

                      <span
                        key={
                          `${skill.name}-${skill.level}`
                        }
                        className="badge text-bg-secondary"
                      >
                        {skill.name}

                        {" · "}

                        {skill.level}
                      </span>

                    )
                  )}

                </div>


                <div className="mb-3">

                  <label className="form-label">
                    Score
                  </label>

                  <input
                    type="number"
                    min="0"
                    max="100"
                    className="form-control"
                    style={{
                      maxWidth: "200px",
                    }}
                    value={
                      scores[item.id]
                      ?? ""
                    }
                    onChange={(event) =>
                      setScores({
                        ...scores,

                        [item.id]:
                          event.target.value,
                      })
                    }
                  />

                </div>


                <div className="mb-3">

                  <label className="form-label">
                    Feedback
                  </label>

                  <textarea
                    className="form-control"
                    rows="4"
                    value={
                      feedback[
                        item.id
                      ] || ""
                    }
                    onChange={(event) =>
                      setFeedback({
                        ...feedback,

                        [item.id]:
                          event.target.value,
                      })
                    }
                  />

                </div>


                <div className="d-flex gap-2">

                  {nextStatuses.map(
                    (newStatus) => (

                      <button
                        type="button"
                        key={newStatus}
                        className="btn btn-outline-info"
                        onClick={() =>
                          review(
                            item.id,
                            newStatus
                          )
                        }
                      >
                        {
                          newStatus.replaceAll(
                            "_",
                            " "
                          )
                        }
                      </button>

                    )
                  )}

                </div>

              </div>

            );

          }
        )}

      </>
    );
  }