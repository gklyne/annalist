## Is there an API for external applications to interact with Annalist data

Yes.  The "API" here is pure HTTP.

Annalist supports content negotiation for retrieving data - currently, only HTML (for web forms) and JSON-LD are offered, but other formats are on the development roadmap.

As yet (2017-05), I haven't implemented HTTP PUT, DELETE operations in Annalist, but these could be performed using a normal web server.  (A challenge here is to implement a coherent access control model.)

Also on the development roadmap is the capability to use LDP/SoLiD as a backend for Annalist (as an alternative to the server host's local file system).  This would provide a natural HTTP API to Annalist data and a clearer route to sharing with other applications.

It is also possible for other applications on the Annalist server to read and write directly to Annalist's collection data storage files (subject to access permissions, of course).

### HTTP interface

The HTTP interface isn't documented separately: it's just an HTTP GET to the same URI that is used to display the content in a browser, content negotiated to JSON-LD (which generates an HTTP redirect response).  Alternatively, if you browse to a page containing the data you want to access, you'll find two links at the bottom:  "JSON-LD" and "DATA" (they return the same data but with different MIME types).  You can grab the URL to use from there.

A similar thing works for collection entity listings, where a key "annal:entity_list" in the result data contains a list of all the selected entities.

I'd suggest experimenting with the CURL tool to get a feel for what is available.

@@TODO: generate link headers for accessing data from other views.