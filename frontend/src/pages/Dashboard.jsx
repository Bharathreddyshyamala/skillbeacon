import { useEffect, useState } from "react";
import { Link } from "react-router";
import { apiRequest } from "../api";
import { useAuth } from "../AuthContext";

export default function Dashboard() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    apiRequest("/profiles/me").then(setProfile).catch(() => {});
  }, []);

  return (
    <>
      <section className="glass-card mb-4">
        <span className="eyebrow">Dashboard</span>
        <h1 className="display-6 fw-bold mt-2">Welcome to SkillBeacon</h1>
        <p className="text-secondary mb-0">Signed in as {user?.email}</p>
      </section>
      <div className="row g-4">
        <div className="col-lg-7">
          <section className="glass-card h-100">
            <div className="d-flex justify-content-between align-items-start">
              <div>
                <p className="section-label">Your profile</p>
                <h2 className="h4 text-capitalize">{profile?.profile_type || user?.role} profile</h2>
              </div>
              <span className="status-pill">{profile?.profile?.is_public ? "Public" : "Private"}</span>
            </div>
            <p className="text-secondary mt-3">Complete your professional details and manage visibility.</p>
            <Link className="btn btn-info" to="/app/profile">Edit profile</Link>
          </section>
        </div>
        <div className="col-lg-5">
          <section className="glass-card h-100">
            <p className="section-label">Account</p>
            <div className="feature-row"><span>Role</span><strong className="text-capitalize">{user?.role}</strong></div>
            <div className="feature-row"><span>Status</span><strong>{user?.is_active ? "Active" : "Inactive"}</strong></div>
            <div className="feature-row"><span>Verified</span><strong>{user?.is_verified ? "Yes" : "Pending"}</strong></div>
          </section>
        </div>
      </div>
    </>
  );
}
