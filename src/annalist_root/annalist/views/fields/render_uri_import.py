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

from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_value
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Link URI value mapping
#
#   ----------------------------------------------------------------------------


class URIImportValueMapper(object):
    """
    Value mapper class for token list
    """

    @staticmethod
    def encode(data_value):
        """
        Encodes link value as string
        """
        return data_value or ""

    @staticmethod
    def decode(field_value):
        """
        Decodes a text value as a link.
        """
        return field_value or ""

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
      <div class="small-10 columns view-value less-import-button">
        <input type="text" size="64" name="{{repeat_prefix}}{{field.field_name}}"
               placeholder="{{field.field_placeholder}}"
               value="{{field.field_value}}" />
      </div>
      <div class="small-2 columns view-value import-button left small-text-right">
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
        linkval = URIImportValueMapper.encode(get_field_value(context, ""))
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
        return self._template.render(context)

def get_uri_import_renderer():
    """
    Return field renderer object for uri import value
    """
    return RenderFieldValue(
        view_renderer=uri_import_view_renderer(), 
        edit_renderer=uri_import_edit_renderer(),
        )

# End.
