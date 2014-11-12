#!/usr/bin/python

"""
Context manager for temporarily suppressing logging
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2014, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

class SuppressLogging:
    """
    Context handler class that suppresses logging for some controlled code.
    """
    
    def __init__(self, loglevel):
        logging.disable(loglevel)
        return
    
    def __enter__(self):
        return 

    def __exit__(self, exctype, excval, exctraceback):
        logging.disable(logging.NOTSET)
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    log.info("log this")
    with SuppressLogging(logging.WARNING):
        log.info("don't log this")
        log.warning("don't log this warning")
        log.error("log this error while up to WARNING suppressed")
    log.info("log this again")

# End.
