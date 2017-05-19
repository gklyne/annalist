## Can I perform bulk import of data?

Annalist does not currently (as of 2017-05) support this directly.

But, with a little programming, it is possible to write data files directly into an Annalist collection as JSON-LD and related data.  Clearly, if doing thjis, it will be important to take care to write files that Annalist can read.

_@@TODO: document entity storage and JSON-LD conventions_

In the longer term, I plan to introduce "data bridges" that allow existing datasets to be incorporated (by reference rather than by copying) into an Annalist data collection.  My first target for this will be to allow existing spreadsheet data to be used with Annalist collections; e.g., I have some early prototype code that can read and re-present Excel spreadsheets and CSV.

