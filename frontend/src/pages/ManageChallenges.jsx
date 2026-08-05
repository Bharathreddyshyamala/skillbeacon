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






  const EMPTY_FORM = {
    title: "",
    company_name: "",
    description: "",
    instructions: "",
    deliverables: "",
    challenge_type: "coding",
    difficulty: "intermediate",
    deadline: "",
    status: "draft",
  };






  export default function ManageChallenges() {

    const navigate =
      useNavigate();






    const [
      catalog,
      setCatalog,
    ] = useState([]);


    const [
      challenges,
      setChallenges,
    ] = useState([]);






    const [
      form,
      setForm,
    ] = useState({
      ...EMPTY_FORM,
    });






    const [
      requirements,
      setRequirements,
    ] = useState([]);


    const [
      skillId,
      setSkillId,
    ] = useState("");


    const [
      skillLevel,
      setSkillLevel,
    ] = useState(
      "beginner"
    );






    const [
      loading,
      setLoading,
    ] = useState(true);


    const [
      submitting,
      setSubmitting,
    ] = useState(false);


    const [
      statusUpdatingId,
      setStatusUpdatingId,
    ] = useState("");


    const [
      error,
      setError,
    ] = useState("");


    const [
      message,
      setMessage,
    ] = useState("");






    async function loadData() {

      setLoading(true);

      setError("");


      try {

        const [
          skillsResponse,
          challengesResponse,
        ] = await Promise.all([

          apiRequest(
            "/skills"
          ),

          apiRequest(
            "/challenges/me"
          ),

        ]);






        setCatalog(
          Array.isArray(
            skillsResponse
          )
            ? skillsResponse
            : []
        );

















        if (
          Array.isArray(
            challengesResponse
          )
        ) {

          setChallenges(
            challengesResponse
          );

        } else {

          setChallenges(
            Array.isArray(
              challengesResponse?.items
            )
              ? challengesResponse.items
              : []
          );

        }


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






    function updateField(
      field,
      value,
    ) {

      setForm(
        (
          currentForm
        ) => ({
          ...currentForm,

          [field]:
            value,
        })
      );
    }






    function addRequirement() {

      setError("");
      setMessage("");


      if (!skillId) {

        setError(
          "Select a skill first."
        );

        return;
      }


      const selectedSkill =
        catalog.find(
          (skill) =>
            skill.id === skillId
        );


      if (!selectedSkill) {

        setError(
          "Selected skill was not found."
        );

        return;
      }


      const alreadyExists =
        requirements.some(
          (requirement) =>
            requirement.skill_id
            === skillId
        );


      if (alreadyExists) {

        setError(
          "That skill is already added to this challenge."
        );

        return;
      }


      setRequirements(
        (
          currentRequirements
        ) => [
          ...currentRequirements,

          {
            skill_id:
              selectedSkill.id,

            skill_name:
              selectedSkill.name,

            minimum_level:
              skillLevel,

            required:
              true,
          },
        ]
      );


      setSkillId("");

      setSkillLevel(
        "beginner"
      );
    }






    function removeRequirement(
      skillIdToRemove,
    ) {

      setRequirements(
        (
          currentRequirements
        ) =>
          currentRequirements.filter(
            (requirement) =>
              requirement.skill_id
              !== skillIdToRemove
          )
      );
    }






    function validateForm() {

      if (
        !form.title.trim()
      ) {

        setError(
          "Challenge title is required."
        );

        return false;
      }


      if (
        !form.company_name.trim()
      ) {

        setError(
          "Company name is required."
        );

        return false;
      }


      if (
        form.description.trim().length
        < 10
      ) {

        setError(
          "Description must contain at least 10 characters."
        );

        return false;
      }


      if (
        form.instructions.trim().length
        < 10
      ) {

        setError(
          "Instructions must contain at least 10 characters."
        );

        return false;
      }


      if (
        form.deadline
      ) {

        const selectedDate =
          new Date(
            `${form.deadline}T00:00:00`
          );


        const today =
          new Date();


        today.setHours(
          0,
          0,
          0,
          0
        );


        if (
          selectedDate
          < today
        ) {

          setError(
            "Challenge deadline cannot be in the past."
          );

          return false;
        }

      }


      return true;
    }






    async function createChallenge(
      event,
    ) {

      event.preventDefault();

      setError("");
      setMessage("");


      if (
        !validateForm()
      ) {

        return;
      }


      setSubmitting(true);


      try {

        await apiRequest(
          "/challenges",
          {
            method: "POST",

            body: jsonBody({

              title:
                form.title.trim(),

              company_name:
                form.company_name.trim(),

              description:
                form.description.trim(),

              instructions:
                form.instructions.trim(),

              deliverables:
                form.deliverables.trim()
                  || null,

              challenge_type:
                form.challenge_type,

              difficulty:
                form.difficulty,

              deadline:
                form.deadline
                  || null,

              status:
                form.status,

              skills:
                requirements.map(
                  (
                    requirement
                  ) => ({

                    skill_id:
                      requirement.skill_id,

                    minimum_level:
                      requirement.minimum_level,

                    required:
                      requirement.required,

                  })
                ),

            }),
          }
        );


        setMessage(
          form.status === "open"
            ? "Challenge created and published successfully."
            : "Challenge saved as draft successfully."
        );




        setForm({
          ...EMPTY_FORM,
        });




        setRequirements([]);

        setSkillId("");

        setSkillLevel(
          "beginner"
        );


        await loadData();


      } catch (requestError) {

        setError(
          requestError.message ||
          "Unable to create challenge."
        );

      } finally {

        setSubmitting(false);

      }
    }






    async function changeStatus(
      challengeId,
      newStatus,
    ) {

      setError("");
      setMessage("");


      let confirmationMessage;


      if (
        newStatus === "open"
      ) {

        confirmationMessage =
          "Publish this challenge? Students will be able to view and submit solutions.";

      } else {

        confirmationMessage =
          "Close this challenge? Students will no longer be able to submit solutions.";

      }


      const confirmed =
        window.confirm(
          confirmationMessage
        );


      if (!confirmed) {

        return;

      }


      setStatusUpdatingId(
        challengeId
      );


      try {

        await apiRequest(
          `/challenges/${challengeId}/status`,
          {
            method: "PATCH",

            body: jsonBody({
              status:
                newStatus,
            }),
          }
        );


        setMessage(
          newStatus === "open"
            ? "Challenge is now open."
            : "Challenge has been closed."
        );


        await loadData();


      } catch (requestError) {

        setError(
          requestError.message ||
          "Unable to update challenge status."
        );

      } finally {

        setStatusUpdatingId("");

      }
    }






    function viewSubmissions(
      challengeId,
    ) {

      navigate(
        `/app/challenges/${challengeId}/submissions`
      );
    }






    function statusBadgeClass(
      status,
    ) {

      switch (status) {

        case "open":

          return "text-bg-success";


        case "closed":

          return "text-bg-danger";


        default:

          return "text-bg-secondary";

      }
    }


    function difficultyBadgeClass(
      difficulty,
    ) {

      switch (difficulty) {

        case "beginner":

          return "text-bg-success";


        case "advanced":

          return "text-bg-danger";


        default:

          return "text-bg-warning";

      }
    }






    return (
      <>





        <div className="mb-4">

          <p className="text-info fw-semibold text-uppercase">
            Employer
          </p>


          <h1 className="display-6 fw-bold">
            Manage Challenges
          </h1>


          <p className="text-secondary">
            Create practical challenges,
            define required skills, and
            review student submissions.
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
            Create Challenge
          </h2>


          <form
            onSubmit={
              createChallenge
            }
          >

            <div className="row g-3">






              <div className="col-md-6">

                <label className="form-label">
                  Challenge Title
                </label>


                <input
                  type="text"
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
                  placeholder="Build a FastAPI REST API"
                  maxLength="200"
                  required
                />

              </div>






              <div className="col-md-6">

                <label className="form-label">
                  Company Name
                </label>


                <input
                  type="text"
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
                  placeholder="SkillBeacon Labs"
                  maxLength="200"
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
                  maxLength="10000"
                  value={
                    form.description
                  }
                  onChange={(event) =>
                    updateField(
                      "description",
                      event.target.value
                    )
                  }
                  placeholder="Describe the problem the student should solve..."
                  required
                />


                <div className="form-text text-end">

                  {
                    form.description.length
                  }

                  /10000

                </div>

              </div>






              <div className="col-12">

                <label className="form-label">
                  Instructions
                </label>


                <textarea
                  className="form-control"
                  rows="6"
                  maxLength="15000"
                  value={
                    form.instructions
                  }
                  onChange={(event) =>
                    updateField(
                      "instructions",
                      event.target.value
                    )
                  }
                  placeholder="Explain the technical requirements, rules, and expected implementation..."
                  required
                />


                <div className="form-text text-end">

                  {
                    form.instructions.length
                  }

                  /15000

                </div>

              </div>






              <div className="col-12">

                <label className="form-label">
                  Deliverables
                </label>


                <textarea
                  className="form-control"
                  rows="4"
                  maxLength="10000"
                  value={
                    form.deliverables
                  }
                  onChange={(event) =>
                    updateField(
                      "deliverables",
                      event.target.value
                    )
                  }
                  placeholder="Example: GitHub repository, README, live demo..."
                />


                <div className="form-text">
                  Optional
                </div>

              </div>






              <div className="col-md-4">

                <label className="form-label">
                  Challenge Type
                </label>


                <select
                  className="form-select"
                  value={
                    form.challenge_type
                  }
                  onChange={(event) =>
                    updateField(
                      "challenge_type",
                      event.target.value
                    )
                  }
                >

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






              <div className="col-md-4">

                <label className="form-label">
                  Difficulty
                </label>


                <select
                  className="form-select"
                  value={
                    form.difficulty
                  }
                  onChange={(event) =>
                    updateField(
                      "difficulty",
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

                </select>

              </div>






              <div className="col-md-4">

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


                <div className="form-text">
                  Optional
                </div>

              </div>

            </div>






            <hr className="my-4" />


            <div className="mb-3">

              <h3 className="h5 mb-1">
                Required Skills
              </h3>


              <p className="text-secondary small mb-0">
                Select the skills students
                should demonstrate when
                completing this challenge.
              </p>

            </div>


            <div className="row g-3">



              <div className="col-md-6">

                <label className="form-label">
                  Skill
                </label>


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
                        key={
                          skill.id
                        }
                        value={
                          skill.id
                        }
                      >
                        {
                          skill.name
                        }
                      </option>

                    )
                  )}

                </select>

              </div>




              <div className="col-md-4">

                <label className="form-label">
                  Minimum Level
                </label>


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




              <div className="col-md-2 d-flex align-items-end">

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






            {
              requirements.length > 0 && (

                <div className="mt-3">

                  <div className="d-flex flex-wrap gap-2">

                    {requirements.map(
                      (
                        requirement
                      ) => (

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
                          title="Remove skill"
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

                </div>

              )
            }






            <hr className="my-4" />


            <div>

              <label className="form-label">
                Challenge Status
              </label>


              <select
                className="form-select"
                style={{
                  maxWidth:
                    "300px",
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


              <div className="form-text">

                Draft challenges are hidden
                from students.

                Published challenges can
                receive submissions.

              </div>

            </div>






            <button
              type="submit"
              className="btn btn-info mt-4"
              disabled={
                submitting
              }
            >

              {
                submitting
                  ? "Creating..."
                  : (
                    form.status === "open"
                      ? "Create & Publish Challenge"
                      : "Save Challenge"
                  )
              }

            </button>

          </form>

        </div>






        <div className="d-flex justify-content-between align-items-center mb-3">

          <div>

            <h2 className="h4 mb-1">
              My Challenges
            </h2>


            <p className="text-secondary small mb-0">
              Publish challenges and review
              student work.
            </p>

          </div>


          {!loading && (

            <span className="text-secondary small">

              {
                challenges.length
              }

              {" "}

              {
                challenges.length === 1
                  ? "challenge"
                  : "challenges"
              }

            </span>

          )}

        </div>






        {loading && (

          <p className="text-secondary">
            Loading challenges...
          </p>

        )}






        {
          !loading &&
          challenges.length === 0 && (

            <div className="glass-card">

              <p className="text-secondary mb-0">
                You have not created any
                challenges yet.
              </p>

            </div>

          )
        }






        {
          !loading &&
          challenges.map(
            (
              challenge
            ) => (

              <div
                key={
                  challenge.id
                }
                className="glass-card mb-4"
              >





                <div className="d-flex justify-content-between align-items-start gap-3 flex-wrap">

                  <div>

                    <p className="text-info text-uppercase small mb-1">

                      {
                        challenge.challenge_type
                          ?.replaceAll(
                            "_",
                            " "
                          )
                      }

                    </p>


                    <h3 className="h5 mb-1">

                      {
                        challenge.title
                      }

                    </h3>


                    <p className="text-secondary mb-2">

                      {
                        challenge.company_name
                      }

                    </p>


                    <div className="d-flex flex-wrap gap-2">



                      <span
                        className={
                          `badge ${
                            statusBadgeClass(
                              challenge.status
                            )
                          } text-capitalize`
                        }
                      >

                        {
                          challenge.status
                        }

                      </span>




                      <span
                        className={
                          `badge ${
                            difficultyBadgeClass(
                              challenge.difficulty
                            )
                          } text-capitalize`
                        }
                      >

                        {
                          challenge.difficulty
                        }

                      </span>

                    </div>

                  </div>






                  <div className="d-flex gap-2 flex-wrap">






                    <button
                      type="button"
                      className="btn btn-outline-info btn-sm"
                      onClick={() =>
                        viewSubmissions(
                          challenge.id
                        )
                      }
                    >
                      View Submissions
                    </button>






                    {
                      challenge.status
                      === "draft" && (

                        <button
                          type="button"
                          className="btn btn-success btn-sm"
                          disabled={
                            statusUpdatingId
                            === challenge.id
                          }
                          onClick={() =>
                            changeStatus(
                              challenge.id,
                              "open"
                            )
                          }
                        >

                          {
                            statusUpdatingId
                            === challenge.id
                              ? "Updating..."
                              : "Publish"
                          }

                        </button>

                      )
                    }






                    {
                      challenge.status
                      === "open" && (

                        <button
                          type="button"
                          className="btn btn-outline-warning btn-sm"
                          disabled={
                            statusUpdatingId
                            === challenge.id
                          }
                          onClick={() =>
                            changeStatus(
                              challenge.id,
                              "closed"
                            )
                          }
                        >

                          {
                            statusUpdatingId
                            === challenge.id
                              ? "Updating..."
                              : "Close"
                          }

                        </button>

                      )
                    }






                    {
                      challenge.status
                      === "closed" && (

                        <button
                          type="button"
                          className="btn btn-success btn-sm"
                          disabled={
                            statusUpdatingId
                            === challenge.id
                          }
                          onClick={() =>
                            changeStatus(
                              challenge.id,
                              "open"
                            )
                          }
                        >

                          {
                            statusUpdatingId
                            === challenge.id
                              ? "Updating..."
                              : "Reopen"
                          }

                        </button>

                      )
                    }

                  </div>

                </div>






                <p className="mt-3">

                  {
                    challenge.description
                  }

                </p>






                <div className="row small mt-4">

                  <div className="col-md-4 mb-3">

                    <span className="text-secondary">
                      Type
                    </span>

                    <div className="text-capitalize">

                      {
                        challenge.challenge_type
                          ?.replaceAll(
                            "_",
                            " "
                          )
                      }

                    </div>

                  </div>


                  <div className="col-md-4 mb-3">

                    <span className="text-secondary">
                      Difficulty
                    </span>

                    <div className="text-capitalize">

                      {
                        challenge.difficulty
                      }

                    </div>

                  </div>


                  <div className="col-md-4 mb-3">

                    <span className="text-secondary">
                      Deadline
                    </span>

                    <div>

                      {
                        challenge.deadline
                          || "No deadline"
                      }

                    </div>

                  </div>

                </div>






                <div className="mt-2">

                  <h4 className="h6">
                    Instructions
                  </h4>


                  <p className="text-secondary">
                    {
                      challenge.instructions
                    }
                  </p>

                </div>






                {
                  challenge.deliverables && (

                    <div className="mt-3">

                      <h4 className="h6">
                        Deliverables
                      </h4>


                      <p className="text-secondary">
                        {
                          challenge.deliverables
                        }
                      </p>

                    </div>

                  )
                }






                <div className="mt-3">

                  <h4 className="h6">
                    Required Skills
                  </h4>


                  {
                    (
                      challenge.skills
                      || []
                    ).length === 0 ? (

                      <p className="small text-secondary mb-0">
                        No specific skills
                        required.
                      </p>

                    ) : (

                      <div className="d-flex flex-wrap gap-2">

                        {
                          (
                            challenge.skills
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
                                  requirement.skill_name
                                  || requirement.skill
                                    ?.name
                                }

                                {" · "}

                                {
                                  requirement.minimum_level
                                }

                              </span>

                            )
                          )
                        }

                      </div>

                    )
                  }

                </div>

              </div>

            )
          )
        }

      </>
    );
  }