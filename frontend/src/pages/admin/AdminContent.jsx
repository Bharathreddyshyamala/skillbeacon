import {
  useEffect,
  useState,
} from "react";

import {
  apiRequest,
  jsonBody,
} from "../../api";


export default function AdminContent() {

  const [
    activeTab,
    setActiveTab,
  ] = useState(
    "opportunities"
  );


  const [
    opportunities,
    setOpportunities,
  ] = useState([]);


  const [
    challenges,
    setChallenges,
  ] = useState([]);


  const [
    search,
    setSearch,
  ] = useState("");


  const [
    statusFilter,
    setStatusFilter,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    updatingId,
    setUpdatingId,
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

      const params =
        new URLSearchParams();


      params.set(
        "limit",
        "100"
      );


      if (
        search.trim()
      ) {

        params.set(
          "search",
          search.trim()
        );

      }


      if (
        statusFilter
      ) {

        params.set(
          "status",
          statusFilter
        );

      }


      if (
        activeTab
        === "opportunities"
      ) {

        const response =
          await apiRequest(
            `/admin/opportunities?${params.toString()}`
          );


        setOpportunities(
          Array.isArray(
            response?.items
          )
            ? response.items
            : []
        );

      } else {

        const response =
          await apiRequest(
            `/admin/challenges?${params.toString()}`
          );


        setChallenges(
          Array.isArray(
            response?.items
          )
            ? response.items
            : []
        );

      }


    } catch (
      requestError
    ) {

      setError(
        requestError.message
        || "Unable to load moderation content."
      );

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    loadData();

  }, [
    activeTab,
  ]);


  function changeTab(
    tab,
  ) {

    setActiveTab(
      tab
    );

    setSearch("");

    setStatusFilter("");

    setError("");

    setMessage("");

  }


  async function moderateOpportunity(
    opportunity,
    newStatus,
  ) {

    const confirmed =
      window.confirm(
        newStatus === "closed"
          ? `Close "${opportunity.title}"?`
          : `Reopen "${opportunity.title}"?`
      );


    if (!confirmed) {
      return;
    }


    setUpdatingId(
      opportunity.id
    );

    setError("");
    setMessage("");


    try {

      await apiRequest(
        `/admin/opportunities/${opportunity.id}/status`,
        {
          method: "PATCH",

          body: jsonBody({
            status:
              newStatus,
          }),
        }
      );


      setMessage(
        "Opportunity moderation status updated."
      );


      await loadData();


    } catch (
      requestError
    ) {

      setError(
        requestError.message
        || "Unable to moderate opportunity."
      );

    } finally {

      setUpdatingId("");

    }
  }


  async function moderateChallenge(
    challenge,
    newStatus,
  ) {

    const confirmed =
      window.confirm(
        newStatus === "closed"
          ? `Close "${challenge.title}"?`
          : `Reopen "${challenge.title}"?`
      );


    if (!confirmed) {
      return;
    }


    setUpdatingId(
      challenge.id
    );

    setError("");
    setMessage("");


    try {

      await apiRequest(
        `/admin/challenges/${challenge.id}/status`,
        {
          method: "PATCH",

          body: jsonBody({
            status:
              newStatus,
          }),
        }
      );


      setMessage(
        "Challenge moderation status updated."
      );


      await loadData();


    } catch (
      requestError
    ) {

      setError(
        requestError.message
        || "Unable to moderate challenge."
      );

    } finally {

      setUpdatingId("");

    }
  }


  const items =
    activeTab === "opportunities"
      ? opportunities
      : challenges;


  return (
    <>

      <div className="mb-4">

        <p className="text-info fw-semibold text-uppercase">
          Administration
        </p>


        <h1 className="display-6 fw-bold">
          Content Moderation
        </h1>


        <p className="text-secondary">
          Review employer opportunities
          and challenges across SkillBeacon.
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


      {/* Tabs */}

      <div className="d-flex gap-2 mb-4">

        <button
          type="button"
          className={
            activeTab
            === "opportunities"
              ? "btn btn-info"
              : "btn btn-outline-info"
          }
          onClick={() =>
            changeTab(
              "opportunities"
            )
          }
        >
          Opportunities
        </button>


        <button
          type="button"
          className={
            activeTab
            === "challenges"
              ? "btn btn-info"
              : "btn btn-outline-info"
          }
          onClick={() =>
            changeTab(
              "challenges"
            )
          }
        >
          Challenges
        </button>

      </div>


      {/* Filters */}

      <div className="glass-card mb-4">

        <form
          className="row g-3"
          onSubmit={(event) => {

            event.preventDefault();

            loadData();

          }}
        >

          <div className="col-md-7">

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
              placeholder="Title, company, or employer email..."
            />

          </div>


          <div className="col-md-3">

            <label className="form-label">
              Status
            </label>


            <select
              className="form-select"
              value={
                statusFilter
              }
              onChange={(event) =>
                setStatusFilter(
                  event.target.value
                )
              }
            >

              <option value="">
                All Statuses
              </option>

              <option value="draft">
                Draft
              </option>

              <option value="open">
                Open
              </option>

              <option value="closed">
                Closed
              </option>

            </select>

          </div>


          <div className="col-md-2 d-flex align-items-end">

            <button
              type="submit"
              className="btn btn-info w-100"
            >
              Search
            </button>

          </div>

        </form>

      </div>


      {loading && (

        <p className="text-secondary">
          Loading content...
        </p>

      )}


      {
        !loading &&
        items.length === 0 && (

          <div className="glass-card">
            No records found.
          </div>

        )
      }


      {
        !loading &&
        items.map(
          (item) => (

            <div
              key={
                item.id
              }
              className="glass-card mb-4"
            >

              <div className="d-flex justify-content-between gap-3 flex-wrap">

                <div>

                  <h2 className="h5 mb-1">
                    {item.title}
                  </h2>


                  <p className="text-secondary mb-1">
                    {item.company_name}
                  </p>


                  <p className="small text-secondary mb-0">
                    Employer:
                    {" "}
                    {item.employer_email}
                  </p>

                </div>


                <span className="badge text-bg-info text-capitalize">

                  {item.status}

                </span>

              </div>


              {
                activeTab
                === "challenges" && (

                  <div className="mt-3">

                    <span className="badge text-bg-secondary me-2 text-capitalize">
                      {
                        item.challenge_type
                          ?.replaceAll(
                            "_",
                            " "
                          )
                      }
                    </span>


                    <span className="badge text-bg-secondary text-capitalize">
                      {item.difficulty}
                    </span>

                  </div>

                )
              }


              <p className="small text-secondary mt-3">

                Deadline:
                {" "}

                {
                  item.deadline
                  || "No deadline"
                }

              </p>


              <div className="mt-3">

                {
                  item.status
                  === "open" && (

                    <button
                      type="button"
                      className="btn btn-outline-danger btn-sm"
                      disabled={
                        updatingId
                        === item.id
                      }
                      onClick={() =>
                        activeTab
                        === "opportunities"

                          ? moderateOpportunity(
                              item,
                              "closed"
                            )

                          : moderateChallenge(
                              item,
                              "closed"
                            )
                      }
                    >
                      Close
                    </button>

                  )
                }


                {
                  item.status
                  === "closed" && (

                    <button
                      type="button"
                      className="btn btn-outline-success btn-sm"
                      disabled={
                        updatingId
                        === item.id
                      }
                      onClick={() =>
                        activeTab
                        === "opportunities"

                          ? moderateOpportunity(
                              item,
                              "open"
                            )

                          : moderateChallenge(
                              item,
                              "open"
                            )
                      }
                    >
                      Reopen
                    </button>

                  )
                }


                {
                  item.status
                  === "draft" && (

                    <span className="text-secondary small">
                      Draft content remains under employer control.
                    </span>

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