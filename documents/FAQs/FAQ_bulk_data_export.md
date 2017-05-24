## Can I perform bulk export of data?

Yes, if you're OK with Annalist's native JSON format.

There are a number of possible routes:

1. If an HTTP request for a list of collection entities is content negotiated as JSON-LD, the returned data contains full content of each entity.  But note that attachments such as uploaded images are not returned by this method.

2. The data can be read directly from the underlying file system.  This requires system access to (i.e. ability to run software) the Annalist server host.

3. A web server (such as Apache httpd) can be configured to make the Annalist collection data available via HTTP requests.

4. A variation of approach 2 that I use a lot is to configure an Annalist collection as a git project, and push it to GitHub (or some other accessible git repository system)

Not currently implemented (as of 2017-05) is conversion to different formats, though a Turtle export is being actively considered.  A future development to provide a dump of an Annalist collection as (say) a zip file is an definite possibility, but is not currently planned (but could be implemented quite quickly if a real requirement were to arise).

