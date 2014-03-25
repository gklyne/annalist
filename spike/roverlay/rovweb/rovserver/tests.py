"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import random
import unittest
import rdflib
from StringIO import StringIO


from django.test import TestCase
from django.test.client import Client

from MiscUtils.HttpSession       import HTTP_Error, HTTP_Session
from MiscUtils.MockHttpResources import MockHttpFileResources, MockHttpDictResources

from rocommand.ro_namespaces import RDF, RO, ORE, AO

from rovserver.models import ResearchObject, AggregatedResource

TestBaseDir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "testdata/")

def test_resource_list(base_uri):
    return (
        [ base_uri+"res1"
        , base_uri+"res2"
        , base_uri+"res3"
        ])

def test_resource_dict(base_uri):
    return (
        { "res1":   "Resource %s\nLine 2\nLine 3"%(base_uri)
        , "res2":   "Resource %s\nLine 2\nLine 3"%(base_uri)
        , "res3":   "Resource %s\nLine 2\nLine 3"%(base_uri)
        })


class MockHttpResourcesTest(TestCase):

    def test_MockHttpResources(self):
        testbaseuri  = "http://testdomain.org/testdata/ro-test-1/"
        testbasepath = os.path.join(TestBaseDir, "ro-test-1/")
        with MockHttpFileResources(testbaseuri, testbasepath):
            hs = HTTP_Session(testbaseuri)
            (status, reason, headers, body) = hs.doRequest("README-ro-test-1.txt")
            self.assertEquals(status, 200)
            self.assertEquals(reason, "OK")
            self.assertEquals(headers["content-type"], "text/plain")
            self.assertRegexpMatches(body, "README-ro-test-1")
            (status, reason, headers, body) = hs.doRequest("README-ro-test-1.txt", method="HEAD")
            self.assertEquals(status, 200)
            self.assertEquals(reason, "OK")
            self.assertEquals(headers["content-type"], "text/plain")
            self.assertEquals(body, "")
            (status, reason, headers, body) = hs.doRequest("subdir1/subdir1-file.txt")
            self.assertEquals(status, 200)
            self.assertEquals(reason, "OK")
            self.assertEquals(headers["content-type"], "text/plain")
            (status, reason, headers, body) = hs.doRequest("minim.rdf", method="HEAD")
            self.assertEquals(status, 200)
            self.assertEquals(reason, "OK")
            self.assertEquals(headers["content-type"], "application/rdf+xml")
            (status, reason, headers, body) = hs.doRequest("filename%20with%20spaces.txt", method="HEAD")
            self.assertEquals(status, 200)
            self.assertEquals(reason, "OK")
            self.assertEquals(headers["content-type"], "text/plain")
            (status, reason, headers, body) = hs.doRequest("filename%23with%23hashes.txt", method="HEAD")
            self.assertEquals(status, 200)
            self.assertEquals(reason, "OK")
            self.assertEquals(headers["content-type"], "text/plain")
        return

class ResearchObjectsTest(TestCase):

    def test_initial_ResearchObjects(self):
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(list(ResearchObject.objects.all()), [])
        return

    def test_add_ResearchObject(self):
        ro = ResearchObject(uri="http://example.org/RO/test")
        ro.save()
        self.assertEqual(ro.uri, "http://example.org/RO/test")
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(map(str,list(ResearchObject.objects.all())), ["http://example.org/RO/test"])
        return ro

    def test_delete_ResearchObject(self):
        ro = self.test_add_ResearchObject()
        ro.delete()
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(map(str,list(ResearchObject.objects.all())), [])
        return

    def test_initial_AggregatedResource(self):
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        self.assertEqual(list(AggregatedResource.objects.all()), [])
        return

    def test_add_AggregatedResource(self):
        res_uri1 = "http://example.org/RO/test/res1"
        res_uri2 = "http://example.org/RO/test/res2"
        res_str1 = res_uri1 + " (True)"
        res_str2 = res_uri2 + " (False)"
        ro   = self.test_add_ResearchObject()
        res1 = AggregatedResource(ro=ro,uri=res_uri1,is_rdf=True)
        res1.save()
        self.assertEqual(res1.uri, res_uri1)
        self.assertEqual(len(AggregatedResource.objects.all()), 1)
        self.assertEqual(map(str,list(AggregatedResource.objects.all())), [res_str1])
        res2 = AggregatedResource(ro=ro,uri=res_uri2,is_rdf=False)
        res2.save()
        self.assertEqual(res2.uri, res_uri2)
        self.assertEqual(len(AggregatedResource.objects.all()), 2)
        self.assertEqual(map(str,list(AggregatedResource.objects.all())), [res_str1, res_str2])
        # Enumerate aggregation for ro
        ros = ResearchObject.objects.filter(uri="http://example.org/RO/test")
        self.assertEqual(len(ros), 1)
        ars = AggregatedResource.objects.filter(ro=ros[0])
        self.assertEqual(len(ars), 2)
        self.assertIn(res1, ars)
        self.assertIn(res2, ars)
        return

    def test_delete_AggregatedResources(self):
        res_uri1 = "http://example.org/RO/test/res1"
        res_uri2 = "http://example.org/RO/test/res2"
        ro   = self.test_add_ResearchObject()
        res1 = AggregatedResource(ro=ro,uri=res_uri1,is_rdf=True)
        res1.save()
        res2 = AggregatedResource(ro=ro,uri=res_uri2,is_rdf=False)
        res2.save()
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(len(AggregatedResource.objects.all()), 2)
        # Delete ro
        ro.delete()
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        return


class RovServerTest(TestCase):

    def test_roverlay_home_get_html(self):
        """
        Test access to roverlay service home with HTML requested
        """
        c = Client()

        r = c.get("/rovserver/", HTTP_ACCEPT="text/html")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")

        r = c.get("/rovserver/", HTTP_ACCEPT="application/html")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")

        r = c.get("/rovserver/")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")
        return

    def test_roverlay_home_get_uri_list(self):
        """
        Test access to roverlay service home with uri-list requested
        """
        c = Client()
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, "")
        return

    def test_roverlay_home_get_error(self):
        """
        Test access to roverlay service home with unsupported type requested
        """
        c = Client()
        r = c.get("/rovserver/", HTTP_ACCEPT="application/unknown")
        self.assertEqual(r.status_code, 406)
        # self.assertEqual(r.reason_phrase, "Not Acceptable") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service error</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service error</h1>")
        self.assertRegexpMatches(r.content, "<h2>406: Not acceptable</h2>")
        return

    def test_roverlay_home_post_create_ro(self):
        """
        Test logic for creating new RO by POST to service
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        c = Client()
        # Create new RO
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        # self.assertEqual(r.reason_phrase, "Created") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        uri1 = r["Location"]
        self.assertRegexpMatches(uri1, "http://testserver/rovserver/ROs/[0-9[a-f]{8}/")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>New research object created</h2>")
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        # Read it back
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, uri1+"\n")
        # Create another RO
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        # self.assertEqual(r.reason_phrase, "Created") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        uri2 = r["Location"]
        self.assertRegexpMatches(uri2, "http://testserver/rovserver/ROs/[0-9[a-f]{8}/")
        self.assertRegexpMatches(r.content, "<title>roverlay service</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
        self.assertRegexpMatches(r.content, "<h2>New research object created</h2>")
        self.assertEqual(len(ResearchObject.objects.all()), 2)
        # Read it back
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, uri1+"\n"+uri2+"\n")
        return

    def test_roverlay_home_post_error(self):
        """
        Test POST to roverlay service home with unsupported type
        """
        c = Client()
        r = c.post("/rovserver/", data="", content_type="application/xml")
        self.assertEqual(r.status_code, 415)
        # self.assertEqual(r.reason_phrase, "Unsupported Media Type") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        self.assertRegexpMatches(r.content, "<title>roverlay service error</title>")
        self.assertRegexpMatches(r.content, "<h1>roverlay service error</h1>")
        self.assertRegexpMatches(r.content, "<h2>415: Unsupported Media Type</h2>")
        return

    def test_roverlay_home_ros_listed(self):
        """
        Test ROs listed on service page
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        c = Client()
        # Create new ROs
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        uri1 = r["Location"]
        r = c.post("/rovserver/", data="", content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        uri2 = r["Location"]
        # Read it back
        r = c.get("/rovserver/")
        self.assertEqual(r.status_code, 200)
        # self.assertEqual(r.reason_phrase, "OK") # Django 1.6 only
        self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
        def urilisting(uri):
            return """<a href="%s">%s</a>"""%(uri, uri)
        self.assertRegexpMatches(r.content, urilisting(uri1))
        self.assertRegexpMatches(r.content, urilisting(uri2))
        return

    def create_test_ro(self, base_uri, uri_list=None):
        c = Client()
        base_uri = "http://example.org/resource/"
        uri_list = uri_list or test_resource_list(base_uri)
        uri_text = "\n".join(uri_list)
        r = c.post("/rovserver/", data=uri_text, content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        ro_uri = r["Location"]
        return ro_uri

    def test_roverlay_home_post_create_aggregation(self):
        """
        Test logic for creating new RO by POST to service
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        c = Client()
        # Create new RO
        base_uri = "http://example.org/resource/"
        uri_list = (
            [ "# Comment at start of URI list"
            , base_uri+"res1"
            , "# Another comment"
            , base_uri+"res2"
            , ""
            , base_uri+"res3"
            ])
        with MockHttpDictResources(base_uri, test_resource_dict(base_uri)):
            ro_uri = self.create_test_ro(base_uri, uri_list)
            self.assertEqual(len(ResearchObject.objects.all()), 1)
            self.assertEqual(len(AggregatedResource.objects.all()), 3)
            # Read back RO list
            r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
            self.assertEqual(r.content, ro_uri+"\n")
        # Check aggregated content
        ros = ResearchObject.objects.filter(uri=ro_uri)
        self.assertEqual(len(ros), 1)
        ars = AggregatedResource.objects.filter(ro=ros[0])
        self.assertEqual(len(ars), 3)
        for ar in ars:
            self.assertIn(ar.uri, uri_list)
        return

    def test_roverlay_ro_get_html(self):
        c = Client()
        base_uri = "http://example.org/resource/"
        with MockHttpDictResources(base_uri, test_resource_dict(base_uri)):
            ro_uri = self.create_test_ro(base_uri)
            # Read HTML for created RO
            r = c.get(ro_uri, HTTP_ACCEPT="text/html")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r["Content-Type"].split(';')[0], "text/html")
            self.assertRegexpMatches(r.content, "<title>Research Object %s</title>"%(ro_uri))
            # self.assertRegexpMatches(r.content, "<h1>roverlay service</h1>")
            # self.assertRegexpMatches(r.content, "<h2>roverlay service interface</h2>")
            def urilisting(uri):
                return """<a href="%s">%s</a>"""%(uri, uri)
            for uri in test_resource_list(base_uri):
                self.assertRegexpMatches(r.content, urilisting(uri))
        return

    def test_roverlay_ro_get_404(self):
        c = Client()
        base_uri = "http://example.org/resource/"
        with MockHttpDictResources(base_uri, test_resource_dict(base_uri)):
            ro_uri = self.create_test_ro(base_uri)
            # Read HTML for created RO
            r = c.get(ro_uri, HTTP_ACCEPT="text/html")
            self.assertEqual(r.status_code, 200)
            no_uri = ro_uri[:-9]+"c01dca11/"
            r = c.get(no_uri, HTTP_ACCEPT="text/html")
            self.assertEqual(r.status_code, 404)
            self.assertRegexpMatches(r.content, r"<title>Error 404: Not found .*</title>")
            self.assertRegexpMatches(r.content, r"<h1>Error 404: Not found .*</h1>")
            self.assertRegexpMatches(r.content, "<p>Research object %s not found</p>"%(no_uri))
        return

    def test_roverlay_ro_get_rdf(self):
        c = Client()
        testbaseuri  = "http://testdomain.org/testdata/ro-test-1/"
        testbasepath = os.path.join(TestBaseDir, "ro-test-1/")
        ro_uri_list = (
            [ testbaseuri+"README-ro-test-1.txt"
            , testbaseuri+"filename%20with%20spaces.txt"
            , testbaseuri+"filename%23with%23hashes.txt"
            , testbaseuri+"minim.rdf"
            , testbaseuri+"subdir1/subdir1-file.txt"
            , testbaseuri+"subdir2/subdir2-file.txt"
            ])
        with MockHttpFileResources(testbaseuri, testbasepath):
            ro_uri = self.create_test_ro(testbaseuri, ro_uri_list)
            r = c.get(ro_uri, HTTP_ACCEPT="application/rdf+xml")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r["Content-Type"].split(';')[0], "application/rdf+xml")
            mg = rdflib.Graph()
            mg.parse(StringIO(r.content), format="xml", publicID=ro_uri)
            rosub = rdflib.URIRef(ro_uri)
            for ar in ro_uri_list:
                self.assertIn((rosub, ORE.aggregates, rdflib.URIRef(ar)), mg)
            # Check annotation
            #
            # <ore:aggregates>
            #   <ro:AggregatedAnnotation>
            #     <ro:annotatesAggregatedResource rdf:resource="data/UserRequirements-astro.ods" />
            #     <ao:body rdf:resource=".ro/(annotation).rdf" />
            #   </ro:AggregatedAnnotation>
            # </ore:aggregates>
            abody   = rdflib.URIRef(testbaseuri+"minim.rdf")
            astub = mg.value(predicate=AO.body, object=abody)
            self.assertIsNotNone(astub)
            self.assertIn((rosub, ORE.aggregates, astub), mg)
            self.assertIn((astub, RDF.type, RO.AggregatedAnnotation), mg)
            self.assertIn((astub, RO.annotatesAggregatedResource, rosub), mg)
        return

    def test_roverlay_ro_get_turtle(self):
        c = Client()
        testbaseuri  = "http://testdomain.org/testdata/ro-test-1/"
        testbasepath = os.path.join(TestBaseDir, "ro-test-1/")
        ro_uri_list = (
            [ testbaseuri+"README-ro-test-1.txt"
            , testbaseuri+"filename%20with%20spaces.txt"
            , testbaseuri+"filename%23with%23hashes.txt"
            , testbaseuri+"minim.rdf"
            , testbaseuri+"subdir1/subdir1-file.txt"
            , testbaseuri+"subdir2/subdir2-file.txt"
            ])
        with MockHttpFileResources(testbaseuri, testbasepath):
            ro_uri = self.create_test_ro(testbaseuri, ro_uri_list)
            r = c.get(ro_uri, HTTP_ACCEPT="text/turtle;charset=UTF-8")
            self.assertEqual(r.status_code, 200)
            self.assertEqual(r["Content-Type"].split(';')[0], "text/turtle")
            mg = rdflib.Graph()
            mg.parse(StringIO(r.content), format="turtle", publicID=ro_uri)
            rosub = rdflib.URIRef(ro_uri)
            for ar in ro_uri_list:
                self.assertIn((rosub, ORE.aggregates, rdflib.URIRef(ar)), mg)
            # Check annotation
            #
            # <ore:aggregates>
            #   <ro:AggregatedAnnotation>
            #     <ro:annotatesAggregatedResource rdf:resource="data/UserRequirements-astro.ods" />
            #     <ao:body rdf:resource=".ro/(annotation).rdf" />
            #   </ro:AggregatedAnnotation>
            # </ore:aggregates>
            abody   = rdflib.URIRef(testbaseuri+"minim.rdf")
            astub = mg.value(predicate=AO.body, object=abody)
            self.assertIsNotNone(astub)
            self.assertIn((rosub, ORE.aggregates, astub), mg)
            self.assertIn((astub, RDF.type, RO.AggregatedAnnotation), mg)
            self.assertIn((astub, RO.annotatesAggregatedResource, rosub), mg)
        return

    @unittest.skip("Slow test")
    def test_roverlay_home_post_github_aggregation(self):
        """
        Test logic for creating new RO by POST to service
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        c = Client()
        # Create new RO
        base_uri = "http://wf4ever.github.io/ro-catalogue/v0.1/simple-requirements/"
        uri_list = (
            [ base_uri + "checklist-runnable.rdf"
            , base_uri + "data/UserRequirements-astro.ods"
            , base_uri + "data/UserRequirements-bio.ods"
            , base_uri + "data/UserRequirements-gen.ods"
            , base_uri + "docs/mkjson.sh"
            , base_uri + "docs/UserRequirements-astro.csv"
            , base_uri + "docs/UserRequirements-astro.json"
            , base_uri + "docs/UserRequirements-bio.csv"
            , base_uri + "docs/UserRequirements-bio.json"
            , base_uri + "docs/UserRequirements-gen.csv"
            , base_uri + "docs/UserRequirements-gen.json"
            , base_uri + "make.sh"
            , base_uri + "minim-checklist.sh"
            , base_uri + "python"
            , base_uri + "python/ReadCSV.py"
            , base_uri + "README"
            , base_uri + "simple-requirements-minim.rdf"
            , base_uri + "simple-requirements-wfdesc.rdf"
            , base_uri + "simple-requirements-wfprov.rdf"
            , base_uri + "TODO"
            ])
        ro_uri = self.create_test_ro(base_uri, uri_list)
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(len(AggregatedResource.objects.all()), 20)
        # Read back RO list
        r = c.get("/rovserver/", HTTP_ACCEPT="text/uri-list")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r["Content-Type"].split(';')[0], "text/uri-list")
        self.assertEqual(r.content, ro_uri+"\n")
        # Check aggregated content
        ros = ResearchObject.objects.filter(uri=ro_uri)
        self.assertEqual(len(ros), 1)
        ars = AggregatedResource.objects.filter(ro=ros[0])
        self.assertEqual(len(ars), 20)
        for ar in ars:
            self.assertIn(ar.uri, uri_list)
        return

    def test_roverlay_ro_delete(self):
        """
        Test logic for deleting RO aggregation by DELETE to service
        """
        self.assertEqual(len(ResearchObject.objects.all()), 0)
        self.assertEqual(len(AggregatedResource.objects.all()), 0)
        c = Client()
        # Create new RO
        base_uri = "http://example.org/resource/"
        uri_list = (
            [ "# Comment at start of URI list"
            , base_uri+"res1"
            , base_uri+"res2"
            , base_uri+"res3"
            ])
        uri_text = "\n".join(uri_list)
        r = c.post("/rovserver/", data=uri_text, content_type="text/uri-list")
        self.assertEqual(r.status_code, 201)
        ro_uri = r["Location"]
        self.assertEqual(len(ResearchObject.objects.all()), 1)
        self.assertEqual(len(AggregatedResource.objects.all()), 3)
        # Delete RO
        r = c.delete(ro_uri)
        self.assertEqual(r.status_code, 204)
        # Check RO and aggregated content are gone
        ros = ResearchObject.objects.filter(uri=ro_uri)
        self.assertEqual(len(ros), 0)
        ars = AggregatedResource.objects.all()
        self.assertEqual(len(ars), 0)
        return

        # import inspect
        # print "ATTRIBUTES:"
        # for (k,v) in inspect.getmembers(r):
        #     print "%20s  %s"%(k,repr(v))
        # print "__dict__:"
        # for k in r.__dict__:
        #     print "[%20s]  %s"%(k,repr(r.__dict__[k]))
