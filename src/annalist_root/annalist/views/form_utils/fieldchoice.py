"""
This module defines a class used to represent a choice for an 
enumerated-value field.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import re
import logging
log = logging.getLogger(__name__)

from collections import OrderedDict, namedtuple

_FieldChoice_tuple = namedtuple("FieldChoice", ("id", "value", "label", "link"))

class FieldChoice(_FieldChoice_tuple):
    """
    Class representing a choice for an enumerated field.

    >>> c1 = FieldChoice('id1', 'value1', 'label1', 'link1')
    >>> c1
    FieldChoice(id='id1', value='value1', label='label1', link='link1')
    >>> str(c1)
    "FieldChoice(id='id1', value='value1', label='label1', link='link1')"
    >>> c1.id
    'id1'
    >>> c1.value
    'value1'
    >>> c1.label
    'label1'
    >>> c1.link
    'link1'
    >>> c2 = FieldChoice(id='id2', value='value2', link='link2')
    >>> c2
    FieldChoice(id='id2', value='value2', label='value2', link='link2')
    >>> c2.id
    'id2'
    >>> c2.value
    'value2'
    >>> c2.label
    'value2'
    >>> c2.link
    'link2'
    >>> c3 = FieldChoice('id3', link='link3')
    >>> c3
    FieldChoice(id='id3', value='id3', label='id3', link='link3')
    >>> c3.id
    'id3'
    >>> c3.value
    'id3'
    >>> c3.label
    'id3'
    >>> c3.link
    'link3'
    >>> c4 = FieldChoice('')
    >>> c4
    FieldChoice(id='', value='', label='', link=None)
    """

    def __new__(_cls, id=None, value=None, label=None, link=None):
        if value is None: value = id
        if label is None: label = value
        result = super(FieldChoice, _cls).__new__(_cls, id, value, label, link)
        return result

    def add_link(self, link=None):
        return FieldChoice(self.id, self.value, self.label, link)

    def option_label(self, sep=u"\xa0\xa0\xa0"):
        """
        Returns string used for displayed option label.

        This function is used mainly for testing, to isolate details of 
        option  presentation from the majority of test cases.
        """
        if self.label:
            if ( (self.value == "%(type_id)s/%(entity_id)s") or
                 re.match(r"^\w{1,32}/\w{1,32}$", self.value) ):
                return u"%s%s(%s)"%(self.label, sep, self.value)
            else:
                return self.label
        else:
            return self.value

    def option_label_html(self, sep=u"&nbsp;&nbsp;&nbsp;"):
        """
        Variation of option_label returns HTML-encoded form of label text
        """
        return self.option_label(sep=sep)

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
