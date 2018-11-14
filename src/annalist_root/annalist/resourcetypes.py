# pylint: disable=no-member, redefined-outer-name

"""
Annalist resource types module
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

# import logging
# log = logging.getLogger(__name__)

from annalist.identifiers       import ANNAL

# """
# Each resource type URI or CURIE is associated with a list of one or more file 
# extensions and MIME content-types.
#
# The first of each list indicates the value used when creating or serving a 
# resource of the indicated type.  Any other values given are alternatives
# that are accepted as supplying a resource that is compatible with the type.
#
# File extensions and MIME types are presented as pairs so that an extension 
# can be inferred when a MIME content-type is given, and vice versa.
# """
resource_types = (
    { ANNAL.CURIE.Metadata:
      [ ("jsonld",  "application/ld+json")
      , ("json",    "application/json")
      ]
    , ANNAL.CURIE.Text:
      [ ("txt",     "text/plain") 
      ]
    , ANNAL.CURIE.Richtext:
      [ ("md",      "text/markdown")
      , ("txt",     "text/plain")
      ]
    , ANNAL.CURIE.Image:
      [ ("image",   "image/*")      # Default extension
      , ("png",     "image/png")
      , ("jpg",     "image/jpeg")
      , ("jpeg",    "image/jpeg")
      , ("gif",     "image/gif")
      , ("tiff",    "image/tiff")
      , ("svg",     "image/svg")
      , ("pdf",     "application/pdf")
      ]
    , ANNAL.CURIE.Audio:
      [ ("audio",   "audio/*")      # Default extension
      , ("mp3",     "audio/mpeg")
      , ("mp4",     "audio/mp4")
      , ("wav",     "audio/wav")
      , ("ogg",     "audio/ogg")
      #@@ needs fleshing out?
      ]
    , ANNAL.CURIE.Resource:
      [ ("md",      "text/markdown")
      , ("txt",     "text/plain")
      , ("png",     "image/png")
      , ("jpg",     "image/jpeg")
      , ("jpeg",    "image/jpeg")
      , ("gif",     "image/gif")
      , ("tiff",    "image/tiff")
      , ("svg",     "image/svg")
      , ("pdf",     "application/pdf")
      ]
    })

default_types = [("dat", "application/octet-stream")]

def file_extension(typeuri):
    """
    Returns preferred file extension for resource type

    >>> file_extension(ANNAL.CURIE.Metadata) == "jsonld"
    True
    >>> file_extension(ANNAL.CURIE.Richtext) == "md"
    True

    """
    return resource_types.get(typeuri, default_types)[0][0]

def content_type(typeuri):
    """
    Returns preferred MIME content-type for resource type

    >>> content_type(ANNAL.CURIE.Metadata) == "application/ld+json"
    True
    >>> content_type(ANNAL.CURIE.Richtext) == "text/markdown"
    True

    """
    return resource_types.get(typeuri, default_types)[0][1]

def file_extension_for_content_type(typeuri, content_type):
    """
    Returns file extension for given content-type as an instance of a given type URI,
    or None.

    >>> file_extension_for_content_type(ANNAL.CURIE.Richtext, "text/markdown") == "md"
    True
    >>> file_extension_for_content_type(ANNAL.CURIE.Resource, "text/markdown") == "md"
    True
    >>> file_extension_for_content_type(ANNAL.CURIE.Resource, "application/pdf") == "pdf"
    True
    >>> file_extension_for_content_type(ANNAL.CURIE.Resource, "application/unknown") == None
    True

    """
    for fe, ct in resource_types.get(typeuri, default_types):
        if ct == content_type:
            return fe
    return None

def content_type_for_file_extension(typeuri, file_extension):
    """
    Returns content-type for given file extension as an instance of a given type URI,
    or None.

    >>> content_type_for_file_extension(ANNAL.CURIE.Richtext, "md") == "text/markdown"
    True
    >>> content_type_for_file_extension(ANNAL.CURIE.Resource, "md") == "text/markdown"
    True
    >>> content_type_for_file_extension(ANNAL.CURIE.Resource, "pdf") == "application/pdf"
    True
    >>> content_type_for_file_extension(ANNAL.CURIE.Resource, "unknown") == None
    True

    """
    for fe, ct in resource_types.get(typeuri, default_types):
        if fe == file_extension:
            return ct
    return None

if __name__ == "__main__":
    import doctest
    doctest.testmod()

# End.
