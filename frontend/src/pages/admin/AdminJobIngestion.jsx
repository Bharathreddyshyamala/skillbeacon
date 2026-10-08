import {
  useCallback,
  useEffect,
  useState,
} from "react";

import {
  deleteSyncedJobs,
  getJobSources,
  importJobSources,
  syncAllJobSources,
  syncJobSource,
} from "../../services/jobIngestionApi";


function formatDate(
  value
) {

  if (!value) {

    return "Never";
  }


  try {

    return new Date(
      value
    ).toLocaleString();

  } catch {

    return value;
  }
}


function statusBadge(
  status
) {

  if (
    status === "success"
  ) {

    return "bg-success";
  }


  if (
    status === "failed"
  ) {

    return "bg-danger";
  }


  if (
    status === "cleared"
  ) {

    return "bg-warning text-dark";
  }


  return "bg-secondary";
}


export default function AdminJobIngestion() {

  const [
    sources,
    setSources,
  ] = useState([]);


  const [
    selectedFile,
    setSelectedFile,
  ] = useState(null);


  const [
    importResult,
    setImportResult,
  ] = useState(null);


  const [
    syncResults,
    setSyncResults,
  ] = useState([]);


  const [
    loadingSources,
    setLoadingSources,
  ] = useState(true);


  const [
    uploading,
    setUploading,
  ] = useState(false);


  const [
    syncingAll,
    setSyncingAll,
  ] = useState(false);


  const [
    syncingSourceId,
    setSyncingSourceId,
  ] = useState(null);


  /*
   * NEW
   *
   * Stores the ID of the source
   * whose jobs are currently
   * being deleted.
   */
  const [
    deletingSourceId,
    setDeletingSourceId,
  ] = useState(null);


  const [
    error,
    setError,
  ] = useState("");


  const [
    message,
    setMessage,
  ] = useState("");


  /*
   * ==================================================
   * LOAD SOURCES
   * ==================================================
   */

  const loadSources =
    useCallback(

      async () => {

        try {

          setLoadingSources(
            true
          );

          setError("");


          const data =
            await getJobSources();


          setSources(

            Array.isArray(data)
              ? data
              : []

          );


        } catch (
          requestError
        ) {

          console.error(
            requestError
          );


          setError(
            requestError.message
            ||
            "Failed to load job sources."
          );


        } finally {

          setLoadingSources(
            false
          );
        }
      },

      []

    );


  useEffect(
    () => {

      loadSources();

    },
    [
      loadSources
    ]
  );


  /*
   * ==================================================
   * EXCEL IMPORT
   * ==================================================
   */

  async function handleUpload(
    event
  ) {

    event.preventDefault();


    setError("");

    setMessage("");

    setImportResult(null);


    if (!selectedFile) {

      setError(
        "Please select an Excel file."
      );

      return;
    }


    if (
      !selectedFile.name
        .toLowerCase()
        .endsWith(".xlsx")
    ) {

      setError(
        "Only .xlsx files are supported."
      );

      return;
    }


    try {

      setUploading(true);


      const result =
        await importJobSources(
          selectedFile
        );


      setImportResult(
        result
      );


      setMessage(
        "Job sources imported successfully."
      );


      setSelectedFile(
        null
      );


      const input =
        document.getElementById(
          "job-source-file"
        );


      if (input) {

        input.value = "";
      }


      await loadSources();


    } catch (
      requestError
    ) {

      console.error(
        requestError
      );


      setError(
        requestError.message
        ||
        "Failed to import job sources."
      );


    } finally {

      setUploading(false);
    }
  }


  /*
   * ==================================================
   * SYNC ONE SOURCE
   * ==================================================
   */

  async function handleSyncOne(
    source
  ) {

    setError("");

    setMessage("");


    try {

      setSyncingSourceId(
        source.id
      );


      const result =
        await syncJobSource(
          source.id
        );


      setSyncResults(
        previous => [

          result,

          ...previous.filter(
            item =>
              item.source_id
              !== result.source_id
          ),

        ]
      );


      if (
        result.status
        === "success"
      ) {

        setMessage(
          `${source.company_name} synced successfully.`
        );

      } else {

        setError(
          `${source.company_name} sync failed: ${
            result.error
            || "Unknown error"
          }`
        );
      }


      await loadSources();


    } catch (
      requestError
    ) {

      console.error(
        requestError
      );


      setError(
        requestError.message
        ||
        `Failed to sync ${source.company_name}.`
      );


    } finally {

      setSyncingSourceId(
        null
      );
    }
  }


  /*
   * ==================================================
   * SYNC ALL SOURCES
   * ==================================================
   */

  async function handleSyncAll() {

    setError("");

    setMessage("");

    setSyncResults([]);


    try {

      setSyncingAll(
        true
      );


      const response =
        await syncAllJobSources();


      const results =
        response.results
        || [];


      setSyncResults(
        results
      );


      const successful =
        results.filter(
          item =>
            item.status
            === "success"
        ).length;


      const failed =
        results.filter(
          item =>
            item.status
            === "failed"
        ).length;


      setMessage(
        (
          `Sync completed. `
          +
          `${successful} successful, `
          +
          `${failed} failed.`
        )
      );


      await loadSources();


    } catch (
      requestError
    ) {

      console.error(
        requestError
      );


      setError(
        requestError.message
        ||
        "Failed to sync job sources."
      );


    } finally {

      setSyncingAll(
        false
      );
    }
  }


  /*
   * ==================================================
   * NEW
   * DELETE SYNCHRONIZED JOBS
   * ==================================================
   */

  async function handleDeleteJobs(
    source
  ) {

    setError("");

    setMessage("");


    const jobCount =
      source.synced_job_count
      || 0;


    /*
     * Important:
     *
     * Require admin confirmation before
     * permanently deleting imported jobs.
     */

    const confirmed =
      window.confirm(

        (
          `Delete all ${jobCount} synced jobs `
          +
          `from ${source.company_name}?\n\n`
          +
          `These jobs will immediately disappear `
          +
          `from the student Opportunities page.\n\n`
          +
          `${source.company_name} will remain as `
          +
          `a configured job source and can be `
          +
          `synchronized again later.`
        )

      );


    if (!confirmed) {

      return;
    }


    try {

      setDeletingSourceId(
        source.id
      );


      const result =
        await deleteSyncedJobs(
          source.id
        );


      setMessage(
        result.message
        ||
        (
          `Deleted synchronized jobs `
          +
          `from ${source.company_name}.`
        )
      );


      /*
       * Remove any old sync result
       * displayed for this source.
       */

      setSyncResults(
        previous =>
          previous.filter(
            item =>
              item.source_id
              !== source.id
          )
      );


      /*
       * Reload source list.
       *
       * synced_job_count should become 0.
       */

      await loadSources();


    } catch (
      requestError
    ) {

      console.error(
        "Delete synced jobs failed:",
        requestError
      );


      setError(
        requestError.message
        ||
        (
          `Unable to delete synced jobs `
          +
          `from ${source.company_name}.`
        )
      );


    } finally {

      setDeletingSourceId(
        null
      );
    }
  }


  /*
   * ==================================================
   * UI
   * ==================================================
   */

  return (

    <div className="container-fluid py-4">


      {/* HEADER */}

      <div
        className="
          d-flex
          justify-content-between
          align-items-center
          flex-wrap
          gap-3
          mb-4
        "
      >

        <div>

          <h2 className="mb-1">
            Job Ingestion
          </h2>


          <p className="text-muted mb-0">

            Import company career
            sources and synchronize
            external jobs.

          </p>

        </div>


        <button
          type="button"
          className="btn btn-primary"
          onClick={
            handleSyncAll
          }
          disabled={
            syncingAll
            ||
            deletingSourceId
            !== null
            ||
            sources.length === 0
          }
        >

          {
            syncingAll
              ? "Syncing..."
              : "Sync All Sources"
          }

        </button>

      </div>


      {/* ERROR */}

      {error && (

        <div
          className="
            alert
            alert-danger
          "
        >

          {error}

        </div>

      )}


      {/* SUCCESS */}

      {message && (

        <div
          className="
            alert
            alert-success
          "
        >

          {message}

        </div>

      )}


      {/* ================================================= */}
      {/* IMPORT EXCEL */}
      {/* ================================================= */}

      <div
        className="
          card
          shadow-sm
          mb-4
        "
      >

        <div className="card-body">

          <h5 className="card-title">
            Import Job Sources
          </h5>


          <p className="text-muted">

            Upload an Excel file
            containing Amazon,
            Microsoft, Greenhouse,
            Lever, or other supported
            job sources.

          </p>


          <form
            onSubmit={
              handleUpload
            }
          >

            <div
              className="
                row
                g-3
                align-items-end
              "
            >


              <div className="col-md-8">

                <label
                  htmlFor="job-source-file"
                  className="form-label"
                >

                  Job Sources Excel

                </label>


                <input
                  id="job-source-file"
                  type="file"
                  className="form-control"
                  accept=".xlsx"
                  onChange={
                    event =>
                      setSelectedFile(
                        event.target
                          .files?.[0]
                        || null
                      )
                  }
                />

              </div>


              <div className="col-md-4">

                <button
                  type="submit"
                  className="
                    btn
                    btn-success
                    w-100
                  "
                  disabled={
                    uploading
                  }
                >

                  {
                    uploading
                      ? "Uploading..."
                      : "Import Excel"
                  }

                </button>

              </div>

            </div>

          </form>

        </div>

      </div>


      {/* ================================================= */}
      {/* IMPORT RESULT */}
      {/* ================================================= */}

      {importResult && (

        <div
          className="
            card
            shadow-sm
            mb-4
          "
        >

          <div className="card-body">

            <h5>
              Import Result
            </h5>


            <div className="row g-3">


              <div className="col-md-3">

                <div
                  className="
                    border
                    rounded
                    p-3
                  "
                >

                  <div className="text-muted">
                    Created
                  </div>

                  <strong>
                    {
                      importResult.created
                    }
                  </strong>

                </div>

              </div>


              <div className="col-md-3">

                <div
                  className="
                    border
                    rounded
                    p-3
                  "
                >

                  <div className="text-muted">
                    Updated
                  </div>

                  <strong>
                    {
                      importResult.updated
                    }
                  </strong>

                </div>

              </div>


              <div className="col-md-3">

                <div
                  className="
                    border
                    rounded
                    p-3
                  "
                >

                  <div className="text-muted">
                    Skipped
                  </div>

                  <strong>
                    {
                      importResult.skipped
                    }
                  </strong>

                </div>

              </div>


              <div className="col-md-3">

                <div
                  className="
                    border
                    rounded
                    p-3
                  "
                >

                  <div className="text-muted">
                    Errors
                  </div>

                  <strong>

                    {
                      importResult
                        .errors
                        ?.length
                      || 0
                    }

                  </strong>

                </div>

              </div>

            </div>


            {
              importResult
                .errors
                ?.length > 0 && (

                <div className="mt-3">

                  <h6>
                    Import Errors
                  </h6>


                  <ul className="mb-0">

                    {
                      importResult
                        .errors
                        .map(
                          (
                            item,
                            index
                          ) => (

                            <li
                              key={
                                index
                              }
                            >

                              Row {
                                item.row
                              }: {
                                item.error
                              }

                            </li>

                          )
                        )
                    }

                  </ul>

                </div>

              )
            }

          </div>

        </div>

      )}


      {/* ================================================= */}
      {/* SOURCES TABLE */}
      {/* ================================================= */}

      <div
        className="
          card
          shadow-sm
        "
      >

        <div
          className="
            card-header
            d-flex
            justify-content-between
            align-items-center
          "
        >

          <strong>
            Configured Job Sources
          </strong>


          <button
            type="button"
            className="
              btn
              btn-sm
              btn-outline-secondary
            "
            onClick={
              loadSources
            }
            disabled={
              loadingSources
            }
          >

            Refresh

          </button>

        </div>


        <div
          className="
            card-body
            p-0
          "
        >


          {loadingSources ? (

            <div className="p-4">

              Loading job sources...

            </div>

          ) : sources.length === 0 ? (

            <div
              className="
                p-4
                text-muted
              "
            >

              No job sources configured.
              Upload an Excel file first.

            </div>

          ) : (

            <div className="table-responsive">

              <table
                className="
                  table
                  table-hover
                  align-middle
                  mb-0
                "
              >


                <thead>

                  <tr>

                    <th>
                      Company
                    </th>

                    <th>
                      Connector
                    </th>

                    <th>
                      Key
                    </th>

                    {/* NEW */}
                    <th>
                      Jobs
                    </th>

                    <th>
                      Active
                    </th>

                    <th>
                      Last Sync
                    </th>

                    <th>
                      Status
                    </th>

                    <th>
                      Actions
                    </th>

                  </tr>

                </thead>


                <tbody>

                  {
                    sources.map(
                      source => (

                        <tr
                          key={
                            source.id
                          }
                        >


                          {/* COMPANY */}

                          <td>

                            <div className="fw-semibold">

                              {
                                source
                                  .company_name
                              }

                            </div>


                            <a
                              href={
                                source
                                  .careers_url
                              }
                              target="_blank"
                              rel="noreferrer"
                              className="small"
                            >

                              Career Site

                            </a>

                          </td>


                          {/* CONNECTOR */}

                          <td>

                            <span
                              className="
                                badge
                                bg-dark
                              "
                            >

                              {
                                source
                                  .connector_type
                              }

                            </span>

                          </td>


                          {/* CONNECTOR KEY */}

                          <td>

                            {
                              source
                                .connector_key
                              || "-"
                            }

                          </td>


                          {/* NEW JOB COUNT */}

                          <td>

                            <span
                              className="
                                badge
                                rounded-pill
                                text-bg-secondary
                              "
                            >

                              {
                                source
                                  .synced_job_count
                                ?? 0
                              }

                            </span>

                          </td>


                          {/* ACTIVE */}

                          <td>

                            {
                              source
                                .is_active
                                ? (

                                  <span
                                    className="
                                      badge
                                      bg-success
                                    "
                                  >

                                    Active

                                  </span>

                                )
                                : (

                                  <span
                                    className="
                                      badge
                                      bg-secondary
                                    "
                                  >

                                    Disabled

                                  </span>

                                )
                            }

                          </td>


                          {/* LAST SYNC */}

                          <td>

                            {
                              formatDate(
                                source
                                  .last_synced_at
                              )
                            }

                          </td>


                          {/* STATUS */}

                          <td>

                            {
                              source
                                .last_sync_status
                                ? (

                                  <>

                                    <span
                                      className={
                                        `badge ${
                                          statusBadge(
                                            source
                                              .last_sync_status
                                          )
                                        }`
                                      }
                                    >

                                      {
                                        source
                                          .last_sync_status
                                      }

                                    </span>


                                    {
                                      source
                                        .last_sync_error
                                        && (

                                        <div
                                          className="
                                            small
                                            text-danger
                                            mt-1
                                          "
                                          title={
                                            source
                                              .last_sync_error
                                          }
                                        >

                                          {
                                            source
                                              .last_sync_error
                                              .substring(
                                                0,
                                                80
                                              )
                                          }

                                        </div>

                                      )
                                    }

                                  </>

                                )
                                : "-"
                            }

                          </td>


                          {/* ACTIONS */}

                          <td>

                            <div
                              className="
                                d-flex
                                flex-wrap
                                gap-2
                              "
                            >


                              {/* SYNC */}

                              <button
                                type="button"
                                className="
                                  btn
                                  btn-sm
                                  btn-outline-primary
                                "
                                onClick={
                                  () =>
                                    handleSyncOne(
                                      source
                                    )
                                }
                                disabled={
                                  syncingAll
                                  ||
                                  syncingSourceId
                                  === source.id
                                  ||
                                  deletingSourceId
                                  === source.id
                                  ||
                                  !source
                                    .is_active
                                }
                              >

                                {
                                  syncingSourceId
                                  === source.id
                                    ? "Syncing..."
                                    : "Sync"
                                }

                              </button>


                              {/* NEW DELETE JOBS BUTTON */}

                              <button
                                type="button"
                                className="
                                  btn
                                  btn-sm
                                  btn-outline-danger
                                "
                                onClick={
                                  () =>
                                    handleDeleteJobs(
                                      source
                                    )
                                }
                                disabled={
                                  syncingAll
                                  ||
                                  syncingSourceId
                                  === source.id
                                  ||
                                  deletingSourceId
                                  === source.id
                                  ||
                                  (
                                    source
                                      .synced_job_count
                                    || 0
                                  ) === 0
                                }
                              >

                                {
                                  deletingSourceId
                                  === source.id
                                    ? "Deleting..."
                                    : "Delete Jobs"
                                }

                              </button>

                            </div>

                          </td>

                        </tr>

                      )
                    )
                  }

                </tbody>

              </table>

            </div>

          )}

        </div>

      </div>


      {/* ================================================= */}
      {/* LATEST SYNC RESULTS */}
      {/* ================================================= */}

      {
        syncResults.length > 0 && (

          <div
            className="
              card
              shadow-sm
              mt-4
            "
          >

            <div className="card-body">

              <h5>
                Latest Sync Results
              </h5>


              <div className="table-responsive">

                <table className="table">

                  <thead>

                    <tr>

                      <th>
                        Company
                      </th>

                      <th>
                        Status
                      </th>

                      <th>
                        Fetched
                      </th>

                      <th>
                        Created
                      </th>

                      <th>
                        Updated
                      </th>

                      <th>
                        Deactivated
                      </th>

                      <th>
                        Complete
                      </th>

                    </tr>

                  </thead>


                  <tbody>

                    {
                      syncResults.map(
                        (
                          result,
                          index
                        ) => (

                          <tr
                            key={
                              result
                                .source_id
                              || index
                            }
                          >


                            <td>

                              {
                                result.company
                                || "-"
                              }

                            </td>


                            <td>

                              <span
                                className={
                                  `badge ${
                                    statusBadge(
                                      result.status
                                    )
                                  }`
                                }
                              >

                                {
                                  result.status
                                }

                              </span>


                              {
                                result.error
                                && (

                                  <div
                                    className="
                                      small
                                      text-danger
                                      mt-1
                                    "
                                  >

                                    {
                                      result.error
                                    }

                                  </div>

                                )
                              }

                            </td>


                            <td>

                              {
                                result.fetched
                                ?? "-"
                              }

                            </td>


                            <td>

                              {
                                result.created
                                ?? "-"
                              }

                            </td>


                            <td>

                              {
                                result.updated
                                ?? "-"
                              }

                            </td>


                            <td>

                              {
                                result.deactivated
                                ?? "-"
                              }

                            </td>


                            <td>

                              {
                                result.complete
                                === true
                                  ? "Yes"
                                  : result.complete
                                    === false
                                      ? "No"
                                      : "-"
                              }

                            </td>

                          </tr>

                        )
                      )
                    }

                  </tbody>

                </table>

              </div>

            </div>

          </div>

        )
      }

    </div>
  );
}