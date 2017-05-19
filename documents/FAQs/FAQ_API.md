## Is there an API for external applications to interact with Annalist data

Yes.  The "API" here is pure HTTP.

Annalist supports content negotiation for retrieving data - currently, only HTML (for web forms) and JSON-LD are offered, but other formats are on the development roadmap.

As yet (2017-05), I haven't implemented HTTP PUT, DELETE operations in Annalist, but these could be performed using a normal web server.  (A challenge here is to implement a coherent access control model.)

Also on the development roadmap is the capability to use LDP/SoLiD as a backend for Annalist (as an alternative to the server host's local file system).  This would provide a natural HTTP API to Annalist data and a clearer route to sharing with other applications.

It is also possible for other applications on the Annalist server to read and write directly to Annalist's collection data storage files (subject to access permissions, of course).

