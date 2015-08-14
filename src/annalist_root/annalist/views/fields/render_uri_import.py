"""
Renderer and value mapper for URI value used to import a resource into 
the local data store.

NOTE: the actual import logic is handled by the edit form handler:
the renderer just ensures appropriate values are returned.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_edit_value,
    get_field_view_value
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Link URI value mapping
#
#   ----------------------------------------------------------------------------


class URIImportValueMapper(RenderBase):
    """
    Value mapper class for token list
    """

    @classmethod
    def encode(cls, data_value):
        """
        Extracts import URL from value structure, for field display.
        """
        return (data_value or {}).get('import_url', "")

    @classmethod
    def decode(cls, field_value):
        """
        Returns textual link value from import URL field value
        """
        return field_value or ""

    def decode_store(self, field_value, entityvals, property_uri):
        """
        Decodes a supplied value and uses it to update the 'import_url'
        field of an URI import field.  
        """
        u = self.decode(field_value)
        v = entityvals.get(property_uri, {})
        if isinstance(v, dict):
            v['import_url'] = u
        else:
            v = {'import_url': u}
        entityvals[property_uri] = v
        return v

#   ----------------------------------------------------------------------------
#
#   Import value templates
#
#   ----------------------------------------------------------------------------

view_import = (
    """<a href="%s" target="_blank">%s</a>""")

edit_import = (
    """<!-- fields.uri_import_edit_renderer -->
    <div class="row">
      <div class="small-10 columns view-value view-subfield less-import-button">
        <input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}"
               placeholder="{{field.field_placeholder}}"
               value="{{encoded_field_value}}" />
      </div>
      <div class="small-2 columns view-value view-subfield import-button left small-text-right">
        <input type="submit" name="{{repeat_prefix}}{{field.field_name}}__import" value="Import" />
      </div>
    </div>
    """)


#   ----------------------------------------------------------------------------
#
#   Link URI field renderers
#
#   ----------------------------------------------------------------------------

class uri_import_view_renderer(object):

    def render(self, context):
        """
        Render import link for viewing.
        """
        linkval = URIImportValueMapper.encode(get_field_view_value(context, ""))
        common_prefixes = (
            [ "http://", "https://"
            , "file:///", "file://localhost/", "file://"
            , "mailto:"]
            )
        textval = linkval
        for p in common_prefixes:
            if linkval.startswith(p):
                textval = linkval[len(p):]
                break
        return view_import%(linkval, textval)

class uri_import_edit_renderer(object):

    def __init__(self):
        self._template = Template(edit_import)
        return

    def render(self, context):
        """
        Render import link for editing
        """
        val = URIImportValueMapper.encode(get_field_edit_value(context, None))
        with context.push(encoded_field_value=val):
            result = self._template.render(context)
        return result

def get_uri_import_renderer():
    """
    Return field renderer object for uri import value
    """
    return RenderFieldValue(
        view_renderer=uri_import_view_renderer(), 
        edit_renderer=uri_import_edit_renderer(),
        )

# End.
