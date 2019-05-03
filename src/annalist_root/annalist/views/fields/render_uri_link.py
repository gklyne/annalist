from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Renderer and value mapper for URI value displayed as a link.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from utils.py3porting                           import is_string, to_unicode

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_edit_value, get_field_view_value
    )

from django.template    import Template, Context

#   ----------------------------------------------------------------------------
#
#   Link URI value mapping
#
#   ----------------------------------------------------------------------------


class URILinkValueMapper(RenderBase):
    """
    Value mapper class for URI string presented for viewing as a clickable link
    """

    @classmethod
    def encode(cls, data_value):
        """
        Encodes link value as string
        """
        return data_value or ""

    @classmethod
    def decode(cls, field_value):
        """
        Decodes a URI string value as a link
        """
        if is_string(field_value):
            field_value = field_value.strip()
        return field_value or ""


#   ----------------------------------------------------------------------------
#
#   Link URI field renderers
#
#   ----------------------------------------------------------------------------

class uri_link_view_renderer(object):

    def render(self, context):
        """
        Render link for viewing.
        """
        linkval = URILinkValueMapper.encode(get_field_view_value(context, ""))
        # log.info("uri_link_view_renderer: linkval %r (orig)"%(linkval,))
        common_prefixes = (
            [ "http://", "https://"
            , "file:///", "file://localhost/", "file://"
            , "mailto:"]
            )
        textval = linkval
        for p in common_prefixes:
            if is_string(linkval) and linkval.startswith(p):
                textval = linkval[len(p):]
                break
        if ":" in linkval:
            link_pref, link_path = linkval.split(":", 1)
            if "collection" not in context:
                log.warning("uri_link_view_renderer: no key 'collection' in context")
                # log.error("@@@@@@@@@@@@@@@@@@@@@")
                # for k in context.flatten():
                #     hidden_fields = (
                #         [ "fields", "row_bound_fields", "repeat_bound_fields"
                #         , "help_text", "help_markdown"
                #         , "forloop", "f", "block", "view_choices"
                #         , "LANGUAGES"
                #         ])
                #     if k not in hidden_fields:
                #         log.error("    @@@ %s: %r"%(k, context[k]))
            else:
                link_vocab = context["collection"].cache_get_vocab(link_pref)
                if link_vocab:
                    linkval = link_vocab.get_uri() + link_path
        # log.info("uri_link_view_renderer: linkval %r (final)"%(linkval,))
        return '''<a href="%s" target="_blank">%s</a>'''%(linkval, textval)

class uri_link_edit_renderer(object):

    def __init__(self):
        self._template = Template(
            '''<input type="text" size="64" name="{{repeat_prefix}}{{field.description.field_name}}" '''+
                   '''placeholder="{{field.description.field_placeholder}}" '''+
                   '''value="{{field.field_edit_value}}" />'''
        )
        return

    def render(self, context):
        """
        Render link for editing
        """
        return self._template.render(context)

def get_uri_link_renderer():
    """
    Return field renderer object for URI link values
    """
    return RenderFieldValue("uri_link",
        view_renderer=uri_link_view_renderer(), 
        edit_renderer=uri_link_edit_renderer(),
        )

# End.
