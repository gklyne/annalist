"""
Utilities for generating HTTP error responses,

These are intended for use by support routines.
Future revisions may provide greater application control over response details.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.http import HttpResponse

def error(values):
    """
    Default error method using errorvalues
    """
    responsebody = """
        <html>
        <head>
            <title>Error %(status)s: %(reason)s</title>
        </head>
        <body>
            <h1>Error %(status)s: %(reason)s</h1>
            <p>%(message)s</p>
            <p>Request URI: %(request_uri)s</p>
        </body>
        </html>
        """ % values
    # NOTE: requires Django 1.6 or later to allow reason parameter
    return HttpResponse(responsebody, status=values['status'], reason=values['reason'])

# Define values for display with common error cases.
def errorvalues(view, status, reason, message):
    return (
        { 'status':   status
        , 'reason':   reason
        , 'message':  message%
            { 'method':         view.request.method
            , 'request_uri':    view.request.build_absolute_uri()
            , 'accept_types':   view.request.META.get('HTTP_ACCEPT',"default_type")
            , 'content_type':   view.request.META.get('CONTENT_TYPE', "application/octet-stream")
            }
        })

def error400values(view, message="Bad request to %(request_uri)s"):
    return errorvalues(view, 400, "Bad request", message)

def error401values(view):
    return errorvalues(view, 401, "Unauthorized",
        "Resource %(request_uri)s requires authentication for access"
        )

def error402values(view):
    return errorvalues(view, 402, "Payment required",
        "Resource %(request_uri)s: payment required"
        )

def error403values(view):
    return errorvalues(view, 401, "Forbidden", 
        "Forbidden %(method)s access to resource %(request_uri)s"
        )

def error404values(view):
    return errorvalues(view, 404, "Not found", 
        "Resource %(request_uri)s not found"
        )

def error405values(view):
    return errorvalues(view, 405, "Method not allowed", 
        "Method %(method)s is not recognized for %(request_uri)s"
        )

def error406values(view):
    return errorvalues(view, 406, "Not acceptable", 
        "%(method)s returning %(accept_types)s not supported for %(request_uri)s"
        )

def error407values(view):
    return errorvalues(view, 407, "Proxy authentication required", 
        "Resource %(request_uri)s: Proxy authentication required"
        )

def error408values(view):
    return errorvalues(view, 408, "Request timeout", 
        "Resource %(request_uri)s: Request timeout"
        )

def error409values(view):
    return errorvalues(view, 409, "Requedst timeout", 
        "Resource %(request_uri)s: Requedst timeout"
        )

def error410values(view):
    return errorvalues(view, 410, "Gone", 
        "Resource %(request_uri)s: Gone"
        )

def error411values(view):
    return errorvalues(view, 411, "Length required", 
        "Resource %(request_uri)s: Length required"
        )

def error412values(view):
    return errorvalues(view, 412, "Precondition failed", 
        "Resource %(request_uri)s: Precondition failed"
        )

def error413values(view):
    return errorvalues(view, 413, "Request entity too large", 
        "Resource %(request_uri)s: Request entity too large"
        )

def error414values(view):
    return errorvalues(view, 414, "Request URI too long", 
        "Resource %(request_uri)s: Request URI too long"
        )

def error415values(view):
    return errorvalues(view, 415, "Unsupported Media Type", 
        "%(method)s with %(content_type)s not supported for %(request_uri)s"
        )

def error416values(view):
    return errorvalues(view, 416, "Requested range not satisfiable", 
        "Resource %(request_uri)s: Requested range not satisfiable"
        )

def error417values(view):
    return errorvalues(view, 417, "Expectation failed", 
        "Resource %(request_uri)s: Expectation failed"
        )

def error426values(view):
    return errorvalues(view, 426, "Upgrade required", 
        "Resource %(request_uri)s: Upgrade required"
        )

def error428values(view):
    return errorvalues(view, 428, "Precondition required", 
        "Resource %(request_uri)s: Precondition required"
        )

def error429values(view):
    return errorvalues(view, 429, "Too many requests", 
        "Resource %(request_uri)s: Too many requests"
        )

def error431values(view):
    return errorvalues(view, 431, "Request header fields too large", 
        "Resource %(request_uri)s: Request header fields too large"
        )

def error451values(view):
    return errorvalues(view, 451, "Unavailable for legal reasons", 
        "Resource %(request_uri)s: Unavailable for legal reasons"
        )

# End.
