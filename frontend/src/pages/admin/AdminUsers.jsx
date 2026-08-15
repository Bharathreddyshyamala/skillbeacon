import {
  useEffect,
  useState,
} from "react";

import {
  apiRequest,
  jsonBody,
} from "../../api";


export default function AdminUsers() {

  const [
    users,
    setUsers,
  ] = useState([]);


  const [
    search,
    setSearch,
  ] = useState("");


  const [
    role,
    setRole,
  ] = useState("");


  const [
    activeFilter,
    setActiveFilter,
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


  async function loadUsers() {

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


      if (role) {

        params.set(
          "role",
          role
        );

      }


      if (
        activeFilter
        !== ""
      ) {

        params.set(
          "is_active",
          activeFilter
        );

      }


      const response =
        await apiRequest(
          `/admin/users?${params.toString()}`
        );


      setUsers(
        Array.isArray(
          response?.items
        )
          ? response.items
          : []
      );


    } catch (
      requestError
    ) {

      setError(
        requestError.message
        || "Unable to load users."
      );

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    loadUsers();

  }, []);


  async function changeActiveStatus(
    user,
  ) {

    const newStatus =
      !user.is_active;


    const confirmed =
      window.confirm(
        newStatus
          ? `Reactivate ${user.email}?`
          : `Deactivate ${user.email}?`
      );


    if (!confirmed) {
      return;
    }


    setUpdatingId(
      user.id
    );

    setError("");
    setMessage("");


    try {

      await apiRequest(
        `/admin/users/${user.id}/status`,
        {
          method: "PATCH",

          body: jsonBody({
            is_active:
              newStatus,
          }),
        }
      );


      setMessage(
        newStatus
          ? "User reactivated successfully."
          : "User deactivated successfully."
      );


      await loadUsers();


    } catch (
      requestError
    ) {

      setError(
        requestError.message
        || "Unable to update user."
      );

    } finally {

      setUpdatingId("");

    }
  }


  async function changeVerification(
    user,
  ) {

    const newStatus =
      !user.is_verified;


    const confirmed =
      window.confirm(
        newStatus
          ? `Verify ${user.email}?`
          : `Remove verification from ${user.email}?`
      );


    if (!confirmed) {
      return;
    }


    setUpdatingId(
      user.id
    );

    setError("");
    setMessage("");


    try {

      await apiRequest(
        `/admin/users/${user.id}/verification`,
        {
          method: "PATCH",

          body: jsonBody({
            is_verified:
              newStatus,
          }),
        }
      );


      setMessage(
        newStatus
          ? "User verified successfully."
          : "Verification removed successfully."
      );


      await loadUsers();


    } catch (
      requestError
    ) {

      setError(
        requestError.message
        || "Unable to update verification."
      );

    } finally {

      setUpdatingId("");

    }
  }


  function clearFilters() {

    setSearch("");

    setRole("");

    setActiveFilter("");

  }


  return (
    <>

      <div className="mb-4">

        <p className="text-info fw-semibold text-uppercase">
          Administration
        </p>


        <h1 className="display-6 fw-bold">
          User Management
        </h1>


        <p className="text-secondary">
          Search, verify, activate,
          and deactivate platform users.
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


      {/* ===================================================
          FILTERS
      ==================================================== */}

      <div className="glass-card mb-4">

        <form
          className="row g-3"
          onSubmit={(event) => {

            event.preventDefault();

            loadUsers();

          }}
        >

          <div className="col-md-5">

            <label className="form-label">
              Search Email
            </label>


            <input
              className="form-control"
              value={search}
              onChange={(event) =>
                setSearch(
                  event.target.value
                )
              }
              placeholder="student@example.com"
            />

          </div>


          <div className="col-md-3">

            <label className="form-label">
              Role
            </label>


            <select
              className="form-select"
              value={role}
              onChange={(event) =>
                setRole(
                  event.target.value
                )
              }
            >

              <option value="">
                All Roles
              </option>

              <option value="student">
                Student
              </option>

              <option value="mentor">
                Mentor
              </option>

              <option value="employer">
                Employer
              </option>

              <option value="admin">
                Admin
              </option>

            </select>

          </div>


          <div className="col-md-2">

            <label className="form-label">
              Status
            </label>


            <select
              className="form-select"
              value={
                activeFilter
              }
              onChange={(event) =>
                setActiveFilter(
                  event.target.value
                )
              }
            >

              <option value="">
                All
              </option>

              <option value="true">
                Active
              </option>

              <option value="false">
                Inactive
              </option>

            </select>

          </div>


          <div className="col-md-2 d-flex align-items-end gap-2">

            <button
              type="submit"
              className="btn btn-info"
            >
              Search
            </button>


            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={() => {

                clearFilters();

                setTimeout(
                  loadUsers,
                  0
                );

              }}
            >
              Clear
            </button>

          </div>

        </form>

      </div>


      {loading && (

        <p className="text-secondary">
          Loading users...
        </p>

      )}


      {
        !loading &&
        users.length === 0 && (

          <div className="glass-card">
            No users found.
          </div>

        )
      }


      {
        !loading &&
        users.length > 0 && (

          <div className="glass-card overflow-auto">

            <table className="table table-dark table-hover align-middle mb-0">

              <thead>

                <tr>

                  <th>
                    Email
                  </th>

                  <th>
                    Role
                  </th>

                  <th>
                    Active
                  </th>

                  <th>
                    Verified
                  </th>

                  <th>
                    Created
                  </th>

                  <th>
                    Actions
                  </th>

                </tr>

              </thead>


              <tbody>

                {users.map(
                  (user) => (

                    <tr
                      key={
                        user.id
                      }
                    >

                      <td>
                        {user.email}
                      </td>


                      <td className="text-capitalize">
                        {user.role}
                      </td>


                      <td>

                        <span
                          className={
                            `badge ${
                              user.is_active
                                ? "text-bg-success"
                                : "text-bg-danger"
                            }`
                          }
                        >

                          {
                            user.is_active
                              ? "Active"
                              : "Inactive"
                          }

                        </span>

                      </td>


                      <td>

                        <span
                          className={
                            `badge ${
                              user.is_verified
                                ? "text-bg-info"
                                : "text-bg-secondary"
                            }`
                          }
                        >

                          {
                            user.is_verified
                              ? "Verified"
                              : "Unverified"
                          }

                        </span>

                      </td>


                      <td>

                        {
                          new Date(
                            user.created_at
                          ).toLocaleDateString()
                        }

                      </td>


                      <td>

                        {
                          user.role
                          === "admin" ? (

                            <span className="text-secondary small">
                              Protected Admin
                            </span>

                          ) : (

                            <div className="d-flex gap-2 flex-wrap">

                              <button
                                type="button"
                                className={
                                  user.is_active
                                    ? "btn btn-outline-danger btn-sm"
                                    : "btn btn-outline-success btn-sm"
                                }
                                disabled={
                                  updatingId
                                  === user.id
                                }
                                onClick={() =>
                                  changeActiveStatus(
                                    user
                                  )
                                }
                              >

                                {
                                  user.is_active
                                    ? "Deactivate"
                                    : "Activate"
                                }

                              </button>


                              <button
                                type="button"
                                className="btn btn-outline-info btn-sm"
                                disabled={
                                  updatingId
                                  === user.id
                                }
                                onClick={() =>
                                  changeVerification(
                                    user
                                  )
                                }
                              >

                                {
                                  user.is_verified
                                    ? "Unverify"
                                    : "Verify"
                                }

                              </button>

                            </div>

                          )
                        }

                      </td>

                    </tr>

                  )
                )}

              </tbody>

            </table>

          </div>

        )
      }

    </>
  );
}