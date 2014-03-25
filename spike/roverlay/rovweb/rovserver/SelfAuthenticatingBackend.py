from django.contrib.auth.models import User

class SelfAuthenticatingBackend(object):
    """
    Authenticate self-declared information provided by user.

    This is, of course, no authentication at all.  It is intended to create a User object
    for use in conjunction with an OAuth2-based authorization flow that is presumed
    to include a suitable level of authentication.  In particular, OpenID Connect.
    
    This class is derived from the example at: 
    https://docs.djangoproject.com/en/1.6/topics/auth/customizing/#authentication-backends
    """
    def authenticate(self, username=None, password=None):
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked.
                user = User(username=username, password='Not specified')
                user.is_staff = True
                user.is_superuser = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

