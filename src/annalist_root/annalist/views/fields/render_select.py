"""
Renderer and value mapper for text values selected from a list of options.
In some cases, the ren dered edit control also inclused a button for 
creating a new value.
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
#   Select value templates
#
#   ----------------------------------------------------------------------------

view_select = (
    """<!-- fields.render_select.py -->
    {% if field.field_value_link_continuation %}
      <a href="{{field.field_value_link_continuation}}">{{field.field_value}}</a>
    {% else %}
      <span>{{field.field_value}}</span>
    {% endif %}
    """)

edit_select = (
    """<!-- field/annalist_edit_select.html -->
    <div class="row">
      <div class="small-10 columns view-value less-new-button">
        <select name="{{repeat_prefix}}{{field.field_name}}">
          {% for v in field_options %}
            {% if v == field.field_value %}
              {% if v == "" %}
                <option value="" selected="selected">{{field.field_placeholder}}</option>
              {% else %}
                <option selected="selected">{{v}}</option>
              {% endif %}
            {% else %}
              {% if v == "" %}
                <option value="">{{field.field_placeholder}}</option>
              {% else %}
                <option>{{v}}</option>
              {% endif %}
            {% endif %}
          {% endfor %}
        </select>
      </div>
      <div class="small-2 columns view-value new-button left small-text-right">
        <button type="submit" 
                name="{{repeat_prefix}}{{field.field_name}}__new" 
                value="New"
                title="Define new {{field.field_label}}"
        >
          +
        </button>
      </div>
    </div>
    """)

view_choice = (
    """<!-- fields.render_choice.py -->
    {% if field.field_value_link_continuation %}
      <a href="{{field.field_value_link_continuation}}">{{field.field_value}}</a>
    {% else %}
      <span>{{field.field_value}}</span>
    {% endif %}
    """)

edit_choice = (
    """<!-- fields.render_choice.py -->
    <select name="{{repeat_prefix}}{{field.field_name}}">
      {% for v in field_options %}
        {% if v == field.field_value %}
          {% if v == "" %}
            <option value="" selected="selected">{{field.field_placeholder}}</option>
          {% else %}
            <option selected="selected">{{v}}</option>
          {% endif %}
        {% else %}
          {% if v == "" %}
            <option value="">{{field.field_placeholder}}</option>
          {% else %}
            <option>{{v}}</option>
          {% endif %}
        {% endif %}
      {% endfor %}
    </select>
    """)


#   ----------------------------------------------------------------------------
#
#   Select text value mapping
#
#   ----------------------------------------------------------------------------


class SelectValueMapper(object):
    """
    Value mapper class for text selected from a list of choices.
    """

    @staticmethod
    def encode(data_value):
        """
        Encodes supplied data value as an option value to be selected in a 
        <select> form inbput.
        """
        return data_value or ""

    @staticmethod
    def decode(field_value):
        """
        Decodes a selected option value as a value to be stored in an 
        entity field.
        """
        return field_value

#   ----------------------------------------------------------------------------
#
#   Select text field renderers
#
#   ----------------------------------------------------------------------------

class select_view_renderer(object):
    """
    Render select value for viewing using supplied template
    """
    def __init__(self, template):
        self._template = Template(template)
        return

    def render(self, context):
        textval = SelectValueMapper.encode(get_field_value(context, None))
        with context.push(encoded_field_value=textval):
            result = self._template.render(context)
        return result

class select_edit_renderer(object):
    """
    Render select value for editing using supplied template
    """
    def __init__(self, template):
        self._template = Template(template)
        return

    def render(self, context):
        try:
            val     = get_field_value(context, None)
            textval = SelectValueMapper.encode(val)
            options = context['field']['options']
            if textval not in options:
                options = list(options)      # clone
                options.insert(0, textval)   # Add missing current value to options
            with context.push(encoded_field_value=textval, field_options=options):
                result = self._template.render(context)
        except Exception as e:
            log.error(e)
            result = str(e)
        return result

#   ----------------------------------------------------------------------------
#
#   Return render objects for select or choice controls (with or without '+' button)
#
#   ----------------------------------------------------------------------------

def get_select_renderer():
    """
    Return field renderer object for value selector (with '+' button)
    """
    return RenderFieldValue(
        view_renderer=select_view_renderer(view_select),
        edit_renderer=select_edit_renderer(edit_select),
        )

def get_choice_renderer():
    """
    Return field renderer object for value selector (without '+' button)
    """
    return RenderFieldValue(
        view_renderer=select_view_renderer(view_choice),
        edit_renderer=select_edit_renderer(edit_choice),
        )

# End.
