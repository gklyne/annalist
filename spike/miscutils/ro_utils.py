# ro_utils.py

"""
Research Object management supporting utility functions
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os.path
from xml.dom import minidom
try:
    # Running Python 2.5 with simplejson?
    import simplejson as json
except ImportError:
    import json
import re
import logging
log = logging.getLogger(__name__)

CONFIGFILE = ".ro_config"

class EvoType:
    LIVE=0
    SNAPSHOT=1
    ARCHIVE=2
    UNDEFINED=3

def ronametoident(name):
    """
    Turn resource object name into an identifier containing only letters, digits and underscore characters
    """
    name = re.sub(r"\s", '_', name)         # spaces, etc. -> underscores
    name = re.sub(r"\W", "", name)          # Non-identifier characters -> remove
    return name

def progname(args):
    return os.path.basename(args[0])

def ropath(ro_config, dir):
    rodir  = os.path.abspath(dir)
    robase = os.path.realpath(ro_config['robase'])
    log.debug("ropath: rodir  %s"%(rodir))
    log.debug("ropath: robase %s"%(robase))
    if os.path.isdir(rodir) and os.path.commonprefix([robase, os.path.realpath(rodir)]) == robase:
       return rodir
    return None

def configfilename(configbase):
    return os.path.abspath(configbase+"/"+CONFIGFILE)

def writeconfig(configbase, config):
    """
    Write supplied configuration dictionary to indicated directory
    """
    configfile = open(configfilename(configbase), 'w')
    json.dump(config, configfile, indent=4)
    configfile.write("\n")
    configfile.close()
    return

def resetconfig(configbase):
    """
    Reset configuration in indicated directory
    """
    ro_config = {
        "robase":               None,
        "rosrs_uri":            None,
        "rosrs_access_token":   None,
        "username":             None,
        "useremail":            None,
        "annotationTypes":      None,
        "annotationPrefixes":   None,
        }
    writeconfig(configbase, ro_config)
    return

def readconfig(configbase):
    """
    Read configuration in indicated directory and return as a dictionary
    """
    ro_config = {
        "robase":               None,
        "rosrs_uri":            None,
        "rosrs_access_token":   None,
        "username":             None,
        "useremail":            None,
        "annotationTypes":      None,
        "annotationPrefixes":   None,
        }
    configfile = None
    try:
        configfile = open(configfilename(configbase), 'r')
        ro_config  = json.load(configfile)
    finally:
        if configfile: configfile.close()
    return ro_config

def mapmerge(f1, l1, f2, l2):
    """
    Helper function to merge lists of values with different map functions.
    A sorted list is returned containing f1 mapped over the elements of l1 and 
    f2 mapped over the elements ofd l2 that are not in l1; i.e. roughly:

    return sorted([ f1(i1) for i1 in l1 ] + [ f2(i2) for i2 in l2 if i2 not in l1 ])

    The actual code is a little more complex because the final sort is based on the
    original list values rather than the mapped values.
    """    
    def mm(f1, l1, f2, l2, acc):
        if len(l1) == 0: return acc + map(f2, l2)
        if len(l2) == 0: return acc + map(f1, l1)
        if l1[0] < l2[0]: return mm(f1, l1[1:], f2, l2, acc+[f1(l1[0])])
        if l1[0] > l2[0]: return mm(f1, l1, f2, l2[1:], acc+[f2(l2[0])])
        # List heads equal: choose preferentially from l1
        return mm(f1, l1[1:], f2, l2[1:], acc+[f1(l1[0])])
    return mm(f1, sorted(l1), f2, sorted(l2), [])

def prepend_f(pref):
    """
    Returns a function that prepends prefix 'pref' to a supplied string
    """
    return lambda s:pref+s

def testMap():
    l1 = ["a", "b", "d", "e"]
    l2 = ["a", "c"]
    assert mapmerge(prepend_f("1:"), l1, prepend_f("2:"), l2) == ["1:a", "1:b", "2:c", "1:d", "1:e"]
    l1 = ["d", "a"]
    l2 = ["f", "e", "c", "a"]
    assert mapmerge(prepend_f("1:"), l1, prepend_f("2:"), l2) == ["1:a", "2:c", "1:d", "2:e", "2:f"]

def parse_job(rosrs,uri):
    nodes = minidom.parseString(rosrs.doRequest(uri)[-1])
    job_status = nodes.getElementsByTagName("status")[0].firstChild.nodeValue
    target_id = nodes.getElementsByTagName("target")[0].firstChild.nodeValue
    if len(nodes.getElementsByTagName("processed_resources")) == 1 and len(nodes.getElementsByTagName("submitted_resources")) == 1 :
        processed_resources = nodes.getElementsByTagName("processed_resources")[0].firstChild.nodeValue
        submitted_resources = nodes.getElementsByTagName("submitted_resources")[0].firstChild.nodeValue
        return (job_status, target_id, processed_resources, submitted_resources)
    return (job_status, target_id)

# End.
