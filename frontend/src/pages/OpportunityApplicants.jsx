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
      "rejected",
    ],
  
    under_review: [
      "shortlisted",
      "rejected",
    ],
  
    shortlisted: [
      "accepted",
      "rejected",
    ],
  
    accepted: [],
  
    rejected: [],
  
    withdrawn: [],
  };
  
  
  export default function OpportunityApplicants() {
  
    const {
      opportunityId,
    } = useParams();
  
  
    const [items, setItems] =
      useState([]);
  
    const [statusFilter, setStatusFilter] =
      useState("");
  
    const [notes, setNotes] =
      useState({});
  
    const [error, setError] =
      useState("");
  
    const [message, setMessage] =
      useState("");
  
  
    async function loadApplicants() {
  
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
            `/opportunities/${opportunityId}/applications?${params.toString()}`
          );
  
  
        const loadedItems =
          Array.isArray(
            response?.items
          )
            ? response.items
            : [];
  
  
        setItems(
          loadedItems
        );
  
  
        const initialNotes = {};
  
  
        loadedItems.forEach(
          (item) => {
  
            initialNotes[
              item.id
            ] = (
              item.employer_note
              || ""
            );
  
          }
        );
  
  
        setNotes(
          initialNotes
        );
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to load applicants."
        );
  
      }
    }
  
  
    useEffect(() => {
  
      loadApplicants();
  
    }, [statusFilter]);
  
  
    async function changeStatus(
      applicationId,
      newStatus,
    ) {
  
      setError("");
      setMessage("");
  
  
      try {
  
        await apiRequest(
          `/applications/${applicationId}/status`,
          {
            method: "PATCH",
  
            body: jsonBody({
              status:
                newStatus,
  
              employer_note:
                notes[
                  applicationId
                ] || null,
            }),
          }
        );
  
  
        setMessage(
          "Application status updated."
        );
  
  
        await loadApplicants();
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to update application."
        );
  
      }
    }
  
  
    async function saveNote(
      applicationId,
    ) {
  
      try {
  
        await apiRequest(
          `/applications/${applicationId}/note`,
          {
            method: "PATCH",
  
            body: jsonBody({
              employer_note:
                notes[
                  applicationId
                ] || null,
            }),
          }
        );
  
  
        setMessage(
          "Private note saved."
        );
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to save note."
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
            Applicants
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
            Filter by Status
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
  
            <option value="shortlisted">
              Shortlisted
            </option>
  
            <option value="accepted">
              Accepted
            </option>
  
            <option value="rejected">
              Rejected
            </option>
  
            <option value="withdrawn">
              Withdrawn
            </option>
  
          </select>
  
        </div>
  
  
        {items.length === 0 && (
  
          <div className="glass-card">
  
            <p className="text-secondary mb-0">
              No applicants found.
            </p>
  
          </div>
  
        )}
  
  
        {items.map((item) => {
  
          const snapshot =
            item.profile_snapshot
            || {};
  
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
  
                  <h2 className="h4">
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
  
  
              {snapshot.headline && (
  
                <p>
                  <strong>
                    Headline:
                  </strong>
  
                  {" "}
  
                  {snapshot.headline}
                </p>
  
              )}
  
  
              {snapshot.summary && (
  
                <p>
                  {snapshot.summary}
                </p>
  
              )}
  
  
              <h3 className="h6">
                Skills
              </h3>
  
  
              <div className="d-flex flex-wrap gap-2 mb-4">
  
                {
                  (snapshot.skills || [])
                  .map(
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
                  )
                }
  
              </div>
  
  
              <h3 className="h6">
                Cover Letter
              </h3>
  
  
              <p className="text-secondary">
                {
                  item.cover_letter ||
                  "No cover letter submitted."
                }
              </p>
  
  
              {item.resume_available && (
  
                <button
                  type="button"
                  className="btn btn-outline-info btn-sm mb-4"
                  onClick={() =>
                    downloadResume(
                      item.id
                    )
                  }
                >
                  Download Résumé
                </button>
  
              )}
  
  
              <div className="mb-3">
  
                <label className="form-label">
                  Private Employer Note
                </label>
  
                <textarea
                  className="form-control"
                  rows="3"
                  value={
                    notes[item.id]
                    || ""
                  }
                  onChange={(event) =>
                    setNotes({
                      ...notes,
  
                      [item.id]:
                        event.target.value,
                    })
                  }
                />
  
                <button
                  type="button"
                  className="btn btn-outline-secondary btn-sm mt-2"
                  onClick={() =>
                    saveNote(
                      item.id
                    )
                  }
                >
                  Save Note
                </button>
  
              </div>
  
  
              {
                nextStatuses.length > 0 && (
  
                  <div>
  
                    <h3 className="h6">
                      Move Application
                    </h3>
  
  
                    <div className="d-flex flex-wrap gap-2">
  
                      {nextStatuses.map(
                        (nextStatus) => (
  
                          <button
                            type="button"
                            key={nextStatus}
                            className="btn btn-outline-info btn-sm"
                            onClick={() =>
                              changeStatus(
                                item.id,
                                nextStatus
                              )
                            }
                          >
  
                            {
                              nextStatus
                                .replaceAll(
                                  "_",
                                  " "
                                )
                            }
  
                          </button>
  
                        )
                      )}
  
                    </div>
  
                  </div>
  
                )
              }
  
            </div>
  
          );
  
        })}
  
      </>
    );
  }