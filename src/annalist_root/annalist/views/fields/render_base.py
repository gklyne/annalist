"""
Base class for renderers
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

class RenderBase(object):
    """
    Base class for form value renderers
    """

    def __init__(self):
        """
        Creates a renderer object for a simple text field
        """
        super(RenderBase, self).__init__()
        return

    def render(self, context):
        assert False, "Render method not implemented for %s"%(type(__self__).__name__)

    @classmethod
    def encode(cls, field_value):
        """
        Returns a string value as itself, for use as a textual form value
        """
        return field_value

    @classmethod
    def decode(cls, field_value):
        """
        Returns a textual form value as itself.
        """
        return field_value

    def decode_store(self, field_value, entityvals, property_uri):
        """
        Decodes a supplied value and stores it into a field of 
        a supplied entity value dictionary
        """
        v = self.decode(field_value)
        entityvals[property_uri] = v
        return v

# End.
