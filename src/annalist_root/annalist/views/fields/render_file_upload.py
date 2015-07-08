"""
Renderer and value mapper for file upload used to upload a resource into 
the local data store.
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


class FileUploadValueMapper(RenderBase):
    """
    Value mapper class for token list
    """

    @classmethod
    def resource_name(cls, data_value):
        """
        Extracts import URL ref from value structure, for field display.
        """
        return (data_value or {}).get('resource_name', "(@@resource_name not present)")

    @classmethod
    def uploaded_file(cls, data_value):
        """
        Extracts uploaded filename from value structure, for field display.
        """
        return (data_value or {}).get('uploaded_file', "")


    @classmethod
    def encode(cls, data_value):
        """
        Extracts import URL ref from value structure, for field display.
        """
        return cls.resource_name(data_value)

    @classmethod
    def decode(cls, field_value):
        """
        Returns textual path value from file upload field value
        """
        return field_value or ""

    def decode_store(self, field_value, entityvals, property_uri):
        """
        Decodes a supplied value and uses it to update the 'upload_file'
        field of an URI import field.  
        """
        u = self.decode(field_value)
        v = entityvals.get(property_uri, {})
        try:
            v['resource_name'] = u
        except TypeError:
            v = {'resource_name': u}    # Ignore non-updatable value
        entityvals[property_uri] = v
        return v

#   ----------------------------------------------------------------------------
#
#   Import value templates
#
#   ----------------------------------------------------------------------------

# NOTE: this is a minimal rendering.  Enhancements might include additional information 
#       from the entity field, especially for the view (e.g. content-type, etc.)
# NOTE: The <a> element supports a `type` attribute 
#       (cf. https://developer.mozilla.org/en-US/docs/Web/HTML/Element/a)

view_upload = (
    """Uploaded file <a href="%s" target="_blank">%s</a>""")

edit_upload = (
    """<!-- fields.render_file_upload -->
    <input type="file" name="{{repeat_prefix}}{{field.field_name}}"
           placeholder="{{field.field_placeholder}}"
           value="{{resource_name}}" />
    {% if uploaded_file != "" %}
    Previously uploaded: {{uploaded_file}}
    {% endif %}
    """)

#   ----------------------------------------------------------------------------
#
#   Link URI field renderers
#
#   ----------------------------------------------------------------------------

class File_upload_view_renderer(object):

    def render(self, context):
        """
        Render import link for viewing.
        """
        val      = get_field_view_value(context, None)
        linkval  = FileUploadValueMapper.resource_name(val)
        textval  = FileUploadValueMapper.uploaded_file(val)
        return view_upload%(linkval, textval)

class File_upload_edit_renderer(object):

    def __init__(self):
        self._template = Template(edit_upload)
        return

    def render(self, context):
        """
        Render import link for editing
        """
        val = get_field_edit_value(context, None)
        resource_name = FileUploadValueMapper.resource_name(val)
        uploaded_file = FileUploadValueMapper.uploaded_file(val)
        with context.push(resource_name=resource_name, uploaded_file=uploaded_file):
            result = self._template.render(context)
        return result

def get_file_upload_renderer():
    """
    Return field renderer object for uri import value
    """
    return RenderFieldValue(
        view_renderer=File_upload_view_renderer(), 
        edit_renderer=File_upload_edit_renderer(),
        )

# End.
