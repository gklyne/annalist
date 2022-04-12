## What do the various one-character directories mean?

These are used as URL path elements to avoid ambiguity in path specifications.

*   `/c/` collections
*   `/d/` data (presents using default view) - the form here is `.../d/<type-id>/<entity-id>`
*   `/l/` lists (use specified list view)
*   `/v/` views (use specified entity view)

Others may be added later.

NOTE: these details are provided for information.  Per REST hypermedia principles, client applications should not use knowledge of the URI structure, but rather should follow links from the Annalist site home page.

Currently (2017-05), the home page is not content negotiated, so until machine-readable link data is presented it may be necessary to exploit some aspects of URL structure.

