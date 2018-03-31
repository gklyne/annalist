"""
Test case with additional test methods used by some Annalist tests
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import re

import logging
log = logging.getLogger(__name__)

from django.test import TestCase # cf. https://docs.djangoproject.com/en/dev/topics/testing/tools/#assertions

from annalist.models.entitytypeinfo             import EntityTypeInfo

from annalist.views.fields.bound_field          import bound_field
from annalist.views.fields.field_description    import FieldDescription

class AnnalistTestCase(TestCase):
    """
    Additonal test methods for Annalist test cases
    """

    def check_entity_does_not_exist(self, type_id, entity_id):
        "Helper function checks content of entity record"
        typeinfo = EntityTypeInfo(self.testcoll, type_id)
        self.assertFalse(typeinfo.entity_exists(entity_id))
        return

    def check_entity_values(self, type_id, entity_id, check_values=None):
        "Helper function checks content of entity record; returns entity"
        typeinfo = EntityTypeInfo(self.testcoll, type_id)
        self.assertTrue(typeinfo.entity_exists(entity_id))
        e = typeinfo.get_entity(entity_id)
        self.assertEqual(e.get_id(), entity_id)
        self.assertEqual(e.get_type_id(), type_id)
        self.assertDictionaryMatch(e.get_values(), check_values)
        return e

    def assertEqualPrefix(self, actual, expect, prefix=""):
        self.assertEqual(actual, expect, msg="%s: actual %r, expected %r"%(prefix, actual, expect))
        return

    def assertMatch(self, string, pattern, msg=None):
        """
        Throw an exception if the regular expresson pattern is matched
        """
        m = re.search(pattern, string)
        if not m or not m.group(0):
            raise self.failureException(
                (msg or "'%s' does not match /%s/"%(string, pattern)))
        return

    def assertKeysMatch(self, actual_dict, expect_dict):
        """
        Check that the expect_dict keys are the same as those in actual_dict.

        Use with assertDictionaryMatch to ensure that two dictionaries are the same,
        not just that all the expected entries are present in the actual dictionary.
        """
        self.assertEqual(set(actual_dict.keys()), set(expect_dict.keys()))
        return

    def assertDictionaryMatch(self, actual_dict, expect_dict, prefix=""):
        """
        Check that the expect_dict values are all present in actual_dict.

        If a dictionary element (with a key other than '@type') contains a list, the 
        listed values are assumed to be dictionaries which are matched recursively. 
        (This logic is used when checking sub-contexts used to render data-defined 
        forms.)

        Similarly, if a dictionary element is itself a dictionary, the 
        corresponding values are matched recursively.
        """
        # log.info("\n***********\nexpect_dict %r"%(expect_dict))
        # log.info("\n-----------\nactual_dict %r"%(actual_dict))
        for k in expect_dict:
            if k not in actual_dict:
                log.info(prefix+"Expected key %s not found in actual"%(k))
                log.info("  expect %r"%(expect_dict,))
                log.info("  actual %r"%(actual_dict,))
            self.assertTrue(k in actual_dict, prefix+"Expected key %s not found in actual"%(k))
            if isinstance(expect_dict[k],(list,tuple)):
                if isinstance(actual_dict[k],(list,tuple)):
                    # log.info("dict match: prefix: %s, key: %s, list_len %d"%(prefix, k, len(expect_dict[k])))
                    if k == "@type":
                        self.assertEqual(
                            set(actual_dict[k]), set(expect_dict[k]),
                            "Key %s: %r != %r"%(k, set(actual_dict[k]), set(expect_dict[k]))
                            )
                    else:
                        # NOTE: this logic tests for expected list being a leading sublist of 
                        # the actual list.  Thus, an empty epected list macthes any actual list.
                        for i in range(len(expect_dict[k])):
                            # if i >= len(actual_dict[k]):
                            #     log.info("\n***********\nexpect_dict %r"%(expect_dict))
                            #     log.info("\n-----------\nactual_dict %r"%(actual_dict))
                            #     log.info("\n***********")
                            self.assertTrue(i < len(actual_dict[k]), prefix+"Actual dict key %s has no element %d"%(k,i))
                            if ( isinstance(actual_dict[k][i], (dict, bound_field, FieldDescription)) and 
                                 isinstance(expect_dict[k][i], dict)
                               ):
                                self.assertDictionaryMatch(
                                    actual_dict[k][i], expect_dict[k][i], 
                                    prefix=prefix+"Key %s[%d]: "%(k,i)
                                    )
                            else:
                                self.assertEqual(
                                    actual_dict[k][i], expect_dict[k][i],
                                    prefix+"Key %s[%d]: %r != %r"%(k, i, actual_dict[k], expect_dict[k])
                                    )
                else:
                    self.fail(prefix+"Key %s expected list, got %r instead of %r"%(k, actual_dict[k], expect_dict[k]))
            elif isinstance(expect_dict[k],dict):
                self.assertDictionaryMatch(
                    actual_dict[k], expect_dict[k], 
                    prefix=prefix+"Key %s: "%(k,)
                    )
            else:
                if actual_dict[k] != expect_dict[k]:
                    log.info("\n***********\nexpect_dict %r"%(expect_dict))
                    log.info("\n-----------\nactual_dict %r"%(actual_dict))
                    log.info("\n***********")
                # log.info("dict match: prefix: %s, key: %s, actual %s, expected: %s"%(prefix, k, actual_dict[k], expect_dict[k]))
                self.assertEqual(actual_dict[k], expect_dict[k], 
                    prefix+"Key %s: actual '%s' expected '%s'"%(k, actual_dict[k], expect_dict[k]))
        # log.info("\n****** matched")
        return

    def assertEqualIgnoreWS(self, first, second, msg=None):
        """
        Test if string `first` is equal to `second`, normalizing all whitespace.
        """
        self.assertEqual(
            re.sub(r'\s+', " ", first).strip(), 
            re.sub(r'\s+', " ", second).strip(), 
            msg=msg)
        return

    def assertInIgnoreWS(self, first, second, msg=None):
        """
        Test if string `first` is contained within `second`, normalizing all whitespace.
        """
        self.assertIn(re.sub(r'\s+', " ", first), re.sub(r'\s+', " ", second), msg=msg)
        return

    def assertStarts(self, first, second, msg=None):
        """
        Test that string `second` starts with the string `first`
        """
        second_start = second[:len(first)]
        self.assertEqual(first, second_start, msg=msg)
        return

# End.
