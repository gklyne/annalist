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
    get_context_value, 
    get_context_field_value, 
    get_field_edit_value,
    get_field_view_value,
    get_context_field_description_value
    )
from annalist.views.form_utils.fieldchoice      import FieldChoice

#   ----------------------------------------------------------------------------
#
#   Field placement render support functions
#
#   ----------------------------------------------------------------------------

# These symbols don't display will with some languages/fonts (specifically Chinese)
view_is_occupied  = "&block;"
view_not_occupied = "&blk14;"

option_is_occupied  = "#"
option_not_occupied = "."

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
    , ("small:0,12;medium:6,6right", "......###### (6/6R)")
    , ("small:0,12;medium:8,4right", "........#### (8/4R)")
    , ("small:0,12;medium:9,3right", ".........### (9/3R)")
    , ("small:0,9", "#########... (0/9col)")
    , ("small:3,9", "...######### (3/9col)")
    , ("small:0,8", "########.... (0/8col)")
    , ("small:4,8", "....######## (4/8col)")
    , ("small:0,6", "######...... (0/6col)")
    , ("small:3,6", "...######... (3/6col)")
    , ("small:6,6", "......###### (6/6col)")
    , ("small:0,4", "####........ (0/4col)")
    , ("small:4,4", "....####.... (4/4col)")
    , ("small:8,4", "........#### (8/4col)")
    , ("small:0,3", "###......... (0/3col)")
    , ("small:3,3", "...###...... (3/3col)")
    , ("small:6,3", "......###... (6/3col)")
    , ("small:9,3", ".........### (9/3col)")
    ])

def option_symbol(occupied):
    return (
        option_is_occupied  if occupied == "#" else 
        option_not_occupied if occupied == "." else occupied
        )

def option_body(occupancy):
    """
    Returns an option body string corresponding to a supplied occupancy string
    """
    return "".join([ option_symbol(c) for c in occupancy ])


def view_symbol(occupied):
    return (
        view_is_occupied  if occupied == "#" else 
        view_not_occupied if occupied == "." else occupied
        )

def view_body(occupancy):
    """
    Returns an option body string corresponding to a supplied occupancy string
    """
    return "".join([ view_symbol(c) for c in occupancy ])

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

def placement_opton_text(placement, placeholder="(select...)"):
    if placement in placement_occupancy:
        display_text = option_body(placement_occupancy[placement])
    elif placement == "":
        display_text = placeholder
    else:
        display_text = placement
    return display_text

def placement_option(placement, placeholder, placement_selected="False"):
    body_text = placement_opton_text(placement, placeholder=placeholder)
    if placement_selected:
        selected = ''' selected="selected"'''
    else:
        selected = ""
    return (
        '''<option value="%s"%s>%s</option>'''%
        (placement, selected, body_text)
        )

def placement_display_span(placement):
    if placement in placement_occupancy:
        display_text = view_body(placement_occupancy[placement])
    elif placement == "":
        display_text = placeholder
    else:
        display_text = placement
    return '''<span class="placement-text">%s</span>'''%display_text

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
        field_name        = get_context_field_description_value(
            context, 'field_name', "_unknown_"
            )
        field_placeholder = get_context_field_description_value(
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
    return RenderFieldValue("placement",
        view_renderer=placement_view_renderer(), 
        edit_renderer=placement_edit_renderer()
        )

#   ----------------------------------------------------------------------------
#
#   Internal representation of field placement and placement string parser
#
#   ----------------------------------------------------------------------------

LayoutOptions = namedtuple("LayoutOptions", ["s", "m", "l"])

Placement = namedtuple("Placement", ['width', 'offset', 'display', 'field', 'label', 'value'])

def get_placement_classes(placement):
    """
    Returns Placement classes corresponding to placement string provided.

    >>> get_placement_classes("small:0,12").field
    'small-12 columns'
    >>> get_placement_classes("small:0,12").label
    'small-12 medium-2 columns'
    >>> get_placement_classes("small:0,12").value
    'small-12 medium-10 columns'
    >>> get_placement_classes("medium:0,12")                        # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=12, m=12, l=12), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-12 columns', \
        label='small-12 medium-2 columns', \
        value='small-12 medium-10 columns')
    >>> get_placement_classes("large:0,12")                         # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=12, m=12, l=12), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-12 columns', \
        label='small-12 medium-2 columns', \
        value='small-12 medium-10 columns')

    >>> get_placement_classes("small:0,12;medium:0,4")              # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=12, m=4, l=4), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-12 medium-4 columns', \
        label='small-12 medium-6 columns', \
        value='small-12 medium-6 columns')
    >>> get_placement_classes("small:0,12; medium:0,4")             # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=12, m=4, l=4), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-12 medium-4 columns', \
        label='small-12 medium-6 columns', \
        value='small-12 medium-6 columns')

    >>> get_placement_classes("small:0,12;medium:0,6;large:0,4")    # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=12, m=6, l=4), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-12 medium-6 large-4 columns', \
        label='small-12 medium-4 large-6 columns', \
        value='small-12 medium-8 large-6 columns')

    >>> get_placement_classes("small:0,6;medium:0,4")               # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=6, m=4, l=4), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-6 medium-4 columns', \
        label='small-12 medium-6 columns', \
        value='small-12 medium-6 columns')

    >>> get_placement_classes("small:0,6;medium:0,4,right")         # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=6, m=4, l=4), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-6 medium-4 columns right', \
        label='small-12 medium-6 columns', \
        value='small-12 medium-6 columns')

    >>> get_placement_classes("small:0,6")                          # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=6, m=6, l=6), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=True, m=True, l=True), \
        field='small-6 columns', \
        label='small-12 medium-4 columns', \
        value='small-12 medium-8 columns')

    >>> get_placement_classes("small:0,12,hide;medium:0,4")         # doctest: +NORMALIZE_WHITESPACE
    Placement(width=LayoutOptions(s=12, m=4, l=4), \
        offset=LayoutOptions(s=0, m=0, l=0), \
        display=LayoutOptions(s=False, m=True, l=True), \
        field='small-12 medium-4 columns show-for-medium-up', \
        label='small-12 medium-6 columns', \
        value='small-12 medium-6 columns')
    """
    def set_field_width(pmmode, pmwidth):
        if pmwidth == 0:
            field_width[pmmode] = 0
            label_width[pmmode] = 0
            value_width[pmmode] = 0
        else:
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
    set_field_width("small",  12)       # Default small-12  columns (may be overridden)
    set_field_width("medium", 12)       # Default medium-12 columns (may be overridden)
    set_field_width("large",  12)       # Default large-12  columns (may be overridden)
    field_offset  = {'small': 0, 'medium': 0, 'large': 0}
    field_display = {'small': True, 'medium': True, 'large': True}
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
        field_offset[pmmode]  = pmoffset
        if pmhide:
            field_display[pmmode] = False
        if pmmode == "small":
            set_field_width("medium", pmwidth)
        field_offset["medium"] = pmoffset
        if pmmode in ["small", "medium"]:
            set_field_width("large", pmwidth)
            field_offset["large"] = pmoffset
    c = Placement(
            width=make_field_width(
                sw=field_width["small"], mw=field_width["medium"], lw=field_width["large"]
                ),
            offset=make_field_offset(
                so=field_offset['small'], mo=field_offset['medium'],lo=field_offset['large']
                ),
            display=make_field_display(
                sd=field_display['small'], md=field_display['medium'],ld=field_display['large']
                ),
            field=format_class(field_width, pmright, pmshow),
            label=format_class(label_width),
            value=format_class(value_width)
            )
    # log.debug("get_placement_class %s, returns %s"%(placement,c))
    return c

def make_field_width(sw=12, mw=12, lw=12):
    return LayoutOptions(s=sw, m=mw, l=lw)

def make_field_offset(so=0, mo=0, lo=0):
    return LayoutOptions(s=so, m=mo, l=lo)

def make_field_display(sd=True, md=True, ld=True):
    return LayoutOptions(s=sd, m=md, l=ld)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
