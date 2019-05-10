# annalist_site.test

Contains data used when running Django tests.

empty/ contains a copy of the site data used to initialize a new (empty) site.
testinit/ contains a copy of the site data used to initialize the site used for testing.
data/ contains the site that is actually modified by the tests

The test suite also copies data from annalist/data/sitedata/ into the data/ directory 
when running tests (this contains definitions of built-in forms, etc., which may 
in principle be overridden by local definitions).

The actual test data is created by annalist.tests.test_createsitedata.CreateSiteData.

