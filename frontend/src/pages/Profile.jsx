import { useEffect, useState } from "react";
import { ApiError, apiRequest } from "../api";

const empty = {
  first_name: "", last_name: "", headline: "", summary: "", education: "",
  work_experience: "", preferred_roles: "", preferred_locations: "",
  work_authorization: "", availability: "", career_goals: "", github_url: "",
  linkedin_url: "", portfolio_url: "", company_name: "", industry: "",
  company_size: "", website: "", description: "", location: "",
  display_name: "", bio: "", years_of_experience: "", languages: "",
  mentorship_formats: "", is_accepting_requests: true, is_public: false,
};

const toText = (value) => Array.isArray(value) ? value.join(", ") : "";
const toList = (value) => value.split(",").map((x) => x.trim()).filter(Boolean);

function Field({ label, name, value, onChange, type = "text" }) {
  return <div className="mb-3"><label className="form-label">{label}</label>
    <input className="form-control" name={name} value={value} onChange={onChange} type={type} /></div>;
}

function Area({ label, name, value, onChange }) {
  return <div className="mb-3"><label className="form-label">{label}</label>
    <textarea className="form-control" rows="4" name={name} value={value} onChange={onChange} /></div>;
}

export default function Profile() {
  const [envelope, setEnvelope] = useState(null);
  const [form, setForm] = useState(empty);
  const [resume, setResume] = useState(null);
  const [resumesList, setResumesList] = useState([]);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [saving, setSaving] = useState(false);

  const loadResumes = () => {
    apiRequest("/documents/my-documents?document_type=resume")
      .then((data) => setResumesList(data.items || []))
      .catch(() => {});
  };

  useEffect(() => {
    apiRequest("/profiles/me").then((data) => {
      setEnvelope(data);
      const p = data.profile || {};
      setForm({ ...empty, ...p,
        preferred_roles: toText(p.preferred_roles),
        preferred_locations: toText(p.preferred_locations),
        languages: toText(p.languages),
        mentorship_formats: toText(p.mentorship_formats),
        years_of_experience: p.years_of_experience ?? "",
      });
      if (data.profile_type === "student") {
        loadResumes();
      }
    }).catch((err) => setError(err.message));
  }, []);

  const role = envelope?.profile_type;
  function change(e) {
    const { name, value, checked, type } = e.target;
    setForm((current) => ({ ...current, [name]: type === "checkbox" ? checked : value }));
  }

  function payload() {
    if (role === "student") return {
      first_name: form.first_name || null, last_name: form.last_name || null,
      headline: form.headline || null, summary: form.summary || null,
      education: form.education || null, work_experience: form.work_experience || null,
      preferred_roles: toList(form.preferred_roles),
      preferred_locations: toList(form.preferred_locations),
      work_authorization: form.work_authorization || null,
      availability: form.availability || null, career_goals: form.career_goals || null,
      github_url: form.github_url || null, linkedin_url: form.linkedin_url || null,
      portfolio_url: form.portfolio_url || null, is_public: form.is_public,
    };
    if (role === "employer") return {
      company_name: form.company_name || null, industry: form.industry || null,
      company_size: form.company_size || null, website: form.website || null,
      description: form.description || null, location: form.location || null,
      is_public: form.is_public,
    };
    return {
      display_name: form.display_name || null, headline: form.headline || null,
      bio: form.bio || null, industry: form.industry || null,
      years_of_experience: form.years_of_experience === "" ? null : Number(form.years_of_experience),
      languages: toList(form.languages), mentorship_formats: toList(form.mentorship_formats),
      availability: form.availability || null,
      is_accepting_requests: form.is_accepting_requests,
      is_public: form.is_public,
    };
  }

  async function save(e) {
    e.preventDefault(); setSaving(true); setMessage(""); setError("");
    try {
      const data = await apiRequest("/profiles/me", { method: "PUT", body: JSON.stringify(payload()) });
      setEnvelope(data); setMessage("Profile saved successfully.");
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Unable to save profile.");
    } finally { setSaving(false); }
  }

  async function upload(e) {
    e.preventDefault();
    if (!resume) return setError("Choose a PDF or DOCX resume.");
    const data = new FormData();
    data.append("resume", resume);
    try {
      const result = await apiRequest("/profiles/me/resume", {
        method: "POST",
        body: data,
      });
      setEnvelope(result);
      setMessage("Resume uploaded and added to your library successfully.");
      setError("");
      setResume(null);
      loadResumes();
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleDeleteResume(docId) {
    if (!window.confirm("Are you sure you want to delete this resume?")) return;
    try {
      await apiRequest(`/documents/${docId}`, { method: "DELETE" });
      setMessage("Resume deleted from library.");
      loadResumes();
      const updatedProfile = await apiRequest("/profiles/me");
      setEnvelope(updatedProfile);
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleSetPrimaryResume(fileUrl) {
    try {
      const updated = await apiRequest("/profiles/me", {
        method: "PUT",
        body: JSON.stringify({ ...payload(), resume_path: fileUrl }),
      });
      setEnvelope(updated);
      setMessage("Primary active resume updated.");
    } catch (err) {
      setError(err.message);
    }
  }

  async function handleViewDocument(docId) {
    try {
      const data = await apiRequest(`/documents/${docId}/download`);
      if (data?.download_url) {
        window.open(data.download_url, "_blank", "noopener,noreferrer");
      } else {
        setError("Download link not available.");
      }
    } catch (err) {
      setError(err.message || "Failed to open document.");
    }
  }

  if (!envelope && !error) return <p className="text-secondary">Loading profile...</p>;

  return <>
    <div className="mb-4"><span className="eyebrow">Role-based profile</span>
      <h1 className="display-6 fw-bold mt-2 text-capitalize">{role} profile</h1></div>
    {message && <div className="alert alert-success">{message}</div>}
    {error && <div className="alert alert-danger">{error}</div>}
    <div className="row g-4">
      <div className="col-xl-8">
        <form className="glass-card" onSubmit={save}>
          {role === "student" && <>
            <div className="row"><div className="col-md-6"><Field label="First name" name="first_name" value={form.first_name} onChange={change} /></div>
            <div className="col-md-6"><Field label="Last name" name="last_name" value={form.last_name} onChange={change} /></div></div>
            <Field label="Headline" name="headline" value={form.headline} onChange={change} />
            <Area label="Summary" name="summary" value={form.summary} onChange={change} />
            <Area label="Education" name="education" value={form.education} onChange={change} />
            <Area label="Work experience" name="work_experience" value={form.work_experience} onChange={change} />
            <Field label="Preferred roles (comma separated)" name="preferred_roles" value={form.preferred_roles} onChange={change} />
            <Field label="Preferred locations (comma separated)" name="preferred_locations" value={form.preferred_locations} onChange={change} />
            <Field label="Work authorization" name="work_authorization" value={form.work_authorization} onChange={change} />
            <Field label="Availability" name="availability" value={form.availability} onChange={change} />
            <Area label="Career goals" name="career_goals" value={form.career_goals} onChange={change} />
            <Field label="GitHub URL" name="github_url" value={form.github_url} onChange={change} type="url" />
            <Field label="LinkedIn URL" name="linkedin_url" value={form.linkedin_url} onChange={change} type="url" />
            <Field label="Portfolio URL" name="portfolio_url" value={form.portfolio_url} onChange={change} type="url" />
          </>}
          {role === "employer" && <>
            <Field label="Company name" name="company_name" value={form.company_name} onChange={change} />
            <Field label="Industry" name="industry" value={form.industry} onChange={change} />
            <Field label="Company size" name="company_size" value={form.company_size} onChange={change} />
            <Field label="Website" name="website" value={form.website} onChange={change} type="url" />
            <Area label="Description" name="description" value={form.description} onChange={change} />
            <Field label="Location" name="location" value={form.location} onChange={change} />
          </>}
          {role === "mentor" && <>
            <Field label="Display name" name="display_name" value={form.display_name} onChange={change} />
            <Field label="Headline" name="headline" value={form.headline} onChange={change} />
            <Area label="Bio" name="bio" value={form.bio} onChange={change} />
            <Field label="Industry" name="industry" value={form.industry} onChange={change} />
            <Field label="Years of experience" name="years_of_experience" value={form.years_of_experience} onChange={change} type="number" />
            <Field label="Languages (comma separated)" name="languages" value={form.languages} onChange={change} />
            <Field label="Mentorship formats (comma separated)" name="mentorship_formats" value={form.mentorship_formats} onChange={change} />
            <Area label="Availability" name="availability" value={form.availability} onChange={change} />
            <div className="form-check form-switch mb-3"><input className="form-check-input" type="checkbox" name="is_accepting_requests" checked={form.is_accepting_requests} onChange={change} />
              <label className="form-check-label">Accepting mentorship requests</label></div>
          </>}
          <div className="visibility-box"><div><strong>Public profile</strong><p className="small text-secondary mb-0">Allow public profile access.</p></div>
            <div className="form-check form-switch"><input className="form-check-input" type="checkbox" name="is_public" checked={form.is_public} onChange={change} /></div></div>
          <button className="btn btn-info mt-4" disabled={saving}>{saving ? "Saving..." : "Save profile"}</button>
        </form>
      </div>
      <div className="col-xl-4">
        <aside className="glass-card"><p className="section-label">Visibility</p>
          <span className="status-pill">{form.is_public ? "Public" : "Private"}</span></aside>
        {role === "student" && (
          <div className="glass-card mt-4">
            <p className="section-label">Resume Library (Cloudflare R2)</p>
            <h2 className="h5">Upload New Resume</h2>
            <p className="small text-secondary">
              PDF or DOCX (Max 5 MB). Upload multiple tailored resumes for different roles.
            </p>
            <form onSubmit={upload}>
              <input
                className="form-control"
                type="file"
                accept=".pdf,.docx,.doc"
                onChange={(e) => setResume(e.target.files?.[0] || null)}
              />
              <button
                className="btn btn-outline-info w-100 mt-3"
                disabled={!resume}
              >
                Upload to Resume Library
              </button>
            </form>

            <div className="mt-4">
              <h6 className="fw-semibold text-secondary text-uppercase small">
                Your Stored Resumes ({resumesList.length})
              </h6>
              {resumesList.length === 0 && (
                <p className="small text-muted mb-0">No resumes stored yet.</p>
              )}
              <div className="d-flex flex-column gap-2 mt-2">
                {resumesList.map((doc) => {
                  const isPrimary =
                    envelope?.profile?.resume_path === doc.file_url;
                  return (
                    <div
                      key={doc.id}
                      className={`p-2 rounded bg-dark border ${
                        isPrimary ? "border-info" : "border-secondary"
                      }`}
                    >
                      <div className="d-flex align-items-center justify-content-between">
                        <div className="text-truncate me-2">
                          <span className="small fw-semibold text-light text-truncate d-block">
                            {doc.file_name}
                          </span>
                          <span className="text-muted" style={{ fontSize: "11px" }}>
                            {(doc.size_bytes / (1024 * 1024)).toFixed(2)} MB •{" "}
                            {new Date(doc.created_at).toLocaleDateString()}
                          </span>
                        </div>
                        {isPrimary && (
                          <span className="badge bg-info text-dark" style={{ fontSize: "10px" }}>
                            Primary
                          </span>
                        )}
                      </div>
                      <div className="d-flex gap-2 mt-2 pt-2 border-top border-secondary">
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-light py-0 px-2"
                          style={{ fontSize: "11px" }}
                          onClick={() => handleViewDocument(doc.id)}
                        >
                          View
                        </button>
                        {!isPrimary && (
                          <button
                            type="button"
                            className="btn btn-sm btn-outline-info py-0 px-2"
                            style={{ fontSize: "11px" }}
                            onClick={() => handleSetPrimaryResume(doc.file_url)}
                          >
                            Set Primary
                          </button>
                        )}
                        <button
                          type="button"
                          className="btn btn-sm btn-outline-danger py-0 px-2 ms-auto"
                          style={{ fontSize: "11px" }}
                          onClick={() => handleDeleteResume(doc.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
        {role === "employer" && (
          <div className="glass-card mt-4">
            <p className="section-label">Company Brand</p>
            <h2 className="h5">Company Logo</h2>
            <p className="small text-secondary">
              PNG, JPG, SVG, or WEBP (Max 2 MB).
            </p>
            {envelope?.profile?.logo_path && (
              <div className="mb-3 text-center">
                <img
                  src={envelope.profile.logo_path}
                  alt="Company Logo"
                  className="img-fluid rounded border border-secondary p-2 bg-dark"
                  style={{ maxHeight: "100px" }}
                />
              </div>
            )}
            <input
              className="form-control"
              type="file"
              accept="image/png,image/jpeg,image/webp,image/svg+xml"
              onChange={async (e) => {
                const file = e.target.files?.[0];
                if (!file) return;
                const fd = new FormData();
                fd.append("file", file);
                try {
                  const doc = await apiRequest("/documents/upload-logo", {
                    method: "POST",
                    body: fd,
                  });
                  setEnvelope((prev) => ({
                    ...prev,
                    profile: { ...prev.profile, logo_path: doc.file_url },
                  }));
                  setMessage("Company logo uploaded successfully to Cloudflare R2.");
                } catch (err) {
                  setError(err.message);
                }
              }}
            />
          </div>
        )}
      </div>
    </div>
  </>;
}
