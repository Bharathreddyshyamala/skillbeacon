import {
    useEffect,
    useState,
  } from "react";
  
  import {
    apiRequest,
  } from "../api";
  
  
  const TERMINAL = [
    "accepted",
    "rejected",
    "withdrawn",
  ];
  
  
  export default function Applications() {
  
    const [items, setItems] =
      useState([]);
  
    const [loading, setLoading] =
      useState(true);
  
    const [error, setError] =
      useState("");
  
    const [message, setMessage] =
      useState("");
  
  
    async function loadApplications() {
  
      setLoading(true);
  
      setError("");
  
  
      try {
  
        const response =
          await apiRequest(
            "/applications/me?limit=100"
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
          "Unable to load applications."
        );
  
      } finally {
  
        setLoading(false);
  
      }
    }
  
  
    useEffect(() => {
  
      loadApplications();
  
    }, []);
  
  
    async function withdraw(
      applicationId,
    ) {
  
      const confirmed =
        window.confirm(
          "Withdraw this application?"
        );
  
  
      if (!confirmed) {
        return;
      }
  
  
      setError("");
      setMessage("");
  
  
      try {
  
        await apiRequest(
          `/applications/${applicationId}/withdraw`,
          {
            method: "PATCH",
          }
        );
  
  
        setMessage(
          "Application withdrawn."
        );
  
  
        await loadApplications();
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to withdraw application."
        );
  
      }
    }
  
  
    function badgeClass(status) {
  
      switch (status) {
  
        case "accepted":
          return "text-bg-success";
  
        case "rejected":
          return "text-bg-danger";
  
        case "shortlisted":
          return "text-bg-info";
  
        case "withdrawn":
          return "text-bg-secondary";
  
        case "under_review":
          return "text-bg-warning";
  
        default:
          return "text-bg-primary";
      }
    }
  
  
    return (
      <>
  
        <div className="mb-4">
  
          <p className="text-info fw-semibold text-uppercase">
            Applications
          </p>
  
          <h1 className="display-6 fw-bold">
            My Applications
          </h1>
  
          <p className="text-secondary">
            Track opportunities you have
            applied to.
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
  
  
        {loading && (
          <p className="text-secondary">
            Loading applications...
          </p>
        )}
  
  
        {
          !loading &&
          !error &&
          items.length === 0 && (
  
            <div className="glass-card">
  
              <p className="text-secondary mb-0">
                You have not submitted any
                applications yet.
              </p>
  
            </div>
  
          )
        }
  
  
        {items.map((item) => (
  
          <div
            key={item.id}
            className="glass-card mb-3"
          >
  
            <div className="d-flex justify-content-between align-items-start gap-3">
  
              <div>
  
                <h2 className="h5 mb-1">
                  {
                    item.opportunity_title
                  }
                </h2>
  
                <p className="text-secondary mb-2">
                  {item.company_name}
                </p>
  
                <span
                  className={
                    `badge ${
                      badgeClass(
                        item.status
                      )
                    } text-capitalize`
                  }
                >
                  {
                    item.status.replaceAll(
                      "_",
                      " "
                    )
                  }
                </span>
  
              </div>
  
  
              {
                !TERMINAL.includes(
                  item.status
                ) && (
  
                  <button
                    className="btn btn-outline-danger btn-sm"
                    type="button"
                    onClick={() =>
                      withdraw(
                        item.id
                      )
                    }
                  >
                    Withdraw
                  </button>
  
                )
              }
  
            </div>
  
  
            <div className="row mt-4 small">
  
              <div className="col-md-4">
                <span className="text-secondary">
                  Type
                </span>
  
                <div className="text-capitalize">
                  {
                    item
                      .opportunity_type
                  }
                </div>
              </div>
  
  
              <div className="col-md-4">
                <span className="text-secondary">
                  Submitted
                </span>
  
                <div>
                  {
                    new Date(
                      item.created_at
                    )
                    .toLocaleDateString()
                  }
                </div>
              </div>
  
  
              <div className="col-md-4">
                <span className="text-secondary">
                  Last Updated
                </span>
  
                <div>
                  {
                    new Date(
                      item.updated_at
                    )
                    .toLocaleDateString()
                  }
                </div>
              </div>
  
              {item.resume_available && (
                <div className="col-12 mt-3 pt-2 border-top border-secondary border-opacity-25">
                  <a
                    href={item.resume_url || `/api/applications/${item.id}/resume`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-outline-info btn-sm"
                  >
                    View Submitted Résumé
                  </a>
                </div>
              )}
  
            </div>
  
          </div>
  
        ))}
  
      </>
    );
  }