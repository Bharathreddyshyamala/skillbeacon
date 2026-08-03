import {
    useEffect,
    useState,
  } from "react";
  
  import {
    useNavigate,
  } from "react-router";
  
  import {
    apiRequest,
    jsonBody,
  } from "../api";
  
  
  export default function Opportunities() {
  
    // =========================================================
    // Navigation
    // =========================================================
  
    const navigate =
      useNavigate();
  
  
    // =========================================================
    // Opportunities
    // =========================================================
  
    const [items, setItems] =
      useState([]);
  
  
    // =========================================================
    // Student application information
    // =========================================================
  
    const [
      applications,
      setApplications,
    ] = useState([]);
  
  
    const [
      applyingId,
      setApplyingId,
    ] = useState("");
  
  
    const [
      coverLetter,
      setCoverLetter,
    ] = useState("");
  
  
    // Student profile used only to show
    // the student what information will
    // be captured with the application.
    const [
      profile,
      setProfile,
    ] = useState(null);
  
  
    // Current Skill Passport
    const [
      mySkills,
      setMySkills,
    ] = useState([]);
  
  
    // =========================================================
    // Filters
    // =========================================================
  
    const [search, setSearch] =
      useState("");
  
  
    const [workMode, setWorkMode] =
      useState("");
  
  
    const [
      opportunityType,
      setOpportunityType,
    ] = useState("");
  
  
    // =========================================================
    // UI state
    // =========================================================
  
    const [loading, setLoading] =
      useState(true);
  
  
    const [submitting, setSubmitting] =
      useState(false);
  
  
    const [error, setError] =
      useState("");
  
  
    const [message, setMessage] =
      useState("");
  
  
    // =========================================================
    // Load Opportunities
    // =========================================================
  
    async function loadOpportunities() {
  
      setLoading(true);
  
      setError("");
  
  
      try {
  
        // ---------------------------------------
        // Build opportunity filters
        // ---------------------------------------
  
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
  
  
        // ---------------------------------------
        // Load all student-related information
        // ---------------------------------------
  
        const [
          opportunityResponse,
          applicationResponse,
          profileResponse,
          skillsResponse,
        ] = await Promise.all([
  
          apiRequest(
            `/opportunities${
              query
                ? `?${query}`
                : ""
            }`
          ),
  
          apiRequest(
            "/applications/me?limit=100"
          ),
  
          apiRequest(
            "/profiles/me"
          ),
  
          apiRequest(
            "/skills/me"
          ),
  
        ]);
  
  
        // ---------------------------------------
        // Opportunities
        // ---------------------------------------
  
        setItems(
          Array.isArray(
            opportunityResponse
          )
            ? opportunityResponse
            : []
        );
  
  
        // ---------------------------------------
        // Existing applications
        // ---------------------------------------
  
        setApplications(
          Array.isArray(
            applicationResponse?.items
          )
            ? applicationResponse.items
            : []
        );
  
  
        // ---------------------------------------
        // Profile
        // ---------------------------------------
  
        setProfile(
          profileResponse || null
        );
  
  
        // ---------------------------------------
        // Skill Passport
        // ---------------------------------------
  
        setMySkills(
          Array.isArray(
            skillsResponse
          )
            ? skillsResponse
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
  
  
    // =========================================================
    // Initial Load
    // =========================================================
  
    useEffect(() => {
  
      loadOpportunities();
  
    }, []);
  
  
    // =========================================================
    // Search
    // =========================================================
  
    function handleSearch(event) {
  
      event.preventDefault();
  
      loadOpportunities();
  
    }
  
  
    // =========================================================
    // Clear Filters
    // =========================================================
  
    function clearFilters() {
  
      setSearch("");
  
      setWorkMode("");
  
      setOpportunityType("");
  
  
      // State updates are asynchronous,
      // so directly fetch all opportunities here.
  
      setLoading(true);
  
      setError("");
  
  
      Promise.all([
  
        apiRequest(
          "/opportunities"
        ),
  
        apiRequest(
          "/applications/me?limit=100"
        ),
  
        apiRequest(
          "/profiles/me"
        ),
  
        apiRequest(
          "/skills/me"
        ),
  
      ])
        .then(
          ([
            opportunityResponse,
            applicationResponse,
            profileResponse,
            skillsResponse,
          ]) => {
  
            setItems(
              Array.isArray(
                opportunityResponse
              )
                ? opportunityResponse
                : []
            );
  
  
            setApplications(
              Array.isArray(
                applicationResponse?.items
              )
                ? applicationResponse.items
                : []
            );
  
  
            setProfile(
              profileResponse || null
            );
  
  
            setMySkills(
              Array.isArray(
                skillsResponse
              )
                ? skillsResponse
                : []
            );
  
          }
        )
        .catch(
          (requestError) => {
  
            setError(
              requestError.message ||
              "Unable to load opportunities."
            );
  
          }
        )
        .finally(
          () => {
  
            setLoading(false);
  
          }
        );
    }
  
  
    // =========================================================
    // Find Existing Application
    // =========================================================
  
    function existingApplication(
      opportunityId,
    ) {
  
      return applications.find(
        (application) =>
          application.opportunity_id
          === opportunityId
      );
    }
  
  
    // =========================================================
    // Open / Close Apply Form
    // =========================================================
  
    function toggleApplyForm(
      opportunityId,
    ) {
  
      setError("");
  
      setMessage("");
  
  
      if (
        applyingId
        === opportunityId
      ) {
  
        setApplyingId("");
  
        setCoverLetter("");
  
        return;
      }
  
  
      setApplyingId(
        opportunityId
      );
  
  
      setCoverLetter("");
  
    }
  
  
    // =========================================================
    // Submit Application
    // =========================================================
  
    async function apply(
      opportunityId,
    ) {
  
      setError("");
  
      setMessage("");
  
  
      // Browser-side duplicate protection.
      // Backend also protects this with
      // the unique database constraint.
  
      const existing =
        existingApplication(
          opportunityId
        );
  
  
      if (existing) {
  
        setError(
          "You already applied to this opportunity."
        );
  
        return;
      }
  
  
      const confirmed =
        window.confirm(
          "Submit this application? Your current profile, skills, and résumé availability will be captured."
        );
  
  
      if (!confirmed) {
  
        return;
  
      }
  
  
      setSubmitting(true);
  
  
      try {
  
        await apiRequest(
          "/applications",
          {
            method: "POST",
  
            body: jsonBody({
  
              opportunity_id:
                opportunityId,
  
              cover_letter:
                coverLetter.trim()
                  || null,
  
            }),
          }
        );
  
  
        setMessage(
          "Application submitted successfully."
        );
  
  
        setApplyingId("");
  
        setCoverLetter("");
  
  
        // Reload data so the Apply button
        // immediately changes to
        // View Application.
  
        await loadOpportunities();
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to submit application."
        );
  
      } finally {
  
        setSubmitting(false);
  
      }
    }
  
  
    // =========================================================
    // Application Status Badge
    // =========================================================
  
    function applicationBadgeClass(
      status,
    ) {
  
      switch (status) {
  
        case "accepted":
  
          return "text-bg-success";
  
  
        case "rejected":
  
          return "text-bg-danger";
  
  
        case "shortlisted":
  
          return "text-bg-info";
  
  
        case "under_review":
  
          return "text-bg-warning";
  
  
        case "withdrawn":
  
          return "text-bg-secondary";
  
  
        default:
  
          return "text-bg-primary";
  
      }
    }
  
  
    // =========================================================
    // Profile helpers
    // =========================================================
  
    // Depending on how /profiles/me is shaped,
    // profile may be returned directly or inside
    // a "profile" property.
  
    const studentProfile =
      profile?.profile
      || profile
      || {};
  
  
    const resumeAvailable =
      Boolean(
        studentProfile?.resume_path
        || studentProfile?.resume_available
      );
  
  
    const studentName = [
  
      studentProfile?.first_name,
  
      studentProfile?.last_name,
  
    ]
      .filter(Boolean)
      .join(" ");
  
  
    // =========================================================
    // UI
    // =========================================================
  
    return (
      <>
  
        {/* =====================================================
            PAGE HEADER
        ====================================================== */}
  
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
  
  
        {/* =====================================================
            SUCCESS MESSAGE
        ====================================================== */}
  
        {message && (
  
          <div className="alert alert-success">
            {message}
          </div>
  
        )}
  
  
        {/* =====================================================
            ERROR MESSAGE
        ====================================================== */}
  
        {error && (
  
          <div className="alert alert-danger">
            {error}
          </div>
  
        )}
  
  
        {/* =====================================================
            FILTERS
        ====================================================== */}
  
        <div className="glass-card mb-4">
  
          <form
            className="row g-3"
            onSubmit={
              handleSearch
            }
          >
  
            {/* Search */}
  
            <div className="col-lg-4">
  
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
  
  
            {/* Work Mode */}
  
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
  
  
            {/* Opportunity Type */}
  
            <div className="col-lg-3">
  
              <label className="form-label">
                Type
              </label>
  
  
              <select
                className="form-select"
                value={
                  opportunityType
                }
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
  
  
            {/* Search Button */}
  
            <div className="col-lg-1 d-flex align-items-end">
  
              <button
                className="btn btn-info w-100"
                type="submit"
              >
                Go
              </button>
  
            </div>
  
  
            {/* Clear Button */}
  
            <div className="col-lg-1 d-flex align-items-end">
  
              <button
                className="btn btn-outline-secondary w-100"
                type="button"
                onClick={
                  clearFilters
                }
              >
                Clear
              </button>
  
            </div>
  
          </form>
  
        </div>
  
  
        {/* =====================================================
            LOADING
        ====================================================== */}
  
        {loading && (
  
          <p className="text-secondary">
            Loading opportunities...
          </p>
  
        )}
  
  
        {/* =====================================================
            EMPTY STATE
        ====================================================== */}
  
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
  
  
        {/* =====================================================
            OPPORTUNITY CARDS
        ====================================================== */}
  
        {
          !loading &&
          items.map(
            (item) => {
  
              const application =
                existingApplication(
                  item.id
                );
  
  
              return (
  
                <div
                  key={item.id}
                  className="glass-card mb-4"
                >
  
                  {/* -------------------------------------------
                      Header
                  -------------------------------------------- */}
  
                  <div className="d-flex justify-content-between gap-3 flex-wrap">
  
                    <div>
  
                      <p className="text-info text-uppercase small mb-1">
  
                        {
                          item.opportunity_type
                        }
  
                      </p>
  
  
                      <h2 className="h4 mb-1">
  
                        {item.title}
  
                      </h2>
  
  
                      <p className="text-secondary">
  
                        {
                          item.company_name
                        }
  
                      </p>
  
                    </div>
  
  
                    <div className="d-flex flex-column align-items-end gap-2">
  
                      <span className="badge text-bg-info text-capitalize">
  
                        {
                          item.work_mode
                        }
  
                      </span>
  
  
                      {/* Existing Application Status */}
  
                      {
                        application && (
  
                          <span
                            className={
                              `badge ${
                                applicationBadgeClass(
                                  application.status
                                )
                              } text-capitalize`
                            }
                          >
  
                            {
                              application.status
                                .replaceAll(
                                  "_",
                                  " "
                                )
                            }
  
                          </span>
  
                        )
                      }
  
                    </div>
  
                  </div>
  
  
                  {/* -------------------------------------------
                      Description
                  -------------------------------------------- */}
  
                  <p>
                    {item.description}
                  </p>
  
  
                  {/* -------------------------------------------
                      Opportunity Details
                  -------------------------------------------- */}
  
                  <div className="row small mb-3">
  
                    {/* Location */}
  
                    <div className="col-md-4">
  
                      <span className="text-secondary">
                        Location
                      </span>
  
  
                      <div>
  
                        {
                          item.location
                          || "Not specified"
                        }
  
                      </div>
  
                    </div>
  
  
                    {/* Employment */}
  
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
                            )
                          || "Not specified"
                        }
  
                      </div>
  
                    </div>
  
  
                    {/* Deadline */}
  
                    <div className="col-md-4">
  
                      <span className="text-secondary">
                        Deadline
                      </span>
  
  
                      <div>
  
                        {
                          item.deadline
                          || "Open"
                        }
  
                      </div>
  
                    </div>
  
                  </div>
  
  
                  {/* -------------------------------------------
                      Compensation
                  -------------------------------------------- */}
  
                  {
                    (
                      item.salary_min
                      || item.salary_max
                    ) && (
  
                      <p>
  
                        <strong>
                          Compensation:
                        </strong>
  
                        {" "}
  
                        {item.currency}
  
                        {" "}
  
                        {
                          item.salary_min
                          ?? "—"
                        }
  
                        {" - "}
  
                        {
                          item.salary_max
                          ?? "—"
                        }
  
                      </p>
  
                    )
                  }
  
  
                  {/* -------------------------------------------
                      Required Skills
                  -------------------------------------------- */}
  
                  <div className="mt-3">
  
                    <h3 className="h6">
                      Required Skills
                    </h3>
  
  
                    {
                      (
                        item.skills
                        || []
                      ).length === 0 ? (
  
                        <p className="small text-secondary">
  
                          No required skills specified.
  
                        </p>
  
                      ) : (
  
                        <div className="d-flex flex-wrap gap-2">
  
                          {
                            (
                              item.skills
                              || []
                            ).map(
                              (
                                requirement
                              ) => (
  
                                <span
                                  key={
                                    requirement.id
                                  }
                                  className="badge rounded-pill text-bg-secondary"
                                >
  
                                  {
                                    requirement
                                      .skill
                                      ?.name
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
  
                      )
                    }
  
                  </div>
  
  
                  {/* =================================================
                      APPLICATION ACTION
                  ================================================== */}
  
                  <div className="mt-4">
  
  
                    {/* -----------------------------------------------
                        Already Applied
                    ------------------------------------------------ */}
  
                    {
                      application ? (
  
                        <div>
  
                          <div className="alert alert-secondary py-2">
  
                            You already applied to
                            this opportunity.
  
                            {" "}
  
                            Current status:
  
                            {" "}
  
                            <strong className="text-capitalize">
  
                              {
                                application.status
                                  .replaceAll(
                                    "_",
                                    " "
                                  )
                              }
  
                            </strong>
  
                          </div>
  
  
                          <button
                            className="btn btn-outline-info"
                            type="button"
                            onClick={() =>
                              navigate(
                                "/app/applications"
                              )
                            }
                          >
  
                            View Application
  
                          </button>
  
                        </div>
  
                      ) : (
  
                        /* -------------------------------------------
                            Apply Button
                        -------------------------------------------- */
  
                        <div>
  
                          <button
                            className="btn btn-info"
                            type="button"
                            onClick={() =>
                              toggleApplyForm(
                                item.id
                              )
                            }
                          >
  
                            {
                              applyingId
                              === item.id
                                ? "Cancel Application"
                                : "Apply"
                            }
  
                          </button>
  
  
                          {/* =========================================
                              APPLY FORM
                          ========================================== */}
  
                          {
                            applyingId
                            === item.id && (
  
                              <div className="border rounded p-4 mt-3">
  
  
                                <h3 className="h5 mb-3">
  
                                  Apply to{" "}
  
                                  {item.title}
  
                                </h3>
  
  
                                <p className="text-secondary small">
  
                                  SkillBeacon will capture a
                                  snapshot of your current profile,
                                  Skill Passport, and résumé
                                  availability when you submit.
  
                                </p>
  
  
                                {/* -------------------------------
                                    Profile Summary
                                -------------------------------- */}
  
                                <div className="mb-4">
  
                                  <h4 className="h6">
                                    Current Profile
                                  </h4>
  
  
                                  {
                                    studentName && (
  
                                      <p className="mb-1">
  
                                        <strong>
                                          {studentName}
                                        </strong>
  
                                      </p>
  
                                    )
                                  }
  
  
                                  {
                                    studentProfile
                                      ?.headline && (
  
                                      <p className="text-secondary mb-1">
  
                                        {
                                          studentProfile
                                            .headline
                                        }
  
                                      </p>
  
                                    )
                                  }
  
  
                                  {
                                    studentProfile
                                      ?.summary && (
  
                                      <p className="small text-secondary mb-0">
  
                                        {
                                          studentProfile
                                            .summary
                                        }
  
                                      </p>
  
                                    )
                                  }
  
                                </div>
  
  
                                {/* -------------------------------
                                    Skill Passport Preview
                                -------------------------------- */}
  
                                <div className="mb-4">
  
                                  <h4 className="h6">
                                    Current Skills
                                  </h4>
  
  
                                  {
                                    mySkills.length
                                    === 0 ? (
  
                                      <p className="small text-secondary">
  
                                        No skills currently
                                        added to your Skill
                                        Passport.
  
                                      </p>
  
                                    ) : (
  
                                      <div className="d-flex flex-wrap gap-2">
  
                                        {
                                          mySkills.map(
                                            (
                                              userSkill
                                            ) => (
  
                                              <span
                                                key={
                                                  userSkill.id
                                                }
                                                className="badge text-bg-secondary"
                                              >
  
                                                {
                                                  userSkill
                                                    .skill
                                                    ?.name
                                                }
  
                                                {" · "}
  
                                                {
                                                  userSkill
                                                    .level
                                                }
  
                                              </span>
  
                                            )
                                          )
                                        }
  
                                      </div>
  
                                    )
                                  }
  
                                </div>
  
  
                                {/* -------------------------------
                                    Résumé Availability
                                -------------------------------- */}
  
                                <div className="mb-4">
  
                                  <h4 className="h6">
                                    Résumé
                                  </h4>
  
  
                                  {
                                    resumeAvailable ? (
  
                                      <p className="small text-success mb-0">
  
                                        ✓ Résumé available.
                                        Your current résumé
                                        will be associated with
                                        this application.
  
                                      </p>
  
                                    ) : (
  
                                      <div className="alert alert-warning py-2 mb-0">
  
                                        You do not currently
                                        have a résumé uploaded.
  
                                        {" "}
  
                                        You may still submit,
                                        but employers will not
                                        have a résumé to review.
  
                                      </div>
  
                                    )
                                  }
  
                                </div>
  
  
                                {/* -------------------------------
                                    Cover Letter
                                -------------------------------- */}
  
                                <div className="mb-3">
  
                                  <label className="form-label">
  
                                    Cover Letter
  
                                  </label>
  
  
                                  <textarea
                                    rows="6"
                                    maxLength="5000"
                                    className="form-control"
                                    value={
                                      coverLetter
                                    }
                                    onChange={(
                                      event
                                    ) =>
                                      setCoverLetter(
                                        event
                                          .target
                                          .value
                                      )
                                    }
                                    placeholder="Explain why you are interested in this opportunity and how your experience matches the role..."
                                  />
  
  
                                  <div className="form-text d-flex justify-content-between">
  
                                    <span>
                                      Optional
                                    </span>
  
  
                                    <span>
  
                                      {
                                        coverLetter.length
                                      }
  
                                      /5000
  
                                    </span>
  
                                  </div>
  
                                </div>
  
  
                                {/* -------------------------------
                                    Confirmation Notice
                                -------------------------------- */}
  
                                <div className="alert alert-info small">
  
                                  By submitting, a historical
                                  snapshot of your profile and
                                  current skills will be saved
                                  with this application.
  
                                  Future profile changes will
                                  not rewrite the submitted
                                  application snapshot.
  
                                </div>
  
  
                                {/* -------------------------------
                                    Submit / Cancel
                                -------------------------------- */}
  
                                <div className="d-flex gap-2">
  
                                  <button
                                    className="btn btn-success"
                                    type="button"
                                    disabled={
                                      submitting
                                    }
                                    onClick={() =>
                                      apply(
                                        item.id
                                      )
                                    }
                                  >
  
                                    {
                                      submitting
                                        ? "Submitting..."
                                        : "Confirm Application"
                                    }
  
                                  </button>
  
  
                                  <button
                                    className="btn btn-outline-secondary"
                                    type="button"
                                    disabled={
                                      submitting
                                    }
                                    onClick={() =>
                                      toggleApplyForm(
                                        item.id
                                      )
                                    }
                                  >
  
                                    Cancel
  
                                  </button>
  
                                </div>
  
                              </div>
  
                            )
                          }
  
                        </div>
  
                      )
                    }
  
  
                    {/* -----------------------------------------------
                        External Application Link
                    ------------------------------------------------ */}
  
                    {
                      item.application_url && (
  
                        <div className="mt-3">
  
                          <a
                            href={
                              item.application_url
                            }
                            target="_blank"
                            rel="noreferrer"
                            className="btn btn-outline-secondary btn-sm"
                          >
  
                            External Application Link
  
                          </a>
  
                        </div>
  
                      )
                    }
  
                  </div>
  
                </div>
  
              );
  
            }
          )
        }
  
      </>
    );
  }