import { useEffect, useState } from "react";

import {
  apiRequest,
  jsonBody,
} from "../api";


export default function Verifications() {
  const [items, setItems] =
    useState([]);

  const [comments, setComments] =
    useState({});

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");

  const [loading, setLoading] =
    useState(true);


  async function loadEvidence() {
    setError("");

    try {
      const response = await apiRequest(
        "/skills/evidence/pending"
      );

      setItems(
        Array.isArray(response)
          ? response
          : []
      );

    } catch (requestError) {
      setError(
        requestError.message ||
        "Unable to load pending evidence."
      );
    } finally {
      setLoading(false);
    }
  }


  useEffect(() => {
    loadEvidence();
  }, []);


  async function reviewEvidence(
    evidenceId,
    status,
  ) {
    setError("");
    setMessage("");

    try {
      await apiRequest(
        `/skills/evidence/${evidenceId}/verify`,
        {
          method: "POST",

          body: jsonBody({
            status,

            comments:
              comments[evidenceId]
              || null,
          }),
        },
      );

      setMessage(
        status === "approved"
          ? "Evidence approved."
          : "Evidence rejected."
      );

      await loadEvidence();

    } catch (requestError) {
      setError(
        requestError.message ||
        "Unable to review evidence."
      );
    }
  }


  if (loading) {
    return (
      <p className="text-secondary">
        Loading verification requests...
      </p>
    );
  }


  return (
    <>
      <div className="mb-4">

        <p className="text-info fw-semibold text-uppercase">
          Verification
        </p>

        <h1 className="display-6 fw-bold">
          Evidence Review
        </h1>

        <p className="text-secondary">
          Review skill evidence submitted
          by SkillBeacon users.
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


      {items.length === 0 && (
        <div className="glass-card">
          <p className="text-secondary mb-0">
            No evidence is waiting for
            verification.
          </p>
        </div>
      )}


      {items.map((item) => (
        <div
          key={item.id}
          className="glass-card mb-4"
        >

          <div className="d-flex justify-content-between gap-3">

            <div>
              <p className="text-info small text-uppercase mb-1">
                {item.skill_name}
              </p>

              <h2 className="h4">
                {item.title}
              </h2>
            </div>

            <span className="badge text-bg-warning">
              Pending
            </span>

          </div>


          <div className="row mt-3">

            <div className="col-md-6">
              <small className="text-secondary">
                Submitted by
              </small>

              <p>
                {item.owner_email}
              </p>
            </div>


            <div className="col-md-3">
              <small className="text-secondary">
                Level
              </small>

              <p className="text-capitalize">
                {item.level}
              </p>
            </div>


            <div className="col-md-3">
              <small className="text-secondary">
                Evidence type
              </small>

              <p className="text-capitalize">
                {item.evidence_type.replaceAll(
                  "_",
                  " "
                )}
              </p>
            </div>

          </div>


          {item.description && (
            <p className="text-secondary">
              {item.description}
            </p>
          )}


          {item.url && (
            <a
              href={item.url}
              target="_blank"
              rel="noreferrer"
              className="btn btn-outline-info btn-sm mb-3"
            >
              View Evidence
            </a>
          )}


          <div className="mb-3">

            <label className="form-label">
              Review comments
            </label>

            <textarea
              className="form-control"
              rows="3"
              value={
                comments[item.id] || ""
              }
              onChange={(event) =>
                setComments({
                  ...comments,

                  [item.id]:
                    event.target.value,
                })
              }
              placeholder="Add comments about this evidence..."
            />

          </div>


          <div className="d-flex gap-2">

            <button
              className="btn btn-success"
              type="button"
              onClick={() =>
                reviewEvidence(
                  item.id,
                  "approved",
                )
              }
            >
              Approve
            </button>


            <button
              className="btn btn-outline-danger"
              type="button"
              onClick={() =>
                reviewEvidence(
                  item.id,
                  "rejected",
                )
              }
            >
              Reject
            </button>

          </div>

        </div>
      ))}
    </>
  );
}