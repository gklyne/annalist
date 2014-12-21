"""
This module contains utilities for use in conjunction with field renderers.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

import re
from collections                    import OrderedDict, namedtuple

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
