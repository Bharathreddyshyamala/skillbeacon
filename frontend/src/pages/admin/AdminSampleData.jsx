import {
  useEffect,
  useState,
} from "react";

import {
  apiRequest,
} from "../../api";


export default function AdminSampleData() {
  const [
    file,
    setFile,
  ] = useState(null);

  const [
    preview,
    setPreview,
  ] = useState(null);

  const [
    batches,
    setBatches,
  ] = useState([]);

  const [
    loading,
    setLoading,
  ] = useState(false);

  const [
    error,
    setError,
  ] = useState("");

  const [
    message,
    setMessage,
  ] = useState("");


  async function loadBatches() {
    try {
      const response =
        await apiRequest(
          "/admin/sample-data/batches"
        );

      setBatches(
        response?.items || []
      );

    } catch (requestError) {
      setError(
        requestError.message ||
        "Unable to load batches."
      );
    }
  }


  useEffect(() => {
    loadBatches();
  }, []);


  async function previewFile() {
    if (!file) {
      setError(
        "Select an Excel file."
      );

      return;
    }

    setLoading(true);
    setError("");
    setMessage("");
    setPreview(null);

    try {
      const form =
        new FormData();

      form.append(
        "file",
        file
      );

      const response =
        await apiRequest(
          "/admin/sample-data/preview",
          {
            method: "POST",
            body: form,
          }
        );

      setPreview(
        response
      );

    } catch (requestError) {
      setError(
        requestError.message ||
        "Preview failed."
      );

    } finally {
      setLoading(false);
    }
  }


  async function importFile() {
    if (
      !file ||
      !preview?.valid
    ) {
      setError(
        "Preview the file and resolve all errors first."
      );

      return;
    }

    const confirmed =
      window.confirm(
        "Import this sample dataset?"
      );

    if (!confirmed) {
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const form =
        new FormData();

      form.append(
        "file",
        file
      );

      const response =
        await apiRequest(
          "/admin/sample-data/import",
          {
            method: "POST",
            body: form,
          }
        );

      setMessage(
        response.message ||
        "Sample data imported."
      );

      setPreview(null);

      await loadBatches();

    } catch (requestError) {
      setError(
        requestError.message ||
        "Import failed."
      );

    } finally {
      setLoading(false);
    }
  }


  async function deleteBatch(
    batch
  ) {
    const confirmation =
      window.prompt(
        "Type DELETE SAMPLE DATA to remove this batch."
      );

    if (
      confirmation !==
      "DELETE SAMPLE DATA"
    ) {
      return;
    }

    setLoading(true);
    setError("");
    setMessage("");

    try {
      const response =
        await apiRequest(
          `/admin/sample-data/batches/${batch.id}`,
          {
            method: "DELETE",
          }
        );

      setMessage(
        `Deleted ${response.deleted_records} database records and ${response.deleted_objects} R2 objects.`
      );

      await loadBatches();

    } catch (requestError) {
      setError(
        requestError.message ||
        "Delete failed."
      );

    } finally {
      setLoading(false);
    }
  }


  return (
    <div>

      <div
        className={
          "d-flex justify-content-between " +
          "align-items-center mb-4"
        }
      >

        <div>
          <h1 className="h3 mb-1">
            Sample Data
          </h1>

          <p className="text-secondary mb-0">
            Import and safely remove SkillBeacon
            sample datasets.
          </p>
        </div>

        <a
          className="btn btn-outline-info"
          href="/SkillBeacon_Sample_Data_Template.xlsx"
          download
        >
          Download Template
        </a>

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


      <div
        className={
          "card bg-dark " +
          "border-secondary mb-4"
        }
      >

        <div className="card-body">

          <h2 className="h5">
            Import Excel
          </h2>

          <input
            className="form-control mb-3"
            type="file"
            accept=".xlsx"
            onChange={(event) => {
              setFile(
                event.target.files?.[0] ||
                null
              );

              setPreview(null);
            }}
          />

          <div className="d-flex gap-2">

            <button
              type="button"
              className="btn btn-outline-light"
              disabled={
                loading ||
                !file
              }
              onClick={
                previewFile
              }
            >
              Preview
            </button>

            <button
              type="button"
              className="btn btn-primary"
              disabled={
                loading ||
                !preview?.valid
              }
              onClick={
                importFile
              }
            >
              Import Sample Data
            </button>

          </div>

        </div>

      </div>


      {preview && (
        <div
          className={
            "card bg-dark " +
            "border-secondary mb-4"
          }
        >

          <div className="card-body">

            <h2 className="h5">
              Preview
            </h2>

            <p>
              Status:{" "}

              <strong
                className={
                  preview.valid
                    ? "text-success"
                    : "text-danger"
                }
              >
                {
                  preview.valid
                    ? "Valid"
                    : "Invalid"
                }
              </strong>
            </p>


            <div className="row g-2">

              {
                Object.entries(
                  preview.row_counts ||
                  {}
                ).map(
                  ([name, count]) => (
                    <div
                      className="col-md-3"
                      key={name}
                    >

                      <div
                        className={
                          "border rounded " +
                          "p-2"
                        }
                      >

                        <div
                          className={
                            "small " +
                            "text-secondary"
                          }
                        >
                          {name}
                        </div>

                        <strong>
                          {count}
                        </strong>

                      </div>

                    </div>
                  )
                )
              }

            </div>


            {
              preview.errors?.length >
              0 && (
                <div
                  className={
                    "table-responsive " +
                    "mt-3"
                  }
                >

                  <table
                    className={
                      "table table-dark " +
                      "table-sm"
                    }
                  >

                    <thead>
                      <tr>
                        <th>Sheet</th>
                        <th>Row</th>
                        <th>Field</th>
                        <th>Error</th>
                      </tr>
                    </thead>

                    <tbody>

                      {
                        preview.errors.map(
                          (
                            item,
                            index
                          ) => (
                            <tr key={index}>

                              <td>
                                {item.sheet}
                              </td>

                              <td>
                                {item.row || "-"}
                              </td>

                              <td>
                                {item.field || "-"}
                              </td>

                              <td>
                                {item.message}
                              </td>

                            </tr>
                          )
                        )
                      }

                    </tbody>

                  </table>

                </div>
              )
            }

          </div>

        </div>
      )}


      <div
        className={
          "card bg-dark " +
          "border-secondary"
        }
      >

        <div className="card-body">

          <h2 className="h5 mb-3">
            Import History
          </h2>

          <div className="table-responsive">

            <table
              className={
                "table table-dark " +
                "align-middle"
              }
            >

              <thead>
                <tr>
                  <th>File</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Records</th>
                  <th />
                </tr>
              </thead>

              <tbody>

                {
                  batches.map(
                    (batch) => {

                      const total =
                        Object.values(
                          batch.row_counts ||
                          {}
                        ).reduce(
                          (
                            sum,
                            count
                          ) =>
                            sum +
                            Number(count),
                          0
                        );

                      return (
                        <tr key={batch.id}>

                          <td>
                            {
                              batch
                                .source_filename
                            }
                          </td>

                          <td>
                            <span
                              className={
                                "badge " +
                                "bg-secondary"
                              }
                            >
                              {batch.status}
                            </span>
                          </td>

                          <td>
                            {
                              new Date(
                                batch.created_at
                              )
                                .toLocaleString()
                            }
                          </td>

                          <td>
                            {total}
                          </td>

                          <td className="text-end">

                            {
                              (
                                batch.status ===
                                  "completed" ||
                                batch.status ===
                                  "deleted_with_storage_errors"
                              ) && (
                                <button
                                  type="button"
                                  className={
                                    "btn " +
                                    "btn-outline-danger " +
                                    "btn-sm"
                                  }
                                  disabled={
                                    loading
                                  }
                                  onClick={
                                    () =>
                                      deleteBatch(
                                        batch
                                      )
                                  }
                                >
                                  Delete Sample Data
                                </button>
                              )
                            }

                          </td>

                        </tr>
                      );
                    }
                  )
                }

              </tbody>

            </table>

          </div>

        </div>

      </div>

    </div>
  );
}