"""
This module contains support for field placement rendering
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
from collections    import OrderedDict, namedtuple

from annalist.views.fields.render_base          import RenderBase
from annalist.views.fields.render_fieldvalue    import (
    RenderFieldValue,
    get_context_value, get_context_field_value, 
    get_field_edit_value,
    get_field_view_value    
    )
from annalist.views.form_utils.fieldchoice      import FieldChoice

#   ----------------------------------------------------------------------------
#
#   Field placement render support functions
#
#   ----------------------------------------------------------------------------

# Enumerated placement options.
#
# '.' and '#' here are placeholders for symbols that will be used to show
# that a grid column is unoccupied or occupied respectively by the field.
placement_occupancy = OrderedDict(
    [ ("small:0,12"           , "############ (0/12)")
    #@@ Label width calculation doesn't work for placements not sub-multiple of 12
    #@@ (but still OK for columns)
    # , ("small:0,12;medium:0,9", "#########... (0/9)")
    # , ("small:0,12;medium:3,9", "...######### (3/9)")
    # , ("small:0,12;medium:0,8", "########.... (0/8)")
    # , ("small:0,12;medium:4,8", "....######## (4/8)")
    , ("small:0,12;medium:0,6", "######...... (0/6)")
    , ("small:0,12;medium:3,6", "...######... (3/6)")
    , ("small:0,12;medium:6,6", "......###### (6/6)")
    , ("small:0,12;medium:0,4", "####........ (0/4)")
    , ("small:0,12;medium:4,4", "....####.... (4/4)")
    , ("small:0,12;medium:8,4", "........#### (8/4)")
    , ("small:0,12;medium:0,3", "###......... (0/3)")
    , ("small:0,12;medium:3,3", "...###...... (3/3)")
    , ("small:0,12;medium:6,3", "......###... (6/3)")
    , ("small:0,12;medium:9,3", ".........### (9/3)")
    , ("small:0,12;medium:6,6right", "......###### (6/6 right)")
    , ("small:0,12;medium:8,4right", "........#### (8/4 right)")
    , ("small:0,12;medium:9,3right", ".........### (9/3 right)")
    , ("small:0,9", "#########... (0/9 column)")
    , ("small:3,9", "...######### (3/9 column)")
    , ("small:0,8", "########.... (0/8 column)")
    , ("small:4,8", "....######## (4/8 column)")
    , ("small:0,6", "######...... (0/6 column)")
    , ("small:3,6", "...######... (3/6 column)")
    , ("small:6,6", "......###### (6/6 column)")
    , ("small:0,4", "####........ (0/4 column)")
    , ("small:4,4", "....####.... (4/4 column)")
    , ("small:8,4", "........#### (8/4 column)")
    , ("small:0,3", "###......... (0/3 column)")
    , ("small:3,3", "...###...... (3/3 column)")
    , ("small:6,3", "......###... (6/3 column)")
    , ("small:9,3", ".........### (9/3 column)")
    ])

def option_symbol(occupied):
    return (
        "&block;" if occupied == "#" else 
        "&blk14;" if occupied == "." else occupied
        )

def option_body(occupancy):
    """
    Returns an option body string corresponding to a supplied occupancy string
    """
    return "".join([ option_symbol(c) for c in occupancy ])

def get_placement_options():
    return [ FieldChoice(o, label=option_body(placement_occupancy[o])) 
             for o in placement_occupancy 
           ]
    # return [ option_body(placement_occupancy[o]) for o in placement_occupancy ]
    # return placement_occupancy.keys()

def get_placement_value_option_dict():
    return { o: option_body(placement_occupancy[o]) for o in placement_occupancy }

def get_placement_option_value_dict():
    return { option_body(placement_occupancy[o]) : o for o in placement_occupancy }

def placement_display_text(placement, placeholder="(select...)"):
    if placement in placement_occupancy:
        display_text = option_body(placement_occupancy[placement])
    elif placement == "":
        display_text = placeholder
    else:
        display_text = placement
    return display_text

def placement_display_span(placement):
    return (
        '''<span class="placement-text">%s</span>'''%
        placement_display_text(placement)
        )

def placement_option(placement, placeholder, placement_selected="False"):
    body_text = placement_display_text(placement, placeholder=placeholder)
    if placement_selected:
        selected = ''' selected="selected"'''
    else:
        selected = ""
    return (
        '''<option value="%s"%s>%s</option>'''%
        (placement, selected, body_text)
        )

#   ----------------------------------------------------------------------------
#
#   Field placement field renderers
#
#   ----------------------------------------------------------------------------

class placement_view_renderer(object):

    def render(self, context):
        """
        Render field placement for viewing.
        """
        placement = get_field_view_value(context, "&nbsp;")
        if placement in placement_occupancy:
            return placement_display_span(placement)
        # Not predefined value - return string in unadorned span.
        # (Without a <span ... /> with some content, the grid layout gets messed up.
        return '''<span>%s</span>'''%(placement or "(not specified)")

class placement_edit_renderer(object):

    def render(self, context):
        """
        Render field placement for editing
        """
        repeat_prefix     = get_context_value(context, 'repeat_prefix', "")
        placement         = get_field_edit_value(context, "")
        field_name        = get_context_field_value(
            context, 'field_name', "_unknown_"
            )
        field_placeholder = get_context_field_value(
            context, 'field_placeholder', "small:0,12"
            )
        option_elem = placement_option(
            "", field_placeholder, placement_selected=(placement=="")
            )
        pref = (
            [ '''<select class="placement-text" name="%s%s">'''%
                  (repeat_prefix, field_name)
            , "  "+option_elem
            ])
        opts = []
        if placement != "" and placement not in placement_occupancy:
            option_elem = placement_option(
                placement, field_placeholder, placement_selected=True
                )
            opts.append("  "+option_elem)
        for opt in placement_occupancy:
            option_elem = placement_option(
                opt, field_placeholder, placement_selected=(placement==opt)
                )
            opts.append("  "+option_elem)
        suff = ['''</select>''']
        return '\n'.join(pref+opts+suff)

def get_field_placement_renderer():
    """
    Return field renderer object for field placement values
    """
    return RenderFieldValue(
        view_renderer=placement_view_renderer(), 
        edit_renderer=placement_edit_renderer()
        )

#   ----------------------------------------------------------------------------
#
#   Internal representation of field placement and placement string parser
#
#   ----------------------------------------------------------------------------

Placement = namedtuple("Placement", ['field', 'label', 'value'])

def get_placement_classes(placement):
    """
    Returns placement classes corresponding to placement string provided.

    >>> get_placement_classes("small:0,12").field
    'small-12 columns'
    >>> get_placement_classes("small:0,12").label
    'small-12 medium-2 columns'
    >>> get_placement_classes("small:0,12").value
    'small-12 medium-10 columns'
    >>> get_placement_classes("medium:0,12")
    Placement(field='small-12 columns', label='small-12 medium-2 columns', value='small-12 medium-10 columns')
    >>> get_placement_classes("large:0,12")
    Placement(field='small-12 columns', label='small-12 medium-2 columns', value='small-12 medium-10 columns')

    >>> get_placement_classes("small:0,12;medium:0,4")
    Placement(field='small-12 medium-4 columns', label='small-12 medium-6 columns', value='small-12 medium-6 columns')
    >>> get_placement_classes("small:0,12; medium:0,4")
    Placement(field='small-12 medium-4 columns', label='small-12 medium-6 columns', value='small-12 medium-6 columns')

    >>> get_placement_classes("small:0,12;medium:0,6;large:0,4")
    Placement(field='small-12 medium-6 large-4 columns', label='small-12 medium-4 large-6 columns', value='small-12 medium-8 large-6 columns')
    >>> get_placement_classes("small:0,6;medium:0,4")
    Placement(field='small-6 medium-4 columns', label='small-12 medium-6 columns', value='small-12 medium-6 columns')
    >>> get_placement_classes("small:0,6;medium:0,4,right")
    Placement(field='small-6 medium-4 columns right', label='small-12 medium-6 columns', value='small-12 medium-6 columns')
    >>> get_placement_classes("small:0,6")
    Placement(field='small-6 columns', label='small-12 medium-4 columns', value='small-12 medium-8 columns')

    >>> get_placement_classes("small:0,12,hide;medium:0,4")
    Placement(field='small-12 medium-4 columns show-for-medium-up', label='small-12 medium-6 columns', value='small-12 medium-6 columns')
    """
    def set_field_width(pmmode, pmwidth):
        field_width[pmmode] = pmwidth
        label_width[pmmode] = labelw[pmmode]*(12 // pmwidth)
        value_width[pmmode] = 12 - label_width[pmmode]
        if label_width[pmmode] >= 12:
            label_width[pmmode] = 12
            value_width[pmmode] = 12
        return
    def format_class(cd, right="", show=""):
        prev = cd.get("small", None)
        for test in ("medium", "large"):
            if (test in cd):
                if cd[test] == prev:
                    del cd[test]
                else:
                    prev = cd[test]
        if right: right = " "+right
        if show:  show  = " "+show
        return " ".join([k+"-"+str(v) for k,v in cd.items()]) + " columns" + right + show
    ppr = re.compile(r"^(small|medium|large):(\d+),(\d+),?(right)?,?(hide)?$")
    ps = [ s.strip() for s in placement.split(';') ]
    labelw      = {'small': 12, 'medium': 2, 'large': 2}
    field_width = OrderedDict()
    label_width = OrderedDict()
    value_width = OrderedDict()
    pmright     = ""
    pmshow      = ""
    set_field_width("small", 12)        # Default small-12 columns (may be overridden)
    set_field_width("medium", 12)       # Default medium-12 columns (may be overridden)
    # Process each placement sub-expression
    for p in ps:
        pm = ppr.match(p)
        if not pm:
            break
        pmmode   = pm.group(1)      # "small", "medium" or "large"
        pmoffset = int(pm.group(2))
        pmwidth  = int(pm.group(3))
        pmright  = pm.group(4) or ""
        pmhide   = pm.group(5)
        if pmhide:
            pmshow = {'small': "show-for-medium-up", 'medium': "show-for-large-up", 'large': ""}[pmmode]
            # print "pmhide %s, pmmode %s, pmshow %s"%(pmhide, pmmode, pmshow)
        set_field_width(pmmode, pmwidth)
        if pmmode == "small":
            set_field_width("medium", pmwidth)
    c = Placement(
            field=format_class(field_width, pmright, pmshow),
            label=format_class(label_width),
            value=format_class(value_width)
            )
    # log.debug("get_placement_class %s, returns %s"%(placement,c))
    return c

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
