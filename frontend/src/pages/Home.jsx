import { Link } from "react-router";

export default function Home() {
  return (
    <main className="landing-page">
      <nav className="navbar navbar-dark py-4">
        <div className="container">
          <Link className="navbar-brand brand" to="/">SkillBeacon</Link>
          <div className="d-flex gap-2">
            <Link className="btn btn-outline-light" to="/login">Log in</Link>
            <Link className="btn btn-info" to="/register">Create account</Link>
          </div>
        </div>
      </nav>
      <section className="container hero-section">
        <div className="row align-items-center g-5">
          <div className="col-lg-7">
            <span className="eyebrow">Career development platform</span>
            <h1 className="display-3 fw-bold mt-3">Make your skills and career story visible.</h1>
            <p className="lead text-secondary mt-4">
              Create a role-based profile, manage your professional information,
              and prepare for opportunities, mentorship, and verified skills.
            </p>
            <div className="d-flex flex-wrap gap-3 mt-4">
              <Link className="btn btn-info btn-lg" to="/register">Build your profile</Link>
              <Link className="btn btn-outline-light btn-lg" to="/login">Open dashboard</Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}
