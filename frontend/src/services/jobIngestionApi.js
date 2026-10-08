import {
  apiRequest,
} from "../api";


/*
 * Get every configured
 * external job source.
 */
export function getJobSources() {

  return apiRequest(
    "/admin/job-ingestion/sources"
  );
}


/*
 * Upload job_sources.xlsx.
 */
export function importJobSources(
  file
) {

  const formData =
    new FormData();


  formData.append(
    "file",
    file
  );


  return apiRequest(
    "/admin/job-ingestion/sources/import",
    {
      method: "POST",
      body: formData,
    }
  );
}


/*
 * Sync every ACTIVE source.
 */
export function syncAllJobSources() {

  return apiRequest(
    "/admin/job-ingestion/sync",
    {
      method: "POST",
    }
  );
}


/*
 * Sync one source.
 */
export function syncJobSource(
  sourceId
) {

  return apiRequest(
    `/admin/job-ingestion/sources/${sourceId}/sync`,
    {
      method: "POST",
    }
  );
}


/*
 * NEW
 *
 * Delete every ExternalJob belonging
 * to one source.
 *
 * The JobSource itself remains.
 */
export function deleteSyncedJobs(
  sourceId
) {

  return apiRequest(
    `/admin/job-ingestion/sources/${sourceId}/jobs`,
    {
      method: "DELETE",
    }
  );
}