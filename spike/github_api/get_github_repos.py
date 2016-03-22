"""
Retrieve user repositories summary from GitHub

    python get_repos.py <user> <format>

Gets filtered results from an equivalent to something like:

    curl https://api.github.com/users/gklyne/repos -H "Accept: application/vnd.github.v3+json"

"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import sys
import json
from HttpSession import HTTP_Session

def get_repos(repo_base_uri, userid, format):
    session = HTTP_Session(repo_base_uri)
    (status, reason, respheaders, respbody) = session.doRequest(
        "users/%s/repos"%userid,
        reqheaders={'accept': " application/vnd.github.v3+json"}
        )
    assert status == 200, "Status = %03d"%status
    respdata = json.loads(respbody)
    for repo in respdata:
        print(format%repo)
    return

if __name__ == "__main__":
    userid = "gklyne"
    format = "- %(name)s: %(git_url)s"
    if len(sys.argv) >= 2:
        userid = sys.argv[1]
    if len(sys.argv) >= 3:
        format = sys.argv[2]
    get_repos("https://api.github.com/", userid, format)

# End.

