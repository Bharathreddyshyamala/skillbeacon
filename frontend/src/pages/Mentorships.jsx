import {
    useEffect,
    useState,
  } from "react";
  
  import {
    apiRequest,
    jsonBody,
  } from "../api";
  
  import {
    useAuth,
  } from "../AuthContext";
  
  
  const EMPTY_REQUEST = {
    focus_area: "",
    goals: "",
    message: "",
  };
  
  
  const EMPTY_SESSION = {
    title: "",
    description: "",
    scheduled_start: "",
    scheduled_end: "",
    meeting_url: "",
    shared_notes: "",
  };
  
  
  export default function Mentorships() {
    const { user } = useAuth();
  
    const [mentors, setMentors] =
      useState([]);
  
    const [mentorships, setMentorships] =
      useState([]);
  
    const [selectedMentorId, setSelectedMentorId] =
      useState("");
  
    const [requestForm, setRequestForm] =
      useState(
        EMPTY_REQUEST
      );
  
    const [mentorResponses, setMentorResponses] =
      useState({});
  
    const [sessionMentorshipId, setSessionMentorshipId] =
      useState("");
  
    const [sessionForm, setSessionForm] =
      useState(
        EMPTY_SESSION
      );
  
    const [search, setSearch] =
      useState("");
  
    const [loading, setLoading] =
      useState(true);
  
    const [submitting, setSubmitting] =
      useState(false);
  
    const [error, setError] =
      useState("");
  
    const [message, setMessage] =
      useState("");
  
  
    const isStudent =
      user?.role === "student";
  
    const isMentor =
      user?.role === "mentor";
  
  
    async function loadData(
      mentorSearch = search,
    ) {
      setLoading(true);
      setError("");
  
      try {
        if (isStudent) {
          const params =
            new URLSearchParams();
  
          params.set(
            "limit",
            "100"
          );
  
          if (
            mentorSearch.trim()
          ) {
            params.set(
              "search",
              mentorSearch.trim()
            );
          }
  
          const [
            mentorResponse,
            mentorshipResponse,
          ] = await Promise.all([
            apiRequest(
              `/mentorships/mentors?${params.toString()}`
            ),
  
            apiRequest(
              "/mentorships/me?limit=100"
            ),
          ]);
  
          setMentors(
            Array.isArray(
              mentorResponse?.items
            )
              ? mentorResponse.items
              : []
          );
  
          setMentorships(
            Array.isArray(
              mentorshipResponse?.items
            )
              ? mentorshipResponse.items
              : []
          );
        } else {
          const mentorshipResponse =
            await apiRequest(
              "/mentorships/me?limit=100"
            );
  
          const loadedItems =
            Array.isArray(
              mentorshipResponse?.items
            )
              ? mentorshipResponse.items
              : [];
  
          setMentorships(
            loadedItems
          );
  
          const responseValues = {};
  
          loadedItems.forEach(
            (item) => {
              responseValues[
                item.id
              ] =
                item.mentor_response
                || "";
            }
          );
  
          setMentorResponses(
            responseValues
          );
        }
      } catch (requestError) {
        setError(
          requestError.message ||
          "Unable to load mentorship information."
        );
      } finally {
        setLoading(false);
      }
    }
  
  
    useEffect(() => {
      if (
        isStudent ||
        isMentor
      ) {
        loadData();
      }
    }, [
      user?.role,
    ]);
  
  
    function updateRequestField(
      field,
      value,
    ) {
      setRequestForm({
        ...requestForm,
        [field]: value,
      });
    }
  
  
    function updateSessionField(
      field,
      value,
    ) {
      setSessionForm({
        ...sessionForm,
        [field]: value,
      });
    }
  
  
    function openRequestForm(
      mentorId,
    ) {
      if (
        selectedMentorId
        === mentorId
      ) {
        setSelectedMentorId("");
        setRequestForm(
          EMPTY_REQUEST
        );
  
        return;
      }
  
      setSelectedMentorId(
        mentorId
      );
  
      setRequestForm(
        EMPTY_REQUEST
      );
  
      setError("");
      setMessage("");
    }
  
  
    async function sendRequest(
      mentorId,
    ) {
      setError("");
      setMessage("");
  
      if (
        !requestForm.focus_area.trim()
      ) {
        setError(
          "Enter a focus area."
        );
  
        return;
      }
  
      if (
        requestForm.goals.trim().length
        < 10
      ) {
        setError(
          "Describe your goals using at least 10 characters."
        );
  
        return;
      }
  
      setSubmitting(true);
  
      try {
        await apiRequest(
          "/mentorships/requests",
          {
            method: "POST",
  
            body: jsonBody({
              mentor_id:
                mentorId,
  
              focus_area:
                requestForm
                  .focus_area
                  .trim(),
  
              goals:
                requestForm
                  .goals
                  .trim(),
  
              message:
                requestForm
                  .message
                  .trim()
                || null,
            }),
          }
        );
  
        setMessage(
          "Mentorship request sent."
        );
  
        setSelectedMentorId("");
  
        setRequestForm(
          EMPTY_REQUEST
        );
  
        await loadData();
      } catch (requestError) {
        setError(
          requestError.message ||
          "Unable to send mentorship request."
        );
      } finally {
        setSubmitting(false);
      }
    }
  
  
    async function cancelRequest(
      mentorshipId,
    ) {
      const confirmed =
        window.confirm(
          "Cancel this mentorship request?"
        );
  
      if (!confirmed) {
        return;
      }
  
      setError("");
      setMessage("");
  
      try {
        await apiRequest(
          `/mentorships/${mentorshipId}/cancel`,
          {
            method: "PATCH",
          }
        );
  
        setMessage(
          "Mentorship request cancelled."
        );
  
        await loadData();
      } catch (requestError) {
        setError(
          requestError.message ||
          "Unable to cancel request."
        );
      }
    }
  
  
    async function respond(
      mentorshipId,
      decision,
    ) {
      const confirmed =
        window.confirm(
          decision === "accepted"
            ? "Accept this mentorship request?"
            : "Reject this mentorship request?"
        );
  
      if (!confirmed) {
        return;
      }
  
      setError("");
      setMessage("");
  
      try {
        await apiRequest(
          `/mentorships/${mentorshipId}/respond`,
          {
            method: "PATCH",
  
            body: jsonBody({
              decision,
  
              mentor_response:
                mentorResponses[
                  mentorshipId
                ]?.trim()
                || null,
            }),
          }
        );
  
        setMessage(
          decision === "accepted"
            ? "Mentorship request accepted."
            : "Mentorship request rejected."
        );
  
        await loadData();
      } catch (requestError) {
        setError(
          requestError.message ||
          "Unable to respond to mentorship request."
        );
      }
    }
  
  
    function openSessionForm(
      mentorshipId,
    ) {
      if (
        sessionMentorshipId
        === mentorshipId
      ) {
        setSessionMentorshipId("");
        setSessionForm(
          EMPTY_SESSION
        );
  
        return;
      }
  
      setSessionMentorshipId(
        mentorshipId
      );
  
      setSessionForm(
        EMPTY_SESSION
      );
  
      setError("");
      setMessage("");
    }
  
  
    async function scheduleSession(
      mentorshipId,
    ) {
      setError("");
      setMessage("");
  
      if (
        !sessionForm.title.trim()
      ) {
        setError(
          "Enter a session title."
        );
  
        return;
      }
  
      if (
        !sessionForm.scheduled_start ||
        !sessionForm.scheduled_end
      ) {
        setError(
          "Select session start and end times."
        );
  
        return;
      }
  
      const start =
        new Date(
          sessionForm.scheduled_start
        );
  
      const end =
        new Date(
          sessionForm.scheduled_end
        );
  
      if (
        end <= start
      ) {
        setError(
          "Session end time must be after the start time."
        );
  
        return;
      }
  
      setSubmitting(true);
  
      try {
        await apiRequest(
          `/mentorships/${mentorshipId}/sessions`,
          {
            method: "POST",
  
            body: jsonBody({
              title:
                sessionForm
                  .title
                  .trim(),
  
              description:
                sessionForm
                  .description
                  .trim()
                || null,
  
              scheduled_start:
                start.toISOString(),
  
              scheduled_end:
                end.toISOString(),
  
              meeting_url:
                sessionForm
                  .meeting_url
                  .trim()
                || null,
  
              shared_notes:
                sessionForm
                  .shared_notes
                  .trim()
                || null,
            }),
          }
        );
  
        setMessage(
          "Mentorship session scheduled."
        );
  
        setSessionMentorshipId("");
  
        setSessionForm(
          EMPTY_SESSION
        );
  
        await loadData();
      } catch (requestError) {
        setError(
          requestError.message ||
          "Unable to schedule mentorship session."
        );
      } finally {
        setSubmitting(false);
      }
    }
  
  
    async function updateSessionStatus(
      sessionId,
      newStatus,
    ) {
      const confirmed =
        window.confirm(
          newStatus === "completed"
            ? "Mark this session completed?"
            : "Cancel this session?"
        );
  
      if (!confirmed) {
        return;
      }
  
      setError("");
      setMessage("");
  
      try {
        await apiRequest(
          `/mentorships/sessions/${sessionId}/status`,
          {
            method: "PATCH",
  
            body: jsonBody({
              status:
                newStatus,
  
              shared_notes:
                null,
            }),
          }
        );
  
        setMessage(
          `Session changed to ${newStatus}.`
        );
  
        await loadData();
      } catch (requestError) {
        setError(
          requestError.message ||
          "Unable to update session."
        );
      }
    }
  
  
    async function finishMentorship(
      mentorshipId,
    ) {
      const confirmed =
        window.confirm(
          "Complete this mentorship? Any remaining scheduled sessions will be cancelled."
        );
  
      if (!confirmed) {
        return;
      }
  
      setError("");
      setMessage("");
  
      try {
        await apiRequest(
          `/mentorships/${mentorshipId}/complete`,
          {
            method: "PATCH",
          }
        );
  
        setMessage(
          "Mentorship completed."
        );
  
        await loadData();
      } catch (requestError) {
        setError(
          requestError.message ||
          "Unable to complete mentorship."
        );
      }
    }
  
  
    function statusBadgeClass(
      status,
    ) {
      switch (status) {
        case "active":
          return "text-bg-success";
  
        case "pending":
          return "text-bg-warning";
  
        case "rejected":
          return "text-bg-danger";
  
        case "completed":
          return "text-bg-info";
  
        case "cancelled":
          return "text-bg-secondary";
  
        default:
          return "text-bg-secondary";
      }
    }
  
  
    function sessionBadgeClass(
      status,
    ) {
      switch (status) {
        case "completed":
          return "text-bg-success";
  
        case "cancelled":
          return "text-bg-secondary";
  
        default:
          return "text-bg-info";
      }
    }
  
  
    const pendingRequests =
      mentorships.filter(
        (item) =>
          item.status === "pending"
      );
  
    const otherMentorships =
      mentorships.filter(
        (item) =>
          item.status !== "pending"
      );
  
  
    return (
      <>
        <div className="mb-4">
          <p className="text-info fw-semibold text-uppercase">
            Mentorship
          </p>
  
          <h1 className="display-6 fw-bold">
            {isStudent
              ? "Find Your Mentor"
              : "Mentorship Management"}
          </h1>
  
          <p className="text-secondary">
            {isStudent
              ? "Connect with experienced mentors and receive career guidance."
              : "Review student requests, guide mentees, and schedule sessions."}
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
            Loading mentorship information...
          </p>
        )}
  
  
        {/* =====================================================
            STUDENT: MENTOR DIRECTORY
        ====================================================== */}
  
        {!loading && isStudent && (
          <>
            <div className="glass-card mb-4">
              <form
                className="row g-3"
                onSubmit={(event) => {
                  event.preventDefault();
  
                  loadData(
                    search
                  );
                }}
              >
                <div className="col-md-10">
                  <label className="form-label">
                    Search Mentors
                  </label>
  
                  <input
                    className="form-control"
                    value={search}
                    onChange={(event) =>
                      setSearch(
                        event.target.value
                      )
                    }
                    placeholder="Search by mentor email..."
                  />
                </div>
  
                <div className="col-md-2 d-flex align-items-end">
                  <button
                    className="btn btn-info w-100"
                    type="submit"
                  >
                    Search
                  </button>
                </div>
              </form>
            </div>
  
  
            <h2 className="h4 mb-3">
              Available Mentors
            </h2>
  
  
            {mentors.length === 0 && (
              <div className="glass-card mb-5">
                <p className="text-secondary mb-0">
                  No active mentors were found.
                </p>
              </div>
            )}
  
  
            {mentors.map(
              (mentor) => (
                <div
                  key={mentor.mentor_id}
                  className="glass-card mb-4"
                >
                  <div className="d-flex justify-content-between gap-3 flex-wrap">
                    <div>
                      <h3 className="h4 mb-1">
                        {mentor.name}
                      </h3>
  
                      <p className="text-secondary mb-1">
                        {mentor.email}
                      </p>
  
                      {mentor.headline && (
                        <p className="text-info mb-2">
                          {mentor.headline}
                        </p>
                      )}
                    </div>
  
                    <button
                      type="button"
                      className="btn btn-outline-info"
                      onClick={() =>
                        openRequestForm(
                          mentor.mentor_id
                        )
                      }
                    >
                      {selectedMentorId
                      === mentor.mentor_id
                        ? "Cancel"
                        : "Request Mentorship"}
                    </button>
                  </div>
  
  
                  {mentor.bio && (
                    <p className="mt-3">
                      {mentor.bio}
                    </p>
                  )}
  
  
                  <div className="row small">
                    <div className="col-md-6">
                      <span className="text-secondary">
                        Expertise
                      </span>
  
                      <div>
                        {mentor.expertise ||
                          "Not specified"}
                      </div>
                    </div>
  
                    <div className="col-md-6">
                      <span className="text-secondary">
                        Experience
                      </span>
  
                      <div>
                        {mentor.years_experience
                          ? `${mentor.years_experience} years`
                          : "Not specified"}
                      </div>
                    </div>
                  </div>
  
  
                  {(mentor.skills || []).length > 0 && (
                    <div className="mt-3">
                      <h4 className="h6">
                        Skill Passport
                      </h4>
  
                      <div className="d-flex flex-wrap gap-2">
                        {mentor.skills.map(
                          (skill) => (
                            <span
                              key={skill.id}
                              className="badge text-bg-secondary"
                            >
                              {skill.name}
                              {" · "}
                              {skill.level}
                              {" · "}
                              {skill.confidence_score}%
                            </span>
                          )
                        )}
                      </div>
                    </div>
                  )}
  
  
                  {selectedMentorId
                  === mentor.mentor_id && (
                    <div className="border rounded p-4 mt-4">
                      <h4 className="h5 mb-3">
                        Send Mentorship Request
                      </h4>
  
                      <div className="mb-3">
                        <label className="form-label">
                          Focus Area
                        </label>
  
                        <input
                          className="form-control"
                          value={
                            requestForm.focus_area
                          }
                          onChange={(event) =>
                            updateRequestField(
                              "focus_area",
                              event.target.value
                            )
                          }
                          placeholder="Backend development, interviews, career planning..."
                        />
                      </div>
  
                      <div className="mb-3">
                        <label className="form-label">
                          Goals
                        </label>
  
                        <textarea
                          className="form-control"
                          rows="5"
                          maxLength="3000"
                          value={
                            requestForm.goals
                          }
                          onChange={(event) =>
                            updateRequestField(
                              "goals",
                              event.target.value
                            )
                          }
                          placeholder="Describe what you want to achieve..."
                        />
                      </div>
  
                      <div className="mb-3">
                        <label className="form-label">
                          Message
                        </label>
  
                        <textarea
                          className="form-control"
                          rows="3"
                          maxLength="2000"
                          value={
                            requestForm.message
                          }
                          onChange={(event) =>
                            updateRequestField(
                              "message",
                              event.target.value
                            )
                          }
                          placeholder="Introduce yourself to the mentor..."
                        />
                      </div>
  
                      <button
                        type="button"
                        className="btn btn-success"
                        disabled={submitting}
                        onClick={() =>
                          sendRequest(
                            mentor.mentor_id
                          )
                        }
                      >
                        {submitting
                          ? "Sending..."
                          : "Send Request"}
                      </button>
                    </div>
                  )}
                </div>
              )
            )}
          </>
        )}
  
  
        {/* =====================================================
            MENTOR: PENDING REQUESTS
        ====================================================== */}
  
        {!loading && isMentor && (
          <>
            <h2 className="h4 mb-3">
              Pending Requests
            </h2>
  
            {pendingRequests.length === 0 && (
              <div className="glass-card mb-5">
                <p className="text-secondary mb-0">
                  No mentorship requests are waiting for review.
                </p>
              </div>
            )}
  
            {pendingRequests.map(
              (mentorship) => (
                <div
                  key={mentorship.id}
                  className="glass-card mb-4"
                >
                  <div className="d-flex justify-content-between flex-wrap gap-3">
                    <div>
                      <h3 className="h5 mb-1">
                        {mentorship.student_name}
                      </h3>
  
                      <p className="text-secondary">
                        {mentorship.student_email}
                      </p>
                    </div>
  
                    <span className="badge text-bg-warning text-capitalize">
                      Pending
                    </span>
                  </div>
  
                  <p>
                    <strong>
                      Focus Area:
                    </strong>
                    {" "}
                    {mentorship.focus_area}
                  </p>
  
                  <p>
                    <strong>
                      Goals:
                    </strong>
                    {" "}
                    {mentorship.goals}
                  </p>
  
                  {mentorship.message && (
                    <p>
                      <strong>
                        Student Message:
                      </strong>
                      {" "}
                      {mentorship.message}
                    </p>
                  )}
  
                  <div className="mb-3">
                    <label className="form-label">
                      Response to Student
                    </label>
  
                    <textarea
                      className="form-control"
                      rows="3"
                      value={
                        mentorResponses[
                          mentorship.id
                        ] || ""
                      }
                      onChange={(event) =>
                        setMentorResponses({
                          ...mentorResponses,
  
                          [mentorship.id]:
                            event.target.value,
                        })
                      }
                    />
                  </div>
  
                  <div className="d-flex gap-2">
                    <button
                      type="button"
                      className="btn btn-success"
                      onClick={() =>
                        respond(
                          mentorship.id,
                          "accepted"
                        )
                      }
                    >
                      Accept
                    </button>
  
                    <button
                      type="button"
                      className="btn btn-outline-danger"
                      onClick={() =>
                        respond(
                          mentorship.id,
                          "rejected"
                        )
                      }
                    >
                      Reject
                    </button>
                  </div>
                </div>
              )
            )}
          </>
        )}
  
  
        {/* =====================================================
            MY MENTORSHIPS
        ====================================================== */}
  
        {!loading && (
          <>
            <h2 className="h4 mt-5 mb-3">
              {isStudent
                ? "My Mentorships"
                : "Current and Previous Mentorships"}
            </h2>
  
            {(isStudent
              ? mentorships
              : otherMentorships
            ).length === 0 && (
              <div className="glass-card">
                <p className="text-secondary mb-0">
                  No mentorships found.
                </p>
              </div>
            )}
  
            {(isStudent
              ? mentorships
              : otherMentorships
            ).map(
              (mentorship) => (
                <div
                  key={mentorship.id}
                  className="glass-card mb-4"
                >
                  <div className="d-flex justify-content-between flex-wrap gap-3">
                    <div>
                      <h3 className="h5 mb-1">
                        {isStudent
                          ? mentorship.mentor_name
                          : mentorship.student_name}
                      </h3>
  
                      <p className="text-secondary mb-2">
                        {isStudent
                          ? mentorship.mentor_email
                          : mentorship.student_email}
                      </p>
                    </div>
  
                    <span
                      className={
                        `badge ${
                          statusBadgeClass(
                            mentorship.status
                          )
                        } text-capitalize`
                      }
                    >
                      {mentorship.status}
                    </span>
                  </div>
  
                  <p>
                    <strong>
                      Focus Area:
                    </strong>
                    {" "}
                    {mentorship.focus_area}
                  </p>
  
                  <p>
                    <strong>
                      Goals:
                    </strong>
                    {" "}
                    {mentorship.goals}
                  </p>
  
                  {mentorship.mentor_response && (
                    <p>
                      <strong>
                        Mentor Response:
                      </strong>
                      {" "}
                      {mentorship.mentor_response}
                    </p>
                  )}
  
  
                  {mentorship.status === "pending" &&
                    isStudent && (
                      <button
                        type="button"
                        className="btn btn-outline-danger btn-sm"
                        onClick={() =>
                          cancelRequest(
                            mentorship.id
                          )
                        }
                      >
                        Cancel Request
                      </button>
                    )}
  
  
                  {mentorship.status === "active" && (
                    <>
                      <div className="d-flex gap-2 flex-wrap">
                        {isMentor && (
                          <button
                            type="button"
                            className="btn btn-outline-info btn-sm"
                            onClick={() =>
                              openSessionForm(
                                mentorship.id
                              )
                            }
                          >
                            {sessionMentorshipId
                            === mentorship.id
                              ? "Close Session Form"
                              : "Schedule Session"}
                          </button>
                        )}
  
                        <button
                          type="button"
                          className="btn btn-outline-warning btn-sm"
                          onClick={() =>
                            finishMentorship(
                              mentorship.id
                            )
                          }
                        >
                          Complete Mentorship
                        </button>
                      </div>
  
  
                      {isMentor &&
                        sessionMentorshipId
                        === mentorship.id && (
                          <div className="border rounded p-4 mt-4">
                            <h4 className="h5">
                              Schedule Session
                            </h4>
  
                            <div className="mb-3">
                              <label className="form-label">
                                Title
                              </label>
  
                              <input
                                className="form-control"
                                value={
                                  sessionForm.title
                                }
                                onChange={(event) =>
                                  updateSessionField(
                                    "title",
                                    event.target.value
                                  )
                                }
                              />
                            </div>
  
                            <div className="mb-3">
                              <label className="form-label">
                                Description
                              </label>
  
                              <textarea
                                className="form-control"
                                rows="3"
                                value={
                                  sessionForm.description
                                }
                                onChange={(event) =>
                                  updateSessionField(
                                    "description",
                                    event.target.value
                                  )
                                }
                              />
                            </div>
  
                            <div className="row g-3">
                              <div className="col-md-6">
                                <label className="form-label">
                                  Start
                                </label>
  
                                <input
                                  type="datetime-local"
                                  className="form-control"
                                  value={
                                    sessionForm.scheduled_start
                                  }
                                  onChange={(event) =>
                                    updateSessionField(
                                      "scheduled_start",
                                      event.target.value
                                    )
                                  }
                                />
                              </div>
  
                              <div className="col-md-6">
                                <label className="form-label">
                                  End
                                </label>
  
                                <input
                                  type="datetime-local"
                                  className="form-control"
                                  value={
                                    sessionForm.scheduled_end
                                  }
                                  onChange={(event) =>
                                    updateSessionField(
                                      "scheduled_end",
                                      event.target.value
                                    )
                                  }
                                />
                              </div>
                            </div>
  
                            <div className="mt-3">
                              <label className="form-label">
                                Meeting URL
                              </label>
  
                              <input
                                type="url"
                                className="form-control"
                                value={
                                  sessionForm.meeting_url
                                }
                                onChange={(event) =>
                                  updateSessionField(
                                    "meeting_url",
                                    event.target.value
                                  )
                                }
                              />
                            </div>
  
                            <div className="mt-3">
                              <label className="form-label">
                                Shared Notes
                              </label>
  
                              <textarea
                                className="form-control"
                                rows="3"
                                value={
                                  sessionForm.shared_notes
                                }
                                onChange={(event) =>
                                  updateSessionField(
                                    "shared_notes",
                                    event.target.value
                                  )
                                }
                              />
                            </div>
  
                            <button
                              type="button"
                              className="btn btn-success mt-3"
                              disabled={submitting}
                              onClick={() =>
                                scheduleSession(
                                  mentorship.id
                                )
                              }
                            >
                              {submitting
                                ? "Scheduling..."
                                : "Schedule Session"}
                            </button>
                          </div>
                        )}
                    </>
                  )}
  
  
                  <div className="mt-4">
                    <h4 className="h6">
                      Sessions
                    </h4>
  
                    {(mentorship.sessions || []).length === 0 && (
                      <p className="small text-secondary">
                        No sessions have been scheduled.
                      </p>
                    )}
  
                    {(mentorship.sessions || []).map(
                      (session) => (
                        <div
                          key={session.id}
                          className="border rounded p-3 mb-2"
                        >
                          <div className="d-flex justify-content-between flex-wrap gap-2">
                            <div>
                              <strong>
                                {session.title}
                              </strong>
  
                              <div className="small text-secondary">
                                {new Date(
                                  session.scheduled_start
                                ).toLocaleString()}
                                {" – "}
                                {new Date(
                                  session.scheduled_end
                                ).toLocaleString()}
                              </div>
                            </div>
  
                            <span
                              className={
                                `badge ${
                                  sessionBadgeClass(
                                    session.status
                                  )
                                } text-capitalize`
                              }
                            >
                              {session.status}
                            </span>
                          </div>
  
                          {session.description && (
                            <p className="small mt-2 mb-1">
                              {session.description}
                            </p>
                          )}
  
                          {session.shared_notes && (
                            <p className="small text-secondary">
                              {session.shared_notes}
                            </p>
                          )}
  
                          {session.meeting_url &&
                            session.status === "scheduled" && (
                              <a
                                href={session.meeting_url}
                                target="_blank"
                                rel="noreferrer"
                                className="btn btn-outline-info btn-sm me-2"
                              >
                                Join Meeting
                              </a>
                            )}
  
                          {isMentor &&
                            session.status === "scheduled" && (
                              <>
                                <button
                                  type="button"
                                  className="btn btn-outline-success btn-sm me-2"
                                  onClick={() =>
                                    updateSessionStatus(
                                      session.id,
                                      "completed"
                                    )
                                  }
                                >
                                  Mark Completed
                                </button>
  
                                <button
                                  type="button"
                                  className="btn btn-outline-danger btn-sm"
                                  onClick={() =>
                                    updateSessionStatus(
                                      session.id,
                                      "cancelled"
                                    )
                                  }
                                >
                                  Cancel
                                </button>
                              </>
                            )}
                        </div>
                      )
                    )}
                  </div>
                </div>
              )
            )}
          </>
        )}
      </>
    );
  }