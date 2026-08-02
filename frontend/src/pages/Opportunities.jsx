import {
    useEffect,
    useState,
  } from "react";
  
  import {
    apiRequest,
  } from "../api";
  
  
  export default function Opportunities() {
  
    const [items, setItems] =
      useState([]);
  
    const [search, setSearch] =
      useState("");
  
    const [workMode, setWorkMode] =
      useState("");
  
    const [opportunityType, setOpportunityType] =
      useState("");
  
    const [loading, setLoading] =
      useState(true);
  
    const [error, setError] =
      useState("");
  
  
    async function loadOpportunities() {
  
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
  
  
        if (workMode) {
  
          params.set(
            "work_mode",
            workMode
          );
  
        }
  
  
        if (opportunityType) {
  
          params.set(
            "opportunity_type",
            opportunityType
          );
  
        }
  
  
        const query =
          params.toString();
  
  
        const response =
          await apiRequest(
            `/opportunities${
              query
                ? `?${query}`
                : ""
            }`
          );
  
  
        setItems(
          Array.isArray(response)
            ? response
            : []
        );
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to load opportunities."
        );
  
      } finally {
  
        setLoading(false);
  
      }
    }
  
  
    useEffect(() => {
  
      loadOpportunities();
  
    }, []);
  
  
    function handleSearch(event) {
  
      event.preventDefault();
  
      loadOpportunities();
  
    }
  
  
    return (
      <>
  
        <div className="mb-4">
  
          <p className="text-info fw-semibold text-uppercase">
            Opportunities
          </p>
  
          <h1 className="display-6 fw-bold">
            Discover Opportunities
          </h1>
  
          <p className="text-secondary">
            Explore jobs, internships,
            projects, and volunteer
            opportunities.
          </p>
  
        </div>
  
  
        <div className="glass-card mb-4">
  
          <form
            className="row g-3"
            onSubmit={handleSearch}
          >
  
            <div className="col-lg-5">
  
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
                placeholder="Backend, Python, company..."
              />
  
            </div>
  
  
            <div className="col-lg-3">
  
              <label className="form-label">
                Work Mode
              </label>
  
              <select
                className="form-select"
                value={workMode}
                onChange={(event) =>
                  setWorkMode(
                    event.target.value
                  )
                }
              >
  
                <option value="">
                  All
                </option>
  
                <option value="remote">
                  Remote
                </option>
  
                <option value="hybrid">
                  Hybrid
                </option>
  
                <option value="onsite">
                  Onsite
                </option>
  
              </select>
  
            </div>
  
  
            <div className="col-lg-3">
  
              <label className="form-label">
                Type
              </label>
  
              <select
                className="form-select"
                value={opportunityType}
                onChange={(event) =>
                  setOpportunityType(
                    event.target.value
                  )
                }
              >
  
                <option value="">
                  All
                </option>
  
                <option value="job">
                  Job
                </option>
  
                <option value="internship">
                  Internship
                </option>
  
                <option value="project">
                  Project
                </option>
  
                <option value="volunteer">
                  Volunteer
                </option>
  
              </select>
  
            </div>
  
  
            <div className="col-lg-1 d-flex align-items-end">
  
              <button
                className="btn btn-info w-100"
                type="submit"
              >
                Go
              </button>
  
            </div>
  
          </form>
  
        </div>
  
  
        {error && (
  
          <div className="alert alert-danger">
            {error}
          </div>
  
        )}
  
  
        {loading && (
  
          <p className="text-secondary">
            Loading opportunities...
          </p>
  
        )}
  
  
        {
          !loading &&
          !error &&
          items.length === 0 && (
  
            <div className="glass-card">
  
              <p className="text-secondary mb-0">
                No open opportunities found.
              </p>
  
            </div>
  
          )
        }
  
  
        {items.map(
          (item) => (
  
            <div
              key={item.id}
              className="glass-card mb-4"
            >
  
              <div className="d-flex justify-content-between gap-3 flex-wrap">
  
                <div>
  
                  <p className="text-info text-uppercase small mb-1">
                    {item.opportunity_type}
                  </p>
  
                  <h2 className="h4 mb-1">
                    {item.title}
                  </h2>
  
                  <p className="text-secondary">
                    {item.company_name}
                  </p>
  
                </div>
  
  
                <span className="badge text-bg-info text-capitalize">
                  {item.work_mode}
                </span>
  
              </div>
  
  
              <p>
                {item.description}
              </p>
  
  
              <div className="row small mb-3">
  
                <div className="col-md-4">
  
                  <span className="text-secondary">
                    Location
                  </span>
  
                  <div>
                    {
                      item.location ||
                      "Not specified"
                    }
                  </div>
  
                </div>
  
  
                <div className="col-md-4">
  
                  <span className="text-secondary">
                    Employment
                  </span>
  
                  <div className="text-capitalize">
  
                    {
                      item.employment_type
                        ?.replaceAll(
                          "_",
                          " "
                        ) ||
                      "Not specified"
                    }
  
                  </div>
  
                </div>
  
  
                <div className="col-md-4">
  
                  <span className="text-secondary">
                    Deadline
                  </span>
  
                  <div>
                    {
                      item.deadline ||
                      "Open"
                    }
                  </div>
  
                </div>
  
              </div>
  
  
              {
                (
                  item.salary_min ||
                  item.salary_max
                ) && (
  
                  <p>
  
                    <strong>
                      Compensation:
                    </strong>
  
                    {" "}
  
                    {item.currency}
  
                    {" "}
  
                    {
                      item.salary_min ??
                      "—"
                    }
  
                    {" - "}
  
                    {
                      item.salary_max ??
                      "—"
                    }
  
                  </p>
  
                )
              }
  
  
              <div className="mt-3">
  
                <h3 className="h6">
                  Required Skills
                </h3>
  
  
                <div className="d-flex flex-wrap gap-2">
  
                  {
                    (item.skills || []).map(
                      (requirement) => (
  
                        <span
                          key={requirement.id}
                          className="badge rounded-pill text-bg-secondary"
                        >
  
                          {
                            requirement.skill
                              .name
                          }
  
                          {" · "}
  
                          {
                            requirement
                              .minimum_level
                          }
  
                        </span>
  
                      )
                    )
                  }
  
                </div>
  
              </div>
  
  
              {
                item.application_url && (
  
                  <div className="mt-4">
  
                    <a
                      href={
                        item.application_url
                      }
                      target="_blank"
                      rel="noreferrer"
                      className="btn btn-outline-info"
                    >
  
                      External Application Link
  
                    </a>
  
                  </div>
  
                )
              }
  
            </div>
  
          )
        )}
  
      </>
    );
  }