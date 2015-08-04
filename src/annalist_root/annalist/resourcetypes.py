"""
Annalist resource types module
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2015, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

from annalist.identifiers       import ANNAL

"""
Each resource type URI or CURIE is associated with a list of one or more file 
extensions and MIME content-types.

The first of each list indicates the value used when creating or serving a 
resource of the indicated type.  Any other values given are alternatives
that are accepted as supplying a resource that is compatible with the type.

File extensions and MIME types are presented as pairs so that an extension 
can be inferred when a MIME content-type is given, and vice versa.
"""
resource_types = (
    { ANNAL.CURIE.Text:
      [ ("txt",    "text/plain") 
      ]
    , ANNAL.CURIE.Richtext:
      [ ("md",     "text/markdown")
      , ("txt",    "text/plain")
      ]
    , ANNAL.CURIE.Image:
      [ ("png",    "image/png")
      , ("jpg",    "image/jpeg")
      , ("jpeg",   "image/jpeg")
      , ("gif",    "image/gif")
      , ("tiff",   "image/tiff")
      , ("svg",    "image/svg")
      ]
    , ANNAL.CURIE.Audio:
      [ ("mp3",    "audio/mpeg")
      , ("mp4",    "audio/mp4")
      , ("wav",    "audio/wav")
      , ("ogg",    "audio/ogg")
      #@@ needs fleshing out?
      ]
    , ANNAL.CURIE.Upload:
      [ ("md",     "text/markdown")
      , ("txt",    "text/plain")
      , ("png",    "image/png")
      , ("jpg",    "image/jpeg")
      , ("jpeg",   "image/jpeg")
      , ("gif",    "image/gif")
      , ("tiff",   "image/tiff")
      , ("svg",    "image/svg")
      ]
    })

default_types = [("dat", "application/octet-stream")]

def file_extension(typeuri):
    """
    Returns preferred file extension for resource type
    """
    return resource_types.get(typeuri, default_types)[0][0]

def content_type(typeuri):
    """
    Returns preferred MIME content-type for resource type
    """
    return resource_types.get(typeuri, default_types)[0][1]

def file_extension_for_content_type(typeuri, content_type):
    """
    Returns file extension for given content-type as an instance of a given type URI,
    or None.
    """
    for fe, ct in resource_types.get(typeuri, default_types):
        if ct == content_type:
            return fe
    return None

def content_type_for_file_extension(typeuri, file_extension):
    """
    Returns content-type for given file extension as an instance of a given type URI,
    or None.
    """
    for fe, ct in resource_types.get(typeuri, default_types):
        if fe == file_extension:
            return ct
    return None

# End.
