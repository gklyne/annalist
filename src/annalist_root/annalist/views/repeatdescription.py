"""
Define class to represent a repeated field group when processing an entity view.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.identifiers           import RDFS, ANNAL

class RepeatDescription(object):
    """
    Describes information relating to a repeated field group used with entity-value maps when
    processing an entity view description, and methods to perform manipulations involving the 
    repeated field group.
    """

    def __init__(self, repeat):
        """
        Creates a repeated field group description value to use in a context value when
        rendering a form.

        The RepeatDescription object behaves as a dictionary containing the various 
        repeat group attributes.

        repeat      is the repeated field description in the view description.
        """
        self._repeat_context = (
            { 'repeat_id':              repeat[ANNAL.CURIE.repeat_id]
            , 'repeat_label':           repeat[ANNAL.CURIE.repeat_label]
            , 'repeat_label_add':       repeat[ANNAL.CURIE.repeat_label_add]
            , 'repeat_label_delete':    repeat[ANNAL.CURIE.repeat_label_delete]
            , 'repeat_entity_values':   repeat[ANNAL.CURIE.repeat_entity_values]
            , 'repeat_context_values':  repeat[ANNAL.CURIE.repeat_context_values]
            })
        return

    def get_structure_description(self):
        """
        Helper function returns structure description information
        """
        return self._repeat_context

    def __repr__(self):
        return "RepeatDescription.repeat context: %r"%(self._repeat_context)

    # Define methods to facilitate access to values using dictionary operations
    # on the RepeatDescription object

    def keys(self):
        """
        Return collection metadata value keys
        """
        return self._repeat_context.keys()

    def items(self):
        """
        Return collection metadata value fields
        """
        return self._repeat_context.items()

    def get(self, key, default):
        """
        Equivalent to dict.get() function
        """
        return self[key] if self._repeat_context and key in self._repeat_context else default

    def __getitem__(self, k):
        """
        Allow direct indexing to access collection metadata value fields
        """
        return self._repeat_context[k]

    def __setitem__(self, k, v):
        """
        Allow direct indexing to update collection metadata value fields
        """
        self._repeat_context[k] = v
        return

    def __iter__(self):
        """
        Iterator over dictionary keys
        """
        for k in self._repeat_context:
            yield k
        return

# End.
