"""
Renderer and value mapper for Entity Id field
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

# from django.http        import HttpResponse
from django.template    import Template

from annalist.views.fields.render_base  import RenderBase

#   ----------------------------------------------------------------------------
#
#   Entity Id value mapping
#
#   ----------------------------------------------------------------------------

class EntityIdValueMapper(RenderBase):
    """
    Value mapper class for entity id field.
    """

    @classmethod
    def decode(cls, field_value):
        """
        Returns an entity Id form field value as itself with leading/trailing spaces trimmed
        """
        if isinstance(field_value, (str, unicode)):
            field_value = field_value.strip()
        return field_value

    # encode defaults to identity mapper]

#   ----------------------------------------------------------------------------
#
#   Entity Id field renderers
#
#   ----------------------------------------------------------------------------




# End.
