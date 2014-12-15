# Data Capture for the Real World

(Text of a comment posted in response to Cameron neyon's blog post at http://cameronneylon.net/blog/data-capture-for-the-real-world/)

I'm not sure if you'd see this as part of the solution, or part of the problem. I'm working on (yet another?) RDM "system" - https://github.com/gklyne/anna..., http://annalist.net/ - but I am trying to address some of the issues you mention:

* Backup - underlying data is inherently git- friendly, so easily versioned (as a developer, github is my main backup ;) )
* Access to data from different locations - built around web technologies, with mobile-device-friendly "responsive" pages.
* Metadata - I'm not sure there's a universally clear data/metadata distinction, but one of the goals is to be able to annotate (say) images or other data with relevant contextual or observational information
* Provenance - plans to capture provenance info alongside data
* Findable - google-friendly textual data exposed through http, but with labelled fields to allow more semantic search.
* Instrument data - simple web APIs allow data to be added by external processes
* Cataloging - doesn't depend on predefined schema, do cataloging fields can be added as needs are recognised
* Making "pieces work well together" - web technology provides a pretty good base layer, though there's plenty to add. Underlying data is not "locked away" by the application, but presented through the web in a readily used format.

A key notion I'm trying to develop us to allow "just enough structure" at any time, which I think could go some way to addressing some of the concerns you describe. I think this is close to your idea of "The lack of structure, while preserving enough contextual information to be locally useful, can be seen as a strength – any data type can be collected and stored without it needing to be available in some sort of schema."

It's early days yet, and several of the pieces I describe have yet to be realized. I'm hoping to reach a "minimum viable product" stage in a couple of months from now.

Does anything here resonate?
