This directory subtree contains Annalist data that is common to all Annalist installations, in the form of annalist data records.

These records are somewhat self-referential, as they constitute data that is used to bootstarap the Annalist record descrtiption capabilities, describing the views and lists that are used for rendering record views and lists.

The definitions also include default values (e.g. default recoird types and views, etc.).  The intent is that the base definitions may be copied and modified for individual collections.  When looking for a view or list definition, the Annalist software will first look in the collection's own metadata area (which can be locally modified), and then in the overall site metadata area (which cannot be locally modified, and provides baseline compatibility between Annalisty installations).

NOTE: do not delete _annalist_site/site_meta.jsonld from the target site when updating site data:  that file is site-specific.
