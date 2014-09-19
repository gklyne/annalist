"""
Retrieve issues list summary from GitHub

    python get_issues.py <milkestone>

Gets filtered results from an equivalent to something like:

    curl https://api.github.com/repos/gklyne/annalist/issues -H "Accept: application/vnd.github.v3+json"

"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import json
from miscutils.HttpSession import HTTP_Session


def get_issues(repo_base_uri, milestone=None):
    session = HTTP_Session(repo_base_uri)
    (status, reason, respheaders, respbody) = session.doRequest(
        "repos/gklyne/annalist/issues?state=all",
        reqheaders={'accept': " application/vnd.github.v3+json"}
        )
    assert status == 200
    respdata = json.loads(respbody)
    for issue in respdata:
        if  ( not milestone or 
              ( 'milestone' in issue and issue['milestone'] is not None and
                ( milestone == issue['milestone']['title'] or
                  milestone == str(issue['milestone']['num'])
                )
              )
            ):
            closed = "[ ]" if issue['state'] == "open" else "[x]"
            print(
                "- %s "%closed +
                "%(title)s [#%(number)s](%(url)s)"%issue
                )
    return

if __name__ == "__main__":
    milestone = None
    if len(sys.argv) >= 2:
        milestone = sys.argv[1]
    get_issues("https://api.github.com/", milestone)

# End.
