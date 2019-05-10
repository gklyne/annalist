from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

"""
Renderer and value mapper for a short (1-line) text value with optional language code.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2019, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
import collections

from utils.py3porting                           import is_string, to_unicode

from annalist.views.fields.render_base          import RenderBase

from django.conf            import settings
from django.template        import Template, Context

#   ----------------------------------------------------------------------------
#
#   Language-tagged text value mapping
#
#   ----------------------------------------------------------------------------


class TextLanguageValueMapper(RenderBase):
    """
    Value mapper class for language-tagged text
    """

    @classmethod
    def encode(cls, field_value):
        """
        Encodes language-tagged string for display

        >>> TextLanguageValueMapper.encode("text") == "text"
        True
        >>> TextLanguageValueMapper.encode({ "@value": "text" }) == "text"
        True
        >>> TextLanguageValueMapper.encode({ "@value": "text", "@language": "en" }) == "text (en)"
        True
        >>> TextLanguageValueMapper.encode({ "@value": "text", "@language": "" }) == "text"
        True
        >>> TextLanguageValueMapper.encode({ "@value": "text", "@language": None }) == "text"
        True
        """
        field_string = ""
        if is_string(field_value):
            field_string = field_value.strip()
        elif isinstance(field_value, collections.Mapping):
            field_string = field_value["@value"]
            if ("@language" in field_value) and field_value["@language"]:
                field_string += (" ("+field_value["@language"]+")")
        return field_string

    @classmethod
    def decode(cls, field_string):
        """
        Decodes a language-tagged string value as an internal JSON-bvased representation.

        >>> TextLanguageValueMapper.decode("text") == { "@value": "text" }
        True
        >>> TextLanguageValueMapper.decode("text (en)") == { "@value": "text", "@language": "en" }
        True
        >>> TextLanguageValueMapper.decode("text (en) more") == { "@value": "text (en) more" }
        True
        >>> TextLanguageValueMapper.decode("") == { "@value": "" }
        True
        """
        field_string = field_string or ""
        m = re.match(r"^(.*)(\s+\((\w[\w-]+)\))$", field_string)
        if m:
            field_value = { "@value": m.group(1).strip() }
            if m.group(2):
                field_value["@language"] = m.group(3).strip()
        else:
            field_value = { "@value": field_string or "" }
        return field_value

#   ----------------------------------------------------------------------------
#
#   Language-tagged text field renderers
#
#   ----------------------------------------------------------------------------

class text_language_view_renderer(object):

    def render(self, context):
        """
        Render language-tagged text for viewing.
        """
        from annalist.views.fields.render_fieldvalue import get_field_view_value
        textval = TextLanguageValueMapper.encode(get_field_view_value(context, ""))
        log.debug("text_language_view_renderer: textval %r"%(textval,))
        return '''<span>%s</span>'''%(textval)

class text_language_edit_renderer(object):

    def __init__(self):
        self._template = Template(
            '''<input type="text" size="64" name="{{repeat_prefix}}{{field.description.field_name}}" '''+
                   '''placeholder="{{field.description.field_placeholder}}" '''+
                   '''value="{{encoded_field_value}}" />'''
        )
        return

    def render(self, context):
        """
        Render language-tagged text for editing
        """
        from annalist.views.fields.render_fieldvalue import get_field_edit_value
        textval = TextLanguageValueMapper.encode(get_field_edit_value(context, ""))
        log.debug("text_language_edit_renderer: textval %r"%(textval,))
        with context.push(encoded_field_value=textval):
            result = self._template.render(context)
        return result

def get_text_language_renderer():
    """
    Return field renderer object for language-tagged text values
    """
    from annalist.views.fields.render_fieldvalue import RenderFieldValue
    return RenderFieldValue("text_language",
        view_renderer=text_language_view_renderer(), 
        edit_renderer=text_language_edit_renderer(),
        )


if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
