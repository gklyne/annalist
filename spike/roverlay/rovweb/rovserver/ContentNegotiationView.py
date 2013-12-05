
__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
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
            def guard(self, values):
                accept_header = self.request.META.get('HTTP_ACCEPT', "*/*")
                accept_types  = [ a.split(';')[0].strip().lower() 
                                  for a in accept_header.split(',') ]
                for t in types:
                    if t in accept_types:
                        values['accept_type'] = t
                        return func(self, values)
                return None
            return guard
        return decorator

    @staticmethod
    def content_types(types):
        """
        Decorator to use associated function when supplied with the indicated content types 
        """
        def decorator(func):
            def guard(self, values):
                content_type = self.request.META.get('CONTENT_TYPE', "application/octet-stream")
                if content_type.split(';')[0].strip().lower() in types:
                    return func(self, values)
                return None
            return guard
        return decorator

    def get_request_uri(self):
        """
        Utility function returns URI of current request
        (useful when building new URIs with POST, etc.)
        """
        return self.request.build_absolute_uri()

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
        # @@TODO: with Django 1.6, can also set reason string
        return HttpResponse(responsebody, status=values['status'])

    # Define values for display with common error cases.
    # @@TODO: This should really be a separate mixin.  Needs fleshing out.
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

    def error415values(self):
        return self.errorvalues(415, "Unsupported Media Type", 
            "%(method)s with %(content_type)s not supported for %(request_uri)s"
            )

# End.
