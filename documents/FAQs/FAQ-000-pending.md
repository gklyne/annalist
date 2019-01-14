# Pending FAQs and draft responses

----

Q: Attemting to login with Google fails with "missing_token"

The full message seen is:

    Login failed
    (missing_token) Missing access token parameter.

The OpenId Connect (OIDC) authentication code is very sensitive to configuration errors.  Check the following:

1. URIs for various OIDC endpoints in the providerdata exactly match those in the identity provider's documentation (or better still, a working example).  Trailing "/" characters on URIs can cause failure. 

2. Dueto a bug in the code at the time ofm writing (2019-01), the redirect URI used is inconsistent.  Ensure only one redirect URI is declared in the provioder data (there's a code bug here)

3. For Google: ensure the "web property" has been added in the Google search console:

    - https://www.google.com/webmasters/tools/home
    - Add property
    - Follow instructions, which involve downloading a verification file and installing it on the web server.


See also:

- https://stackoverflow.com/questions/10827920/not-receiving-google-oauth-refresh-token
- https://stackoverflow.com/questions/51499034/google-oauthlib-scope-has-changed
