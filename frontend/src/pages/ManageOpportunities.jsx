import {
    useEffect,
    useState,
  } from "react";
  
  import {
    apiRequest,
    jsonBody,
  } from "../api";
  
  
  const EMPTY_FORM = {
  
    title: "",
  
    company_name: "",
  
    description: "",
  
    location: "",
  
    work_mode: "hybrid",
  
    opportunity_type: "internship",
  
    employment_type: "full_time",
  
    salary_min: "",
  
    salary_max: "",
  
    currency: "USD",
  
    application_url: "",
  
    deadline: "",
  
    status: "draft",
  };
  
  
  export default function ManageOpportunities() {
  
    const [catalog, setCatalog] =
      useState([]);
  
    const [items, setItems] =
      useState([]);
  
    const [form, setForm] =
      useState(
        EMPTY_FORM
      );
  
    const [
      requirements,
      setRequirements,
    ] = useState([]);
  
    const [skillId, setSkillId] =
      useState("");
  
    const [skillLevel, setSkillLevel] =
      useState("beginner");
  
    const [error, setError] =
      useState("");
  
    const [message, setMessage] =
      useState("");
  
  
    async function loadData() {
  
      setError("");
  
  
      try {
  
        const [
          skillsResponse,
          opportunitiesResponse,
        ] = await Promise.all([
  
          apiRequest(
            "/skills"
          ),
  
          apiRequest(
            "/opportunities/me"
          ),
  
        ]);
  
  
        setCatalog(
          Array.isArray(
            skillsResponse
          )
            ? skillsResponse
            : []
        );
  
  
        setItems(
          Array.isArray(
            opportunitiesResponse
          )
            ? opportunitiesResponse
            : []
        );
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to load opportunities."
        );
  
      }
    }
  
  
    useEffect(() => {
  
      loadData();
  
    }, []);
  
  
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
  
  
    function addRequirement() {
  
      setError("");
  
  
      if (!skillId) {
  
        setError(
          "Select a skill."
        );
  
        return;
      }
  
  
      const selected =
        catalog.find(
          (skill) =>
            skill.id === skillId
        );
  
  
      if (!selected) {
        return;
      }
  
  
      const alreadyAdded =
        requirements.some(
          (requirement) =>
            requirement.skill_id
            === skillId
        );
  
  
      if (alreadyAdded) {
  
        setError(
          "That skill is already added."
        );
  
        return;
      }
  
  
      setRequirements([
        ...requirements,
  
        {
          skill_id:
            selected.id,
  
          skill_name:
            selected.name,
  
          minimum_level:
            skillLevel,
  
          required:
            true,
        },
      ]);
  
  
      setSkillId("");
  
      setSkillLevel(
        "beginner"
      );
    }
  
  
    function removeRequirement(
      skillIdToRemove,
    ) {
  
      setRequirements(
        requirements.filter(
          (requirement) =>
            requirement.skill_id
            !== skillIdToRemove
        )
      );
    }
  
  
    async function createOpportunity(
      event,
    ) {
  
      event.preventDefault();
  
      setError("");
      setMessage("");
  
  
      try {
  
        await apiRequest(
          "/opportunities",
          {
            method: "POST",
  
            body: jsonBody({
  
              ...form,
  
              salary_min:
                form.salary_min
                  ? Number(
                      form.salary_min
                    )
                  : null,
  
              salary_max:
                form.salary_max
                  ? Number(
                      form.salary_max
                    )
                  : null,
  
              location:
                form.location ||
                null,
  
              application_url:
                form.application_url ||
                null,
  
              deadline:
                form.deadline ||
                null,
  
              skills:
                requirements.map(
                  (requirement) => ({
  
                    skill_id:
                      requirement
                        .skill_id,
  
                    minimum_level:
                      requirement
                        .minimum_level,
  
                    required:
                      requirement
                        .required,
  
                  })
                ),
            }),
          }
        );
  
  
        setMessage(
          "Opportunity created successfully."
        );
  
  
        setForm(
          EMPTY_FORM
        );
  
  
        setRequirements(
          []
        );
  
  
        await loadData();
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to create opportunity."
        );
  
      }
    }
  
  
    async function changeStatus(
      opportunityId,
      newStatus,
    ) {
  
      setError("");
      setMessage("");
  
  
      try {
  
        await apiRequest(
          `/opportunities/${opportunityId}/status`,
          {
            method: "PATCH",
  
            body: jsonBody({
              status:
                newStatus,
            }),
          }
        );
  
  
        setMessage(
          `Opportunity changed to ${newStatus}.`
        );
  
  
        await loadData();
  
  
      } catch (requestError) {
  
        setError(
          requestError.message ||
          "Unable to update opportunity."
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
            Manage Opportunities
          </h1>
  
          <p className="text-secondary">
            Create opportunities and define
            the skills candidates should have.
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
  
  
        <div className="glass-card mb-5">
  
          <h2 className="h4 mb-4">
            Create Opportunity
          </h2>
  
  
          <form
            onSubmit={
              createOpportunity
            }
          >
  
            <div className="row g-3">
  
  
              <div className="col-md-6">
  
                <label className="form-label">
                  Title
                </label>
  
                <input
                  className="form-control"
                  value={
                    form.title
                  }
                  onChange={(event) =>
                    updateField(
                      "title",
                      event.target.value
                    )
                  }
                  required
                />
  
              </div>
  
  
              <div className="col-md-6">
  
                <label className="form-label">
                  Company Name
                </label>
  
                <input
                  className="form-control"
                  value={
                    form.company_name
                  }
                  onChange={(event) =>
                    updateField(
                      "company_name",
                      event.target.value
                    )
                  }
                  required
                />
  
              </div>
  
  
              <div className="col-12">
  
                <label className="form-label">
                  Description
                </label>
  
                <textarea
                  className="form-control"
                  rows="5"
                  value={
                    form.description
                  }
                  onChange={(event) =>
                    updateField(
                      "description",
                      event.target.value
                    )
                  }
                  required
                />
  
              </div>
  
  
              <div className="col-md-4">
  
                <label className="form-label">
                  Opportunity Type
                </label>
  
                <select
                  className="form-select"
                  value={
                    form.opportunity_type
                  }
                  onChange={(event) =>
                    updateField(
                      "opportunity_type",
                      event.target.value
                    )
                  }
                >
  
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
  
  
              <div className="col-md-4">
  
                <label className="form-label">
                  Work Mode
                </label>
  
                <select
                  className="form-select"
                  value={
                    form.work_mode
                  }
                  onChange={(event) =>
                    updateField(
                      "work_mode",
                      event.target.value
                    )
                  }
                >
  
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
  
  
              <div className="col-md-4">
  
                <label className="form-label">
                  Employment Type
                </label>
  
                <select
                  className="form-select"
                  value={
                    form.employment_type
                  }
                  onChange={(event) =>
                    updateField(
                      "employment_type",
                      event.target.value
                    )
                  }
                >
  
                  <option value="full_time">
                    Full Time
                  </option>
  
                  <option value="part_time">
                    Part Time
                  </option>
  
                  <option value="contract">
                    Contract
                  </option>
  
                  <option value="temporary">
                    Temporary
                  </option>
  
                </select>
  
              </div>
  
  
              <div className="col-md-6">
  
                <label className="form-label">
                  Location
                </label>
  
                <input
                  className="form-control"
                  value={
                    form.location
                  }
                  onChange={(event) =>
                    updateField(
                      "location",
                      event.target.value
                    )
                  }
                />
  
              </div>
  
  
              <div className="col-md-6">
  
                <label className="form-label">
                  Deadline
                </label>
  
                <input
                  type="date"
                  className="form-control"
                  value={
                    form.deadline
                  }
                  onChange={(event) =>
                    updateField(
                      "deadline",
                      event.target.value
                    )
                  }
                />
  
              </div>
  
  
              <div className="col-md-6">
  
                <label className="form-label">
                  Minimum Salary
                </label>
  
                <input
                  type="number"
                  min="0"
                  className="form-control"
                  value={
                    form.salary_min
                  }
                  onChange={(event) =>
                    updateField(
                      "salary_min",
                      event.target.value
                    )
                  }
                />
  
              </div>
  
  
              <div className="col-md-6">
  
                <label className="form-label">
                  Maximum Salary
                </label>
  
                <input
                  type="number"
                  min="0"
                  className="form-control"
                  value={
                    form.salary_max
                  }
                  onChange={(event) =>
                    updateField(
                      "salary_max",
                      event.target.value
                    )
                  }
                />
  
              </div>
  
  
              <div className="col-12">
  
                <label className="form-label">
                  External Application URL
                </label>
  
                <input
                  type="url"
                  className="form-control"
                  value={
                    form.application_url
                  }
                  onChange={(event) =>
                    updateField(
                      "application_url",
                      event.target.value
                    )
                  }
                />
                
              
  
              </div>
  
            </div>
  
  
            <hr className="my-4" />
  
  
            <h3 className="h5 mb-3">
              Required Skills
            </h3>
  
  
            <div className="row g-3">
  
              <div className="col-md-6">
  
                <select
                  className="form-select"
                  value={
                    skillId
                  }
                  onChange={(event) =>
                    setSkillId(
                      event.target.value
                    )
                  }
                >
  
                  <option value="">
                    Select Skill
                  </option>
  
                  {catalog.map(
                    (skill) => (
  
                      <option
                        key={skill.id}
                        value={skill.id}
                      >
                        {skill.name}
                      </option>
  
                    )
                  )}
  
                </select>
  
              </div>
  
  
              <div className="col-md-4">
  
                <select
                  className="form-select"
                  value={
                    skillLevel
                  }
                  onChange={(event) =>
                    setSkillLevel(
                      event.target.value
                    )
                  }
                >
  
                  <option value="beginner">
                    Beginner
                  </option>
  
                  <option value="intermediate">
                    Intermediate
                  </option>
  
                  <option value="advanced">
                    Advanced
                  </option>
  
                  <option value="expert">
                    Expert
                  </option>
  
                </select>
  
              </div>
  
  
              <div className="col-md-2">
  
                <button
                  type="button"
                  className="btn btn-outline-info w-100"
                  onClick={
                    addRequirement
                  }
                >
                  Add
                </button>
  
              </div>
  
            </div>
  
  
            <div className="mt-3 d-flex flex-wrap gap-2">
  
              {requirements.map(
                (requirement) => (
  
                  <button
                    type="button"
                    key={
                      requirement.skill_id
                    }
                    className="btn btn-outline-secondary btn-sm"
                    onClick={() =>
                      removeRequirement(
                        requirement.skill_id
                      )
                    }
                  >
  
                    {
                      requirement.skill_name
                    }
  
                    {" · "}
  
                    {
                      requirement.minimum_level
                    }
  
                    {" ×"}
  
                  </button>
  
                )
              )}
  
            </div>
  
  
            <div className="mt-4">
  
              <label className="form-label">
                Status
              </label>
  
              <select
                className="form-select"
                style={{
                  maxWidth: "250px",
                }}
                value={
                  form.status
                }
                onChange={(event) =>
                  updateField(
                    "status",
                    event.target.value
                  )
                }
              >
  
                <option value="draft">
                  Save as Draft
                </option>
  
                <option value="open">
                  Publish Now
                </option>
  
              </select>
  
            </div>
  
  
            <button
              type="submit"
              className="btn btn-info mt-4"
            >
              Create Opportunity
            </button>
  
          </form>
  
        </div>
  
  
        <h2 className="h4 mb-3">
          My Opportunities
        </h2>
  
  
        {
          items.length === 0 && (
  
            <div className="glass-card">
  
              <p className="text-secondary mb-0">
                You have not created any
                opportunities yet.
              </p>
  
            </div>
  
          )
        }
  
  
        {items.map(
          (item) => (
  
            <div
              key={item.id}
              className="glass-card mb-3"
            >
  
              <div className="d-flex justify-content-between align-items-start gap-3">
  
                <div>
  
                  <h3 className="h5">
                    {item.title}
                  </h3>
  
                  <p className="text-secondary mb-2">
                    {item.company_name}
                  </p>
  
                  <span className="badge text-bg-secondary text-capitalize">
                    {item.status}
                  </span>
  
                </div>
  
  
                <div className="d-flex gap-2">
  
  
                  {
                    item.status !== "open" && (
  
                      <button
                        type="button"
                        className="btn btn-success btn-sm"
                        onClick={() =>
                          changeStatus(
                            item.id,
                            "open"
                          )
                        }
                      >
                        Publish
                      </button>
  
                    )
                  }
  
  
                  {
                    item.status === "open" && (
  
                      <button
                        type="button"
                        className="btn btn-outline-warning btn-sm"
                        onClick={() =>
                          changeStatus(
                            item.id,
                            "closed"
                          )
                        }
                      >
                        Close
                      </button>
  
                    )
                  }
  
  
                </div>
  
              </div>
  
            </div>
  
          )
        )}
  
      </>
    );
  }