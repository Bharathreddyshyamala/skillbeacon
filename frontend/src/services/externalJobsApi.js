import {
  apiRequest,
} from "../api";


export function getExternalJobs({
  search = "",
  company = "",
  location = "",
  sort = "posted",
  page = 1,
  pageSize = 50,
} = {}) {

  const params =
    new URLSearchParams();


  if (search.trim()) {

    params.set(
      "search",
      search.trim()
    );
  }


  if (company.trim()) {

    params.set(
      "company",
      company.trim()
    );
  }


  if (location.trim()) {

    params.set(
      "location",
      location.trim()
    );
  }


  params.set(
    "sort",
    sort
  );


  params.set(
    "page",
    String(page)
  );


  params.set(
    "page_size",
    String(pageSize)
  );


  return apiRequest(
    `/external-jobs?${params.toString()}`
  );
}
