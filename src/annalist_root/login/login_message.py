"""
Message strings used by the login pages and associated authentication logic.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import logging
log = logging.getLogger(__name__)

USER_ID_SYNTAX          = "User ID must consist of letters, digits and '_' chacacters (%s)"
UNRECOGNIZED_PROVIDER   = "Unrecognized provider mechanism `%s` in %s"
USER_NOT_AUTHENTICATED  = "User '%s' was not authenticated by %s login service"
USER_NO_EMAIL           = "No email address associated with authenticated user %s"
USER_WRONG_EMAIL        = "Authenticated user %s email address mismatch (%s, %s)"
USER_WRONG_PASSWORD     = "Login as %s: no such user or incorrect password"
USER_ACCOUNT_DISABLED   = "Account %s has been disabled"


# End.
