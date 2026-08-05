import {
    useEffect,
    useState,
  } from "react";

  import {
    apiRequest,
    jsonBody,
  } from "../api";

  import {
    useNavigate,
  } from "react-router";


  const EMPTY_SUBMISSION = {
    submission_text: "",
    repository_url: "",
    demo_url: "",
  };


  export default function Challenges() {

    const navigate =
      useNavigate();


    const [items, setItems] =
      useState([]);

    const [submissions, setSubmissions] =
      useState([]);

    const [search, setSearch] =
      useState("");

    const [difficulty, setDifficulty] =
      useState("");

    const [challengeType, setChallengeType] =
      useState("");

    const [selectedId, setSelectedId] =
      useState("");

    const [form, setForm] =
      useState(
        EMPTY_SUBMISSION
      );

    const [loading, setLoading] =
      useState(true);

    const [submitting, setSubmitting] =
      useState(false);

    const [error, setError] =
      useState("");

    const [message, setMessage] =
      useState("");


    async function loadData() {

      setLoading(true);
      setError("");


      try {

        const params =
          new URLSearchParams();


        if (search.trim()) {
          params.set(
            "search",
            search.trim()
          );
        }


        if (difficulty) {
          params.set(
            "difficulty",
            difficulty
          );
        }


        if (challengeType) {
          params.set(
            "challenge_type",
            challengeType
          );
        }


        params.set(
          "limit",
          "100"
        );


        const [
          challengeResponse,
          submissionResponse,
        ] = await Promise.all([

          apiRequest(
            `/challenges?${params.toString()}`
          ),

          apiRequest(
            "/challenge-submissions/me?limit=100"
          ),

        ]);


        setItems(
          Array.isArray(
            challengeResponse?.items
          )
            ? challengeResponse.items
            : []
        );


        setSubmissions(
          Array.isArray(
            submissionResponse?.items
          )
            ? submissionResponse.items
            : []
        );


      } catch (requestError) {

        setError(
          requestError.message ||
          "Unable to load challenges."
        );

      } finally {

        setLoading(false);

      }
    }


    useEffect(() => {

      loadData();

    }, []);


    function existingSubmission(
      challengeId,
    ) {

      return submissions.find(
        (submission) =>
          submission.challenge_id
          === challengeId
      );
    }


    function updateField(
      field,
      value,
    ) {

      setForm({
        ...form,

        [field]:
          value,
      });
    }


    function openSubmission(
      challengeId,
    ) {

      setSelectedId(
        selectedId === challengeId
          ? ""
          : challengeId
      );

      setForm({
        ...EMPTY_SUBMISSION
      });
    }


    async function submitSolution(
      challengeId,
    ) {

      setError("");
      setMessage("");


      const hasContent =
        form.submission_text.trim()
        || form.repository_url.trim()
        || form.demo_url.trim();


      if (!hasContent) {

        setError(
          "Provide solution text, repository URL, or demo URL."
        );

        return;
      }


      const confirmed =
        window.confirm(
          "Submit this challenge solution? You cannot submit the same challenge twice."
        );


      if (!confirmed) {
        return;
      }


      setSubmitting(true);


      try {

        await apiRequest(
          `/challenges/${challengeId}/submissions`,
          {
            method: "POST",

            body: jsonBody({
              submission_text:
                form.submission_text.trim()
                || null,

              repository_url:
                form.repository_url.trim()
                || null,

              demo_url:
                form.demo_url.trim()
                || null,
            }),
          }
        );


        setMessage(
          "Challenge submitted successfully."
        );


        setSelectedId("");

        setForm({
          ...EMPTY_SUBMISSION
        });


        await loadData();


      } catch (requestError) {

        setError(
          requestError.message ||
          "Unable to submit challenge."
        );

      } finally {

        setSubmitting(false);

      }
    }


    return (
      <>

        <div className="mb-4">

          <p className="text-info fw-semibold text-uppercase">
            Challenges
          </p>

          <h1 className="display-6 fw-bold">
            Employer Challenges
          </h1>

          <p className="text-secondary">
            Solve practical challenges and
            demonstrate your skills.
          </p>

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

          <form
            className="row g-3"
            onSubmit={(event) => {
              event.preventDefault();

              loadData();
            }}
          >

            <div className="col-md-5">

              <label className="form-label">
                Search
              </label>

              <input
                className="form-control"
                value={search}
                onChange={(event) =>
                  setSearch(
                    event.target.value
                  )
                }
                placeholder="API, Python, data..."
              />

            </div>


            <div className="col-md-3">

              <label className="form-label">
                Type
              </label>

              <select
                className="form-select"
                value={challengeType}
                onChange={(event) =>
                  setChallengeType(
                    event.target.value
                  )
                }
              >

                <option value="">
                  All
                </option>

                <option value="coding">
                  Coding
                </option>

                <option value="data">
                  Data
                </option>

                <option value="case_study">
                  Case Study
                </option>

                <option value="design">
                  Design
                </option>

                <option value="general">
                  General
                </option>

              </select>

            </div>


            <div className="col-md-3">

              <label className="form-label">
                Difficulty
              </label>

              <select
                className="form-select"
                value={difficulty}
                onChange={(event) =>
                  setDifficulty(
                    event.target.value
                  )
                }
              >

                <option value="">
                  All
                </option>

                <option value="beginner">
                  Beginner
                </option>

                <option value="intermediate">
                  Intermediate
                </option>

                <option value="advanced">
                  Advanced
                </option>

              </select>

            </div>


            <div className="col-md-1 d-flex align-items-end">

              <button
                className="btn btn-info w-100"
                type="submit"
              >
                Go
              </button>

            </div>

          </form>

        </div>


        <div className="mb-4">

          <button
            className="btn btn-outline-info"
            type="button"
            onClick={() =>
              navigate(
                "/app/challenge-submissions"
              )
            }
          >
            My Challenge Submissions
          </button>

        </div>


        {loading && (
          <p className="text-secondary">
            Loading challenges...
          </p>
        )}


        {!loading &&
          items.length === 0 && (

          <div className="glass-card">

            <p className="text-secondary mb-0">
              No open challenges found.
            </p>

          </div>

        )}


        {items.map(
          (challenge) => {

            const submission =
              existingSubmission(
                challenge.id
              );


            return (

              <div
                key={challenge.id}
                className="glass-card mb-4"
              >

                <div className="d-flex justify-content-between gap-3 flex-wrap">

                  <div>

                    <p className="text-info text-uppercase small mb-1">
                      {
                        challenge.challenge_type
                          .replaceAll(
                            "_",
                            " "
                          )
                      }
                    </p>

                    <h2 className="h4">
                      {challenge.title}
                    </h2>

                    <p className="text-secondary">
                      {challenge.company_name}
                    </p>

                  </div>


                  <span className="badge text-bg-info text-capitalize">
                    {challenge.difficulty}
                  </span>

                </div>


                <p>
                  {challenge.description}
                </p>


                <h3 className="h6">
                  Instructions
                </h3>

                <p className="text-secondary">
                  {challenge.instructions}
                </p>


                {challenge.deliverables && (
                  <>
                    <h3 className="h6">
                      Deliverables
                    </h3>

                    <p className="text-secondary">
                      {challenge.deliverables}
                    </p>
                  </>
                )}


                <p>
                  <strong>
                    Deadline:
                  </strong>

                  {" "}

                  {challenge.deadline ||
                    "No deadline"}
                </p>


                {(challenge.skills || []).length > 0 && (

                  <div className="mb-3">

                    <h3 className="h6">
                      Required Skills
                    </h3>

                    <div className="d-flex flex-wrap gap-2">

                      {challenge.skills.map(
                        (skill) => (

                          <span
                            key={skill.id}
                            className="badge text-bg-secondary"
                          >
                            {skill.skill_name}

                            {" · "}

                            {skill.minimum_level}
                          </span>

                        )
                      )}

                    </div>

                  </div>

                )}


                {submission ? (

                  <div className="alert alert-secondary mb-0">

                    Submitted

                    {" · "}

                    <strong className="text-capitalize">
                      {
                        submission.status
                          .replaceAll(
                            "_",
                            " "
                          )
                      }
                    </strong>

                  </div>

                ) : (

                  <>

                    <button
                      type="button"
                      className="btn btn-info"
                      onClick={() =>
                        openSubmission(
                          challenge.id
                        )
                      }
                    >
                      {selectedId
                      === challenge.id
                        ? "Cancel"
                        : "Submit Solution"}
                    </button>


                    {selectedId
                    === challenge.id && (

                      <div className="border rounded p-4 mt-3">

                        <div className="mb-3">

                          <label className="form-label">
                            Solution Description
                          </label>

                          <textarea
                            rows="6"
                            className="form-control"
                            value={
                              form.submission_text
                            }
                            onChange={(event) =>
                              updateField(
                                "submission_text",
                                event.target.value
                              )
                            }
                          />

                        </div>


                        <div className="mb-3">

                          <label className="form-label">
                            Repository URL
                          </label>

                          <input
                            type="url"
                            className="form-control"
                            value={
                              form.repository_url
                            }
                            onChange={(event) =>
                              updateField(
                                "repository_url",
                                event.target.value
                              )
                            }
                          />

                        </div>


                        <div className="mb-3">

                          <label className="form-label">
                            Demo URL
                          </label>

                          <input
                            type="url"
                            className="form-control"
                            value={
                              form.demo_url
                            }
                            onChange={(event) =>
                              updateField(
                                "demo_url",
                                event.target.value
                              )
                            }
                          />

                        </div>


                        <button
                          type="button"
                          className="btn btn-success"
                          disabled={submitting}
                          onClick={() =>
                            submitSolution(
                              challenge.id
                            )
                          }
                        >
                          {submitting
                            ? "Submitting..."
                            : "Confirm Submission"}
                        </button>

                      </div>

                    )}

                  </>

                )}

              </div>

            );

          }
        )}

      </>
    );
  }