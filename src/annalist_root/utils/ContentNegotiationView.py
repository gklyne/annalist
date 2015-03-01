"""
View class with logic for content negotiation, and more
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2014, G. Klyne and University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from django.http import HttpResponse
from django.views import generic

class ContentNegotiationView(generic.View):
    """
    Generic view class with content negotiation decorators and generic error value methods

    Note: generic.View dispatcher assigns HTTPRequest object to self.request. 
    """

    @staticmethod
    def accept_types(types):
        """
        Decorator to use associated function to render the indicated content types 
        """
        def decorator(func):
            def guard(self, *values):
                accept_header = self.request.META.get('HTTP_ACCEPT', "*/*")
                accept_types  = [ a.split(';')[0].strip().lower() 
                                  for a in accept_header.split(',') ]
                for t in types:
                    if t in accept_types:
                        return func(self, *values)
                return None
            return guard
        return decorator

    @staticmethod
    def content_types(types):
        """
        Decorator to use associated function when supplied with the indicated content types 
        """
        def decorator(func):
            def guard(self, *values):
                content_type = self.request.META.get('CONTENT_TYPE', "application/octet-stream")
                if content_type.split(';')[0].strip().lower() in types:
                    return func(self, *values)
                return None
            return guard
        return decorator

    def get_request_uri(self):
        """
        Utility function returns URI of current request
        (useful when building new URIs with POST, etc.)

        Cf. https://docs.djangoproject.com/en/dev/ref/request-response/#methods
        """
        return self.request.build_absolute_uri()

    def get_request_host(self):
        """
        Utility function returns base URI with HOST part of current request

        @@TODO: return scheme part of the request.  request.scheme is introduced in recent Django

        Cf. https://docs.djangoproject.com/en/dev/ref/request-response/#methods
        """
        scheme = "https" if self.request.is_secure() else "http"
        return "%s://%s"%(scheme, self.request.get_host())

    def get_request_path(self):
        """
        Utility function returns path of current request URI.

        Cf. https://docs.djangoproject.com/en/dev/ref/request-response/#methods
        """
        return self.request.get_full_path()

    # Define values for display with common error cases.
    #
    # @@TODO: This should really be a separate mixin.
    #         Use http_errors module
    def error(self, values):
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
            </body>
            </html>
            """ % values
        return HttpResponse(responsebody, status=values['status'], reason=values['reason'])

    def errorvalues(self, status, reason, message):
        return (
            { 'status':   status
            , 'reason':   reason
            , 'message':  message%
                { 'method':         self.request.method
                , 'request_uri':    self.request.build_absolute_uri()
                , 'accept_types':   self.request.META.get('HTTP_ACCEPT',"default_type")
                , 'content_type':   self.request.META.get('CONTENT_TYPE', "application/octet-stream")
                }
            })

    # def error401values(self):
    #     return self.errorvalues(401, "Unauthorized", 
    #         "Resource %(request_uri)s requires authentication for access"
    #         )

    # def error403values(self):
    #     return self.errorvalues(401, "Forbidden", 
    #         "Forbidden %(method)s access to resource %(request_uri)s"
    #         )

    # def error404values(self):
    #     return self.errorvalues(404, "Not found", 
    #         "Resource %(request_uri)s not found"
    #         )

    # def error405values(self):
    #     return self.errorvalues(405, "Method not allowed", 
    #         "Method %(method)s is not recognized for %(request_uri)s"
    #         )

    # def error406values(self):
    #     return self.errorvalues(406, "Not acceptable", 
    #         "%(method)s returning %(accept_types)s not supported for %(request_uri)s"
    #         )

    # def error415values(self):
    #     return self.errorvalues(415, "Unsupported Media Type", 
    #         "%(method)s with %(content_type)s not supported for %(request_uri)s"
    #         )

    def error400values(self, message="Bad request to %(request_uri)s"):
        return self.errorvalues(400, "Bad request", message)

    def error401values(self, scope="%(method)s"):
        msg = "Resource %s requires authentication for %s access"%("%(request_uri)s", scope)
        return self.errorvalues(401, "Unauthorized", msg)

    def error402values(self):
        return self.errorvalues(402, "Payment required",
            "Resource %(request_uri)s: payment required"
            )

    # def error403values(self):
    #     return self.errorvalues(403, "Forbidden", 
    #         "Forbidden %(method)s access to resource %(request_uri)s"
    #         )

    def error403values(self, scope="%(method)s"):
        msg = "No %s access permission for resource %s"%(scope, "%(request_uri)s")
        return self.errorvalues(403, "Forbidden", msg)

    def error404values(self):
        return self.errorvalues(404, "Not found", 
            "Resource %(request_uri)s not found"
            )

    def error405values(self):
        return self.errorvalues(405, "Method not allowed", 
            "Method %(method)s is not recognized for %(request_uri)s"
            )

    def error406values(self):
        return self.errorvalues(406, "Not acceptable", 
            "%(method)s returning %(accept_types)s not supported for %(request_uri)s"
            )

    def error407values(self):
        return self.errorvalues(407, "Proxy authentication required", 
            "Resource %(request_uri)s: Proxy authentication required"
            )

    def error408values(self):
        return self.errorvalues(408, "Request timeout", 
            "Resource %(request_uri)s: Request timeout"
            )

    def error409values(self):
        return self.errorvalues(409, "Requedst timeout", 
            "Resource %(request_uri)s: Requedst timeout"
            )

    def error410values(self):
        return self.errorvalues(410, "Gone", 
            "Resource %(request_uri)s: Gone"
            )

    def error411values(self):
        return self.errorvalues(411, "Length required", 
            "Resource %(request_uri)s: Length required"
            )

    def error412values(self):
        return self.errorvalues(412, "Precondition failed", 
            "Resource %(request_uri)s: Precondition failed"
            )

    def error413values(self):
        return self.errorvalues(413, "Request entity too large", 
            "Resource %(request_uri)s: Request entity too large"
            )

    def error414values(self):
        return self.errorvalues(414, "Request URI too long", 
            "Resource %(request_uri)s: Request URI too long"
            )

    def error415values(self):
        return self.errorvalues(415, "Unsupported Media Type", 
            "%(method)s with %(content_type)s not supported for %(request_uri)s"
            )

    def error416values(self):
        return self.errorvalues(416, "Requested range not satisfiable", 
            "Resource %(request_uri)s: Requested range not satisfiable"
            )

    def error417values(self):
        return self.errorvalues(417, "Expectation failed", 
            "Resource %(request_uri)s: Expectation failed"
            )

    def error426values(self):
        return self.errorvalues(426, "Upgrade required", 
            "Resource %(request_uri)s: Upgrade required"
            )

    def error428values(self):
        return self.errorvalues(428, "Precondition required", 
            "Resource %(request_uri)s: Precondition required"
            )

    def error429values(self):
        return self.errorvalues(429, "Too many requests", 
            "Resource %(request_uri)s: Too many requests"
            )

    def error431values(self):
        return self.errorvalues(431, "Request header fields too large", 
            "Resource %(request_uri)s: Request header fields too large"
            )

    def error451values(self):
        return self.errorvalues(451, "Unavailable for legal reasons", 
            "Resource %(request_uri)s: Unavailable for legal reasons"
            )

    def error500values(self, message="Server error from request to %(request_uri)s"):
        return self.errorvalues(500, "Server error", message)

# End.
