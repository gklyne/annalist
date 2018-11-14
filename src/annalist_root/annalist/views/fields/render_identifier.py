from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Value mapper for Identifier (URI/CURIE) field
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2017, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from utils.py3porting                   import is_string, to_unicode

from annalist.views.fields.render_base  import RenderBase

#   ----------------------------------------------------------------------------
#
#   Identifier value mapping
#
#   ----------------------------------------------------------------------------

class IdentifierValueMapper(RenderBase):
    """
    Value mapper class for entity id field.
    """

    @classmethod
    def decode(cls, field_value):
        """
        Returns an Identifier (URI/CURIE) form field value with leading/trailing spaces trimmed
        """
        if is_string(field_value):
            field_value = field_value.strip()
        return field_value

    # encode defaults to identity mapper]

# End.
