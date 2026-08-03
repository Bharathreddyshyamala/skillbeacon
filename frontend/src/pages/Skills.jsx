import { useEffect, useState } from "react";

import {
  apiRequest,
  jsonBody,
} from "../api";


export default function Skills() {

  // ---------------------------------------
  // Skill catalog from backend
  // ---------------------------------------

  const [catalog, setCatalog] = useState([]);

  // Skills added by logged-in user
  const [mySkills, setMySkills] = useState([]);


  // ---------------------------------------
  // Add Skill form
  // ---------------------------------------

  const [selectedSkill, setSelectedSkill] =
    useState("");

  const [level, setLevel] =
    useState("beginner");


  // ---------------------------------------
  // Messages
  // ---------------------------------------

  const [error, setError] =
    useState("");

  const [message, setMessage] =
    useState("");


  // ---------------------------------------
  // Evidence form
  // ---------------------------------------

  // Stores the UserSkill ID for which
  // the evidence form is currently open
  const [evidenceSkillId, setEvidenceSkillId] =
    useState("");


  const [evidence, setEvidence] =
    useState({
      evidence_type: "github_project",
      title: "",
      description: "",
      url: "",
    });


  // ---------------------------------------
  // Load catalog + user's skills
  // ---------------------------------------

  async function loadData() {

    setError("");

    try {

      const [
        catalogResponse,
        mySkillsResponse,
      ] = await Promise.all([
        apiRequest("/skills"),
        apiRequest("/skills/me"),
      ]);


      setCatalog(
        Array.isArray(catalogResponse)
          ? catalogResponse
          : []
      );


      setMySkills(
        Array.isArray(mySkillsResponse)
          ? mySkillsResponse
          : []
      );

    } catch (requestError) {

      setError(
        requestError.message ||
        "Unable to load skills."
      );

    }
  }


  useEffect(() => {
    loadData();
  }, []);


  // ---------------------------------------
  // Add Skill
  // ---------------------------------------

  async function addSkill(event) {

    event.preventDefault();

    setError("");
    setMessage("");


    if (!selectedSkill) {

      setError("Select a skill.");

      return;
    }


    try {

      await apiRequest(
        "/skills/me",
        {
          method: "POST",

          body: jsonBody({
            skill_id: selectedSkill,
            level,
          }),
        },
      );


      setMessage(
        "Skill added successfully."
      );


      // Reset form
      setSelectedSkill("");
      setLevel("beginner");


      // Reload skills
      await loadData();

    } catch (requestError) {

      setError(
        requestError.message ||
        "Unable to add skill."
      );

    }
  }


  // ---------------------------------------
  // Delete Skill
  // ---------------------------------------

  async function deleteSkill(userSkillId) {

    const confirmed = window.confirm(
      "Are you sure you want to remove this skill?"
    );


    if (!confirmed) {
      return;
    }


    setError("");
    setMessage("");


    try {

      await apiRequest(
        `/skills/me/${userSkillId}`,
        {
          method: "DELETE",
        },
      );


      setMessage(
        "Skill removed successfully."
      );


      await loadData();

    } catch (requestError) {

      setError(
        requestError.message ||
        "Unable to remove skill."
      );

    }
  }


  // ---------------------------------------
  // Open Evidence form
  // ---------------------------------------

  function openEvidenceForm(userSkillId) {

    setError("");
    setMessage("");


    // If same form is already open,
    // clicking button again closes it
    if (evidenceSkillId === userSkillId) {

      setEvidenceSkillId("");

      return;
    }


    setEvidenceSkillId(userSkillId);


    // Reset form
    setEvidence({
      evidence_type: "github_project",
      title: "",
      description: "",
      url: "",
    });
  }


  // ---------------------------------------
  // Cancel Evidence form
  // ---------------------------------------

  function cancelEvidenceForm() {

    setEvidenceSkillId("");


    setEvidence({
      evidence_type: "github_project",
      title: "",
      description: "",
      url: "",
    });
  }


  // ---------------------------------------
  // Add Evidence
  // ---------------------------------------

  async function addEvidence(event) {

    event.preventDefault();

    setError("");
    setMessage("");


    if (!evidenceSkillId) {

      setError(
        "Unable to determine which skill this evidence belongs to."
      );

      return;
    }


    if (!evidence.title.trim()) {

      setError(
        "Evidence title is required."
      );

      return;
    }


    try {

      await apiRequest(
        `/skills/me/${evidenceSkillId}/evidence`,
        {
          method: "POST",

          body: jsonBody({

            evidence_type:
              evidence.evidence_type,

            title:
              evidence.title.trim(),

            description:
              evidence.description.trim()
                || null,

            url:
              evidence.url.trim()
                || null,

            score: null,

          }),
        },
      );


      setMessage(
        "Evidence added successfully. It is waiting for verification."
      );


      // Reset evidence form
      setEvidenceSkillId("");


      setEvidence({
        evidence_type: "github_project",
        title: "",
        description: "",
        url: "",
      });


      // Reload skill data
      await loadData();

    } catch (requestError) {

      setError(
        requestError.message ||
        "Unable to add evidence."
      );

    }
  }


  // ---------------------------------------
  // Evidence Status Badge
  // ---------------------------------------

  function getEvidenceBadge(status) {

    if (status === "approved") {

      return (
        <span className="badge text-bg-success">
          Approved
        </span>
      );
    }


    if (status === "rejected") {

      return (
        <span className="badge text-bg-danger">
          Rejected
        </span>
      );
    }


    return (
      <span className="badge text-bg-warning">
        Pending
      </span>
    );
  }


  // ---------------------------------------
  // UI
  // ---------------------------------------

  return (
    <>

      {/* PAGE TITLE */}

      <div className="mb-4">

        <p className="text-info fw-semibold text-uppercase">
          Skill Passport
        </p>


        <h1 className="display-6 fw-bold">
          My Skills
        </h1>


        <p className="text-secondary">
          Add skills and prove them using
          projects, certificates, assessments,
          work experience, and other evidence.
        </p>

      </div>


      {/* ERROR MESSAGE */}

      {error && (

        <div
          className="alert alert-danger"
          role="alert"
        >
          {error}
        </div>

      )}


      {/* SUCCESS MESSAGE */}

      {message && (

        <div
          className="alert alert-success"
          role="alert"
        >
          {message}
        </div>

      )}


      <div className="row g-4">


        {/* -------------------------------- */}
        {/* LEFT SIDE - ADD SKILL */}
        {/* -------------------------------- */}

        <div className="col-lg-4">

          <div className="glass-card">

            <h2 className="h5 mb-3">
              Add a Skill
            </h2>


            <form onSubmit={addSkill}>


              {/* Skill */}

              <div className="mb-3">

                <label className="form-label">

                  Skill

                </label>


                <select
                  className="form-select"
                  value={selectedSkill}
                  onChange={(event) =>
                    setSelectedSkill(
                      event.target.value
                    )
                  }
                >

                  <option value="">

                    Select skill

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


              {/* Level */}

              <div className="mb-3">

                <label className="form-label">

                  Level

                </label>


                <select
                  className="form-select"
                  value={level}
                  onChange={(event) =>
                    setLevel(
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


              <button
                className="btn btn-info w-100"
                type="submit"
              >

                Add Skill

              </button>


            </form>

          </div>

        </div>


        {/* -------------------------------- */}
        {/* RIGHT SIDE - SKILL PASSPORT */}
        {/* -------------------------------- */}

        <div className="col-lg-8">


          {/* No Skills */}

          {mySkills.length === 0 && (

            <div className="glass-card">

              <p className="text-secondary mb-0">

                You haven't added any skills yet.

              </p>

            </div>

          )}


          {/* Skill Cards */}

          {mySkills.map(
            (userSkill) => {

              // Prevent errors if evidence is null
              const skillEvidence =
                Array.isArray(userSkill.evidence)
                  ? userSkill.evidence
                  : [];


              return (

                <div
                  key={userSkill.id}
                  className="glass-card mb-4"
                >


                  {/* Skill Header */}

                  <div className="d-flex justify-content-between align-items-start gap-3">


                    <div>

                      <h2 className="h4 mb-1">

                        {userSkill.skill?.name}

                      </h2>


                      <p className="text-secondary text-capitalize mb-0">

                        {userSkill.level}

                      </p>

                    </div>


                    <button
                      className="btn btn-outline-danger btn-sm"
                      type="button"
                      onClick={() =>
                        deleteSkill(
                          userSkill.id
                        )
                      }
                    >

                      Remove

                    </button>


                  </div>


                  {/* -------------------------------- */}
                  {/* Confidence */}
                  {/* -------------------------------- */}

                  <div className="mt-4">


                    <div className="d-flex justify-content-between mb-2">


                      <span>

                        Confidence

                      </span>


                      <strong className="text-info">

                        {
                          userSkill
                            .confidence_score
                        }
                        %

                      </strong>


                    </div>


                    <div
                      className="progress"
                      style={{
                        height: "10px",
                      }}
                    >

                      <div
                        className="progress-bar bg-info"
                        role="progressbar"
                        style={{
                          width:
                            `${
                              userSkill
                                .confidence_score
                            }%`,
                        }}
                        aria-valuenow={
                          userSkill
                            .confidence_score
                        }
                        aria-valuemin="0"
                        aria-valuemax="100"
                      />

                    </div>


                  </div>


                  {/* -------------------------------- */}
                  {/* Evidence Header */}
                  {/* -------------------------------- */}

                  <div className="mt-4">


                    <div className="d-flex justify-content-between align-items-center mb-3">


                      <h3 className="h6 mb-0">

                        Evidence

                      </h3>


                      <button
                        type="button"
                        className="btn btn-outline-info btn-sm"
                        onClick={() =>
                          openEvidenceForm(
                            userSkill.id
                          )
                        }
                      >

                        {
                          evidenceSkillId
                            === userSkill.id
                            ? "Cancel"
                            : "+ Add Evidence"
                        }

                      </button>


                    </div>


                    {/* -------------------------------- */}
                    {/* Existing Evidence */}
                    {/* -------------------------------- */}

                    {skillEvidence.length === 0 ? (

                      <p className="text-secondary small">

                        No evidence added.

                      </p>

                    ) : (

                      skillEvidence.map(
                        (item) => (

                          <div
                            key={item.id}
                            className="border rounded p-3 mb-3"
                          >


                            <div className="d-flex justify-content-between align-items-start gap-3">


                              <div>

                                <strong>

                                  {item.title}

                                </strong>


                                <div className="small text-secondary text-capitalize mt-1">

                                  {
                                    item
                                      .evidence_type
                                      ?.replaceAll(
                                        "_",
                                        " "
                                      )
                                  }

                                </div>

                              </div>


                              {
                                getEvidenceBadge(
                                  item.status
                                )
                              }


                            </div>


                            {/* Description */}

                            {item.description && (

                              <p className="small text-secondary mt-3 mb-2">

                                {
                                  item.description
                                }

                              </p>

                            )}


                            {/* Evidence URL */}

                            {item.url && (

                              <a
                                href={item.url}
                                target="_blank"
                                rel="noreferrer"
                                className="small text-info"
                              >

                                View Evidence

                              </a>

                            )}


                            {/* Verification count */}

                            {
                              Array.isArray(
                                item.verifications
                              ) &&
                              item.verifications.length
                                > 0 && (

                                <div className="small text-secondary mt-2">

                                  {
                                    item
                                      .verifications
                                      .length
                                  }
                                  {" "}
                                  verification
                                  {
                                    item
                                      .verifications
                                      .length !== 1
                                      ? "s"
                                      : ""
                                  }

                                </div>

                              )
                            }


                          </div>

                        )
                      )

                    )}


                    {/* -------------------------------- */}
                    {/* Add Evidence Form */}
                    {/* -------------------------------- */}

                    {
                      evidenceSkillId
                        === userSkill.id && (

                        <form
                          className="border rounded p-3 mt-3"
                          onSubmit={addEvidence}
                        >


                          <h4 className="h6 mb-3">

                            Add Evidence

                          </h4>


                          {/* Evidence Type */}

                          <div className="mb-3">

                            <label className="form-label">

                              Evidence Type

                            </label>


                            <select
                              className="form-select"
                              value={
                                evidence
                                  .evidence_type
                              }
                              onChange={(
                                event
                              ) =>
                                setEvidence({
                                  ...evidence,

                                  evidence_type:
                                    event
                                      .target
                                      .value,
                                })
                              }
                            >


                              <option value="github_project">

                                GitHub Project

                              </option>


                              <option value="certificate">

                                Certificate

                              </option>


                              <option value="assessment">

                                Assessment

                              </option>


                              <option value="employer_challenge">

                                Employer Challenge

                              </option>


                              <option value="work_experience">

                                Work Experience

                              </option>


                              <option value="mentor_review">

                                Mentor Review

                              </option>


                              <option value="other">

                                Other

                              </option>


                            </select>

                          </div>


                          {/* Title */}

                          <div className="mb-3">

                            <label className="form-label">

                              Title

                            </label>


                            <input
                              type="text"
                              className="form-control"
                              value={
                                evidence.title
                              }
                              onChange={(
                                event
                              ) =>
                                setEvidence({
                                  ...evidence,

                                  title:
                                    event
                                      .target
                                      .value,
                                })
                              }
                              placeholder="Example: MongoDB REST API Project"
                              required
                            />

                          </div>


                          {/* Description */}

                          <div className="mb-3">

                            <label className="form-label">

                              Description

                            </label>


                            <textarea
                              className="form-control"
                              rows="4"
                              value={
                                evidence
                                  .description
                              }
                              onChange={(
                                event
                              ) =>
                                setEvidence({
                                  ...evidence,

                                  description:
                                    event
                                      .target
                                      .value,
                                })
                              }
                              placeholder="Explain how this evidence proves your skill..."
                            />

                          </div>


                          {/* URL */}

                          <div className="mb-3">

                            <label className="form-label">

                              Evidence URL

                            </label>


                            <input
                              type="url"
                              className="form-control"
                              value={
                                evidence.url
                              }
                              onChange={(
                                event
                              ) =>
                                setEvidence({
                                  ...evidence,

                                  url:
                                    event
                                      .target
                                      .value,
                                })
                              }
                              placeholder="https://github.com/..."
                            />


                            <div className="form-text">

                              Add a GitHub repository,
                              certificate link, project
                              link, or other supporting
                              evidence.

                            </div>


                          </div>


                          {/* Buttons */}

                          <div className="d-flex gap-2">


                            <button
                              type="submit"
                              className="btn btn-info"
                            >

                              Save Evidence

                            </button>


                            <button
                              type="button"
                              className="btn btn-outline-secondary"
                              onClick={
                                cancelEvidenceForm
                              }
                            >

                              Cancel

                            </button>


                          </div>


                        </form>

                      )
                    }


                  </div>


                </div>

              );

            }
          )}


        </div>


      </div>

    </>
  );
}