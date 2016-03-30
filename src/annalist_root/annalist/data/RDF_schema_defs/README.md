# RDF_schema_defs

This Annalist collection contains definitions that may be imported to creaing RDF schema definitions as an Annalist collection.

NOTE: current limitations of Annalist mean that the exported JSON-LD does not directly use standard RDF schema terms for everything.  For example, subclasses are referenced using a local URI reference rather than the global absolute URI, which can be obtained by defererencing the given reference and extracting the `annal:uri` value from there.

