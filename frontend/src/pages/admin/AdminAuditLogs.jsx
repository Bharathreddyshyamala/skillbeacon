import {
  useEffect,
  useState,
} from "react";

import {
  apiRequest,
} from "../../api";


export default function AdminAuditLogs() {

  const [
    items,
    setItems,
  ] = useState([]);


  const [
    action,
    setAction,
  ] = useState("");


  const [
    targetType,
    setTargetType,
  ] = useState("");


  const [
    loading,
    setLoading,
  ] = useState(true);


  const [
    error,
    setError,
  ] = useState("");


  async function loadLogs() {

    setLoading(true);

    setError("");


    try {

      const params =
        new URLSearchParams();


      params.set(
        "limit",
        "100"
      );


      if (action) {

        params.set(
          "action",
          action
        );

      }


      if (targetType) {

        params.set(
          "target_type",
          targetType
        );

      }


      const response =
        await apiRequest(
          `/admin/audit-logs?${params.toString()}`
        );


      setItems(
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
        || "Unable to load audit logs."
      );

    } finally {

      setLoading(false);

    }
  }


  useEffect(() => {

    loadLogs();

  }, []);


  return (
    <>

      <div className="mb-4">

        <p className="text-info fw-semibold text-uppercase">
          Administration
        </p>


        <h1 className="display-6 fw-bold">
          Audit Logs
        </h1>


        <p className="text-secondary">
          Review important administrative
          actions performed on SkillBeacon.
        </p>

      </div>


      {error && (

        <div className="alert alert-danger">
          {error}
        </div>

      )}


      <div className="glass-card mb-4">

        <form
          className="row g-3"
          onSubmit={(event) => {

            event.preventDefault();

            loadLogs();

          }}
        >

          <div className="col-md-5">

            <label className="form-label">
              Action
            </label>


            <select
              className="form-select"
              value={action}
              onChange={(event) =>
                setAction(
                  event.target.value
                )
              }
            >

              <option value="">
                All Actions
              </option>

              <option value="activate_user">
                Activate User
              </option>

              <option value="deactivate_user">
                Deactivate User
              </option>

              <option value="verify_user">
                Verify User
              </option>

              <option value="unverify_user">
                Unverify User
              </option>

              <option value="close_opportunity">
                Close Opportunity
              </option>

              <option value="reopen_opportunity">
                Reopen Opportunity
              </option>

              <option value="close_challenge">
                Close Challenge
              </option>

              <option value="reopen_challenge">
                Reopen Challenge
              </option>

            </select>

          </div>


          <div className="col-md-5">

            <label className="form-label">
              Target Type
            </label>


            <select
              className="form-select"
              value={
                targetType
              }
              onChange={(event) =>
                setTargetType(
                  event.target.value
                )
              }
            >

              <option value="">
                All
              </option>

              <option value="user">
                User
              </option>

              <option value="opportunity">
                Opportunity
              </option>

              <option value="challenge">
                Challenge
              </option>

            </select>

          </div>


          <div className="col-md-2 d-flex align-items-end">

            <button
              type="submit"
              className="btn btn-info w-100"
            >
              Filter
            </button>

          </div>

        </form>

      </div>


      {loading && (

        <p className="text-secondary">
          Loading audit logs...
        </p>

      )}


      {
        !loading &&
        items.length === 0 && (

          <div className="glass-card">
            No audit logs found.
          </div>

        )
      }


      {
        !loading &&
        items.length > 0 && (

          <div className="glass-card overflow-auto">

            <table className="table table-dark table-hover align-middle mb-0">

              <thead>

                <tr>

                  <th>
                    Date
                  </th>

                  <th>
                    Admin
                  </th>

                  <th>
                    Action
                  </th>

                  <th>
                    Target
                  </th>

                  <th>
                    Details
                  </th>

                </tr>

              </thead>


              <tbody>

                {items.map(
                  (item) => (

                    <tr
                      key={
                        item.id
                      }
                    >

                      <td>

                        {
                          new Date(
                            item.created_at
                          ).toLocaleString()
                        }

                      </td>


                      <td>
                        {item.admin_email}
                      </td>


                      <td>

                        <span className="badge text-bg-info">

                          {
                            item.action
                              .replaceAll(
                                "_",
                                " "
                              )
                          }

                        </span>

                      </td>


                      <td>

                        <div className="text-capitalize">
                          {item.target_type}
                        </div>


                        <div className="small text-secondary">
                          {item.target_id}
                        </div>

                      </td>


                      <td>

                        <pre className="small mb-0 text-light">
                          {
                            JSON.stringify(
                              item.details,
                              null,
                              2
                            )
                          }
                        </pre>

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