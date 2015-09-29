"""
Renderer and value mapper for text values selected from a list of options.
In some cases, the ren dered edit control also inclused a button for 
creating a new value.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import traceback
import logging
log = logging.getLogger(__name__)

from annalist               import message
from annalist.exceptions    import TargetIdNotFound_Error, TargetEntityNotFound_Error
from annalist.util          import fill_type_entity_id

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_field_edit_value,
    get_field_view_value
    )
from annalist.views.form_utils.fieldchoice      import FieldChoice

from django.template        import Template, Context

#   ----------------------------------------------------------------------------
#
#   Select value templates
#
#   ----------------------------------------------------------------------------

# @@TODO: remove references to field value and special case code in bound_field.
#         the continuation URI will need to be provided separately in the context
#         and mentioned separately in the templates

edit_options = (
    '''{% for opt in field_options %} '''+
      '''{% if opt.value == encoded_field_value %} '''+
        '''{% if opt.value == "" %} '''+
          '''<option value="" selected="selected">{{field.field_placeholder}}</option>\n'''+
        '''{% else %} '''+
          '''<option value="{{opt.value}}" selected="selected">{{opt.label}}</option>\n'''+
        '''{% endif %} '''+
      '''{% else %} '''+
        '''{% if opt.value == "" %} '''+
          '''<option value="">{{field.field_placeholder}}</option>\n'''+
        '''{% else %} '''+
          '''<option value="{{opt.value}}">{{opt.label}}</option>\n'''+
        '''{% endif %} '''+
      '''{% endif %} '''+
    '''{% endfor %} '''
    )

view_select = (
    """<!-- fields.render_select.view_select -->
    {% if field_linkval %}
      <a href="{{field_linkval}}">{{field_labelval}}</a>
    {% elif field_textval and field_textval != "" %}
      <span class="value-missing">{{field_labelval}}</span>
    {% else %}
    <span class="value-blank">"""+
      message.NO_SELECTION%{'id': "{{field.field_label}}"}+
    """</span>
    {% endif %}
    """)

edit_select = (
    """<!-- fields.render_select.edit_select -->
    <div class="row"> 
      <div class="small-10 columns view-value less-new-button">
        <select name="{{repeat_prefix}}{{field.field_name}}">
    """+
    edit_options+
    """
        </select>
      </div>
      <div class="small-2 columns view-value new-button left small-text-right">
        <button type="submit" 
                name="{{repeat_prefix}}{{field.field_name}}__new_edit" 
                value="New"
                title="Define new {{field.field_label}}"
        >
          <span class="select-edit-button-text">+&#x270D;</span>
        </button>
      </div>
    </div>
    """)

view_choice = (
    """<!-- fields.render_select.view_choice -->
    {% if field_linkval %}
      <a href="{{field_linkval}}">{{field_labelval}}</a>
    {% elif field_textval and field_textval != "" %}
      <span class="value-missing">{{field_labelval}}</span>
    {% else %}
    <span class="value-blank">"""+
      message.NO_SELECTION%{'id': "{{field.field_label}}"}+
    """</span>
    {% endif %}
    """)

edit_choice = (
    """<!-- fields.render_select.edit_choice -->
    <select name="{{repeat_prefix}}{{field.field_name}}">
    """+
    edit_options+
    """
    </select>
    """)

view_entitytype = (
    """<!-- fields.render_select.view_entitytype -->
    {% if field_linkval %}
      <a href="{{field_linkval}}">{{field_labelval}}</a>
    {% elif field_textval and field_textval != "" %}
      <span class="value-missing">{{field_labelval}}</span>
    {% else %}
    <span class="value-blank">"""+
      message.NO_SELECTION%{'id': "{{field.field_label}}"}+
    """</span>
    {% endif %}
    """)

edit_entitytype = (
    # Note use of fixed field name
    """<!-- fields.render_select.edit_entitytype -->
    <select name="entity_type">
    """+
    edit_options+
    """
    </select>
    """)

view_view_choice = (
    """<!-- field/annalist_view_view_choice.html -->
    <span>{{field.field_value}}</span>
    """)

edit_view_choice = (
    """<!-- field/annalist_edit_view_choice.html -->
    <div class="row">
      <div class="small-9 columns">
        <select name="{{repeat_prefix}}{{field.field_name}}">
        """+
        edit_options+
        """
        </select>
      </div>
      <div class="small-3 columns">
        <input type="submit" name="use_view" value="Show view" />
      </div>
    </div>
    """)

#   ----------------------------------------------------------------------------
#
#   Select text value mapping
#
#   ----------------------------------------------------------------------------

class SelectValueMapper(RenderBase):
    """
    Value mapper class for text selected from a list of choices.
    """

    @classmethod
    def encode(cls, data_value):
        """
        Encodes supplied data value as an option value to be selected in a 
        <select> form input.
        """
        return data_value or ""

#   ----------------------------------------------------------------------------
#
#   Select text field renderers
#
#   ----------------------------------------------------------------------------

class Select_view_renderer(object):
    """
    Render select value for viewing using supplied template

    """
    def __init__(self, template):
        self._template = Template(template)
        return

    def render(self, context):
        try:
            # val      = get_field_view_value(context, None)
            val      = get_field_edit_value(context, None)
            typval   = fill_type_entity_id(val, context['field']['field_ref_type'])
            textval  = SelectValueMapper.encode(typval)
            labelval = textval
            linkval  = None
            linkcont = context['field']['continuation_param']
            options  = context['field']['options']
            for o in options:
                log.info("Select_view_renderer.render: option %r"%(o,))
                if textval == o.value:
                    labelval = o.label
                    linkval  = o.link
                    break
            log.info(
                "Select_view_renderer.render: textval %s, labelval %s, linkval %s"%
                (textval, labelval, linkval)
                )
        except TargetIdNotFound_Error as e:
            log.debug(repr(e))
            textval = ""
        except TargetEntityNotFound_Error as e:        
            log.debug(repr(e))
            textval = repr(e)
        except Exception as e:
            log.error(repr(e))
            textval = repr(e)
        with context.push(
            field_textval=textval, 
            field_labelval=labelval, 
            field_linkval=linkval,
            field_continuation_param=linkcont):
            try:
                result = self._template.render(context)
            except Exception as e:
                log.error(repr(e))
                result = repr(e)
        log.debug("Select_view_renderer.render: result %r"%(result,))
        return result

class Select_edit_renderer(object):
    """
    Render select value for editing using supplied template
    """
    def __init__(self, template):
        self._template = Template(template)
        return

    def render(self, context):
        try:
            val     = get_field_edit_value(context, None) or ""
            # Use refer-to type if value does not include type..
            typval  = fill_type_entity_id(val, context['field']['field_ref_type'])
            textval = SelectValueMapper.encode(typval)
            options = context['field']['options']
            # options is a list of FieldChoice values
            # print repr(options)
            if textval not in [ o.value for o in options ]:
                options = list(options)                   # clone
                options.insert(0, FieldChoice(textval))   # Add missing current value to options
            with context.push(encoded_field_value=textval, field_options=options):
                result = self._template.render(context)
        except Exception as e:
            log.exception("Exception in Select_edit_renderer.render")
            log.error("Select_edit_renderer.render: "+repr(e))
            # log.error("Field val %r"%(val,))
            # log.error("Field name %r"%(context['field']['field_name'],))
            # log.error("Field type ref %r"%(context['field']['field_ref_type'],))
            # ex_type, ex, tb = sys.exc_info()
            # traceback.print_tb(tb)
            result = repr(e)
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
        view_renderer=Select_view_renderer(view_select),
        edit_renderer=Select_edit_renderer(edit_select),
        )

def get_choice_renderer():
    """
    Return field renderer object for value selector (without '+' button)
    """
    return RenderFieldValue(
        view_renderer=Select_view_renderer(view_choice),
        edit_renderer=Select_edit_renderer(edit_choice),
        )

def get_entitytype_renderer():
    """
    Return field renderer object for entitytype
    """
    return RenderFieldValue(
        view_renderer=Select_view_renderer(view_entitytype),
        edit_renderer=Select_edit_renderer(edit_entitytype),
        )

def get_view_choice_renderer():
    """
    Return field renderer object for entitytype
    """
    return RenderFieldValue(
        view_renderer=Select_view_renderer(view_view_choice),
        edit_renderer=Select_edit_renderer(edit_view_choice),
        )

# End.
