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

from django.utils.html import format_html, mark_safe, escape

_FieldChoice_tuple = namedtuple("FieldChoice", ("id", "value", "label", "link", "choice_value"))

class FieldChoice(_FieldChoice_tuple):
    """
    Class representing a choice for an enumerated field.

    >>> c1 = FieldChoice('id1', 'value1', 'label1', 'link1', choice_value=True)
    >>> c1
    FieldChoice(id='id1', value='value1', label='label1', link='link1', choice_value=True)
    >>> str(c1)
    "FieldChoice(id='id1', value='value1', label='label1', link='link1', choice_value=True)"
    >>> c1.id
    'id1'
    >>> c1.value
    'value1'
    >>> c1.label
    'label1'
    >>> c1.link
    'link1'
    >>> c1.choice_html()
    u'label1&nbsp;&nbsp;&nbsp;(value1)'
    >>> c2 = FieldChoice('id2', 'value2', 'label2', 'link2', choice_value=False)
    >>> c2
    FieldChoice(id='id2', value='value2', label='label2', link='link2', choice_value=False)
    >>> str(c2)
    "FieldChoice(id='id2', value='value2', label='label2', link='link2', choice_value=False)"
    >>> c2.id
    'id2'
    >>> c2.value
    'value2'
    >>> c2.label
    'label2'
    >>> c2.link
    'link2'
    >>> c2.choice()
    u'label2'
    >>> c3 = FieldChoice(id='id3', value='value3', link='link3')
    >>> c3
    FieldChoice(id='id3', value='value3', label='value3', link='link3', choice_value=False)
    >>> c3.id
    'id3'
    >>> c3.value
    'value3'
    >>> c3.label
    'value3'
    >>> c3.link
    'link3'
    >>> c4 = FieldChoice('id4', link='link4')
    >>> c4
    FieldChoice(id='id4', value='id4', label='id4', link='link4', choice_value=False)
    >>> c4.id
    'id4'
    >>> c4.value
    'id4'
    >>> c4.label
    'id4'
    >>> c4.link
    'link4'
    >>> c5 = FieldChoice('')
    >>> c5
    FieldChoice(id='', value='', label='', link=None, choice_value=False)
    """

    def __new__(_cls, id=None, value=None, label=None, link=None, choice_value=False):
        if value is None: value = id
        if label is None: label = value
        result = super(FieldChoice, _cls).__new__(_cls, id, value, label, link, choice_value)
        return result

    def choice(self, sep=u"\xa0\xa0\xa0"):
        """
        Return choice string
        """
        if self.choice_value:
            choice_text = self.option_label(sep=sep)
        else:
            choice_text = unicode(self.label)
        return choice_text

    def choice_html(self, sep=u"&nbsp;&nbsp;&nbsp;"):
        """
        Return choice string HTML for option in drop-down list.
        """
        return self.choice(sep=sep)

    def add_link(self, link=None):
        return FieldChoice(self.id, self.value, self.label, link)

    def option_label(self, sep=u"\xa0\xa0\xa0"):
        """
        Returns string used for displayed option label.

        This function is used mainly for testing, to isolate details of 
        option presentation from the majority of test cases.
        """
        if self.label:
            return format_html(u"{}{}({})", self.label, mark_safe(sep), self.value)
        else:
            return escape(self.value)

    def option_label_html(self, sep=u"&nbsp;&nbsp;&nbsp;"):
        """
        Variation of option_label returns HTML-encoded form of label text
        """
        return self.option_label(sep=sep)

def update_choice_labels(fieldchoices):
    """
    Update choice labels in supplied list of FieldChoice values so that duplicate labels can
    be distinguished.

    Returns an updated list of options.
    """
    # Detect non-unique labels
    labels = {}
    for o in fieldchoices:
        l = o.label
        labels[l] = labels.get(l, 0) + 1
    # Generate updated choice values
    new_choices = []
    for o in fieldchoices:
        if labels[o.label] > 1:
            new_choices.append(
                FieldChoice(id=o.id, value=o.value, label=o.label, link=o.link, choice_value=True)
                )
        else:
            new_choices.append(o)
    return new_choices

def get_choice_labels(fieldchoices):
    """
    Return a list of choice labels based on the supplied list of FieldChoice values

    >>> c1  = FieldChoice('id1',  'value1',  'label1', 'link1')
    >>> c2a = FieldChoice('id2a', 'value2a', 'label2', 'link2')
    >>> c2b = FieldChoice('id2b', 'value2b', 'label2', 'link2')
    >>> get_choice_labels([c1,c2a,c2b])
    [u'label1', u'label2\\xa0\\xa0\\xa0(value2a)', u'label2\\xa0\\xa0\\xa0(value2b)']
    """
    return [ fc.choice() for fc in update_choice_labels(fieldchoices) ]

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
