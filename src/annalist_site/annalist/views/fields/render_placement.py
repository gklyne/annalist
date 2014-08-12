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
    >>> get_placement_classes("small:0,6;medium:0,4right")
    Placement(field='small-6 medium-4 right columns', label='small-12 medium-6 columns', value='small-12 medium-6 columns')
    """
    def format_class(cd, right):
        prev = cd.get("small", None)
        for test in ("medium", "large"):
            if (test in cd):
                if cd[test] == prev:
                    del cd[test]
                else:
                    prev = cd[test]
        if right: right = " right"
        return " ".join([k+"-"+str(v) for k,v in cd.items()]) + right + " columns"
    ppr = re.compile(r"^(small|medium|large):(\d+),(\d+)(right)?$")
    ps = [ s.strip() for s in placement.split(';') ]
    labelw      = {'small': 12, 'medium': 2, 'large': 2}
    field_width = OrderedDict([ ('small', 12) ])
    label_width = OrderedDict([ ('small', 12), ('medium',  2) ])
    value_width = OrderedDict([ ('small', 12), ('medium',  10) ])
    for p in ps:
        pm = ppr.match(p)
        if not pm:
            break
        pmmode   = pm.group(1)      # "small", "medium" or "large"
        pmoffset = int(pm.group(2))
        pmwidth  = int(pm.group(3))
        pmright  = pm.group(4) or ""
        field_width[pmmode] = pmwidth
        label_width[pmmode] = labelw[pmmode]*(12 // pmwidth)
        value_width[pmmode] = 12 - label_width[pmmode]
        if label_width[pmmode] >= 12:
            label_width[pmmode] = 12
            value_width[pmmode] = 12
    c = Placement(
            field=format_class(field_width, pmright),
            label=format_class(label_width, ""),
            value=format_class(value_width, "")
            )
    log.debug("get_placement_class %s, returns %s"%(placement,c))
    return c

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
