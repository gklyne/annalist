# Run using:
# 
#    OAUTHLIB_INSECURE_TRANSPORT=1 python oauth2text.py

from requests_oauthlib import OAuth2Session

# Credentials you get from registering a new application
client_id = "733431331031-l97e4tvs1aetaigu3037gajinp7umm73.apps.googleusercontent.com"
client_secret = raw_input('Paste the client secret here:')
redirect_uri = "http://localhost:8000/annalist/login_done/"
# OAuth endpoints given in the Google API documentation
authorization_base_url = "https://accounts.google.com/o/oauth2/v2/auth"
token_url = "https://www.googleapis.com/oauth2/v4/token"
scope = [
    "https://www.googleapis.com/auth/userinfo.email"
    # "https://www.googleapis.com/auth/userinfo.profile"
]
google = OAuth2Session(client_id, scope=scope, redirect_uri=redirect_uri)
# Redirect user to Google for authorization
authorization_url, state = google.authorization_url(authorization_base_url,
    # offline for refresh token
    # force to always make user click authorize
    # access_type="offline", 
    # prompt="select_account"
    )
print 'Please go here and authorize:\n', authorization_url
# Get the authorization verifier code from the callback url
redirect_response = raw_input('Paste the full redirect URL here:')

# Create new session object for "callback" request
google_resp = OAuth2Session(client_id, scope=scope, state=state, redirect_uri=redirect_uri)
# Fetch the access token
google_resp.fetch_token(token_url, client_secret=client_secret,
        authorization_response=redirect_response)
# Fetch a protected resource, i.e. user profile
r = google_resp.get('https://www.googleapis.com/oauth2/v1/userinfo')
print r.content
