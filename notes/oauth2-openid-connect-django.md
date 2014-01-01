# Oauth2, OpenID Connect and Django


## Background

This note records some investigations I've been conducting into authentication and authorization mechanisms for a research data management system I'm developing.  The system aims to allow access to underlying data using standard web requests (i.e. no database or special API used), so I'm looking for an authorization and authentication framework using standard web mechanisms.  In particular, I don't want to be locked into the minutiae of a particular web application framework when serving raw data.

I also don't want to maintain a local username/password database, for reasons well-articulated by @timbray (cf. [http://www.tbray.org/ongoing/When/201x/2013/07/30/On-Federation](), [http://www.tbray.org/ongoing/When/201x/2013/08/14/FC2-Single-Point-of-Failure](), etc.)


## OAuth2 authorization and authentication

OAuth2 is primarily (or initially) an *authorization* system.  But to do this reliably, it must authenticate the user who is doing the authorizing; i.e. it must embody some form of authentication.  Thus, it should be possible for the authorization granted to be just to know the identity (or an identityfing label) of the person doing the authorizing.  Which sounds rather like a form of authentication.

This is just what OpenID Connect (OIDC) ([http://openid.net/specs/openid-connect-core-1_0.html]()) does: it uses the OAuth2 protocol as the basis of an authentication service.  In particular, an OAuth2 scope value of `openid` requests an ID Token (in the form of a [JWT](http://tools.ietf.org/html/draft-ietf-oauth-json-web-token)) to be returned.  Among other possible values, the ID Token contains _issuer_ and _subject_ identifiers, which, taken together, constitute a unique opaque identifier for the authenticated user.  Additional information (name, email, etc.) may be made available (in response to a subsequent request when using the OIDC _authorization flow_, or directly when using the _implicit flow_).


## Django sessions and authentication

[Django](https://www.djangoproject.com/) is a Python web application framework, which supplies a range of WSGI "middleware" options to assist with authentication; key elements in this are [session management](https://docs.djangoproject.com/en/dev/topics/http/sessions/) and [authentication](https://docs.djangoproject.com/en/dev/topics/auth/default/).

Session management provides a way to save information between requests from the same source within some time interval.  This allows information to be saved so that a user is not required to authenticate every individual request.

Authentication is centred on the notion of a `User` that is associated with each incoming request; a `User` object presents known information about an authenticated user associated with each request.  The built-in authentication uses locally stored usernames and passwords when authenticating a user.  But a goal of my investigations is to avoid keeping passwords.  Django does allow alternative authentication "back ends" to be used, but (as far as I can tell) the authentication model requires all credential information to be available prior to invoking the authentication function.

There is some example code for using OAuth2 authorization with Django (cf. [`oauth2client` Django sample code](http://code.google.com/p/google-api-python-client/source/browse/#hg%2Fsamples%2Fdjango_sample), but this code appears to require the user to be authenticated prior to invoking the OAuth2 flow; i.e. it appears to be intended for authorization of access for an already-authenticated user, rather than for handling the authentication itself.


## Implementation

These notes describe my initial implementation attempts to use OpenID Connect (OIDC).

For this, I used an existing Django-based web application, `roverlay`.  I chose this for my experiments because (a) it already existed, (b) it is a fairly simple application, and (c) it provides both a browser-facing web page elements and application-facing REST APIs.  The function of the application is not important here, but further details are available at [https://github.com/wf4ever/ro-manager/blob/master/src/roverlay/README.md]().

Code for the implementation is [available in GitHub](https://github.com/gklyne/annalist/blob/develop/spike/roverlay/rovweb/rovserver/).  (Note that the client secrets file used is not in the code tree, but is found in "~/.roverlay/providers/".)  This is not production-quality code, just something I'm hacking together to build an understanding of how the various pieces interact, which will in turn inform future designs.


### Overall flow and views used

My implementation uses server-side views only, without relying on Javascript in the cient.  It is possible to use Javascript redirects to reduce the number of server redirects and HTTP round-trips needed, but for this exercise I have stuck with server-side logic only. (For an example of AJAX-supported OIDC, see [http://code.google.com/p/openid-connect-example/]().)

The overall sequence used is:

1. User browses to a protected page.
2. If not yet authenticated, server redirects to a login page, with URI of current request as a parameter.
3. The login page requests a user id and provider to use (allowing for future possibilities of using one of multiple providers;  it would be good to introduce a Poetica-style provider selection logic (cf. [https://www.tbray.org/ongoing/When/201x/2013/06/07/Why-findIDP]()), but that's an exercise for later).
4. Redirect to selected OIDC provider.
5. The OIDC provider does its dance, authenticating the user and soliciting authorization for disclosure of requested identifying information, as required.
6. The OIDC provider redirects back to web service client.
7. The web service client saves the credential/token information, then redirects to the originally requested page.
8. This time, the required authentication credentials should be present and correct, and the page is displayed.

To implement this within a Django web service client, the following views are defined:

1.  A Login page, with fields for entry of User ID and OIDC provider selection.
2.  A Login form submission view, which receives the login form data and redirects to the selected OIDC provider, having saved the URI of the original request and other key information.  This has been implemented as a separate view from the login, but could equally be the same view as the login page, distinguished by use of POST rather than GET.
3.  A Login completion page, which receives, checks and saves the OIDC authentication credentials (id token) and then redirects to the originally requested page.  Originally, I tried to redirect straight back to the originally requested page, but this raised two issues:  (a) OIDC requires the AP redirector is to a previously registered page (presumably to avoid some potential security problems), and (b) the logic to detect and handle OIDC return parameters for every page view is potentially complicated.  Having a separate page incurs an additional HTTP round trip for the additional redirect, but does make the underlying logic clearer.
4.  A logout view that purges any saved authentication credentials from the user session, then redirects to the service home page.

There is an additional step not covered here:  depending on the OIDC flow used (_authorization flow_ vs _implicit flow_), having received an ID token the client application may make an additional request to retreive additional information about the user (name, email, etc.).  The extent of such additional information is constrained by the `scope` parameter in the initial authentication/authorization request.


### OAuth2 and Django - take 1

My first implementation attempt was adapted from the example OAuth2 use with Django that is part of the [Google API python client library](http://code.google.com/p/google-api-python-client/).  This code uses the Django `@login_required` decorator to establish a `User` object for each incoming request.

For visibility of interactions, rather than use the `@login_required` decorator, I used the Django [authentication library functions](https://docs.djangoproject.com/en/dev/topics/auth/default/) directly; specifically `authenticate` and `login` from package `django.contrib.auth`.

I tried just creating a User value and then using `login` to associate it with a session, but that caused an error, and in any case violates the documented use of `login`, which insists on the supplied User being authenticated.  Django's pluggable authentication system does not, as far as I can see, support OAuth2-style redirection flows.  So I created a [dummy `SelfAuthenticatingBackend` module](https://github.com/gklyne/annalist/blob/develop/spike/roverlay/rovweb/rovserver/SelfAuthenticatingBackend.py) to provide a fake Authentication for Django, and consequently rely on including my own tests for actually checking that web requests are duly authenticated by the OIDC mechanisms.

This approach works, and it has the advantage that the various elements of the OAuth2 flow used is quite visible, but it seems sub-optimal to invoke then subvert the existing Django mechanisms.


### OAuth2 and Django - take 2

@@TODO - second attempt

> Rather than storing the `oauth2client` `flow` object in the Django database keyed by user, try storing it in the session object.  This will mean that the flow can be initiated before there is an authenticated Django user.  The User object can then be created and registered as authenticated at the completion of the OAuth2 flow.


## oauth2client and OIDC id_token

Examination of the source code shows that the aut2client extracts and decodes the id_token returned in the `flow.step2_exchange` process ([here](https://code.google.com/p/google-api-python-client/source/browse/oauth2client/client.py#1293) and [here](_extract_id_token)), but does not validate it as specified in the OpenID Connect protocol, [section 3.1.3.7](http://openid.net/specs/openid-connect-core-1_0.html#IDTokenValidation).  Note that this allows that when the token has been received by TLS communucation directly with the authorization server, the JWT signature checking is not required.

Also unclear in the oauth2client documentaion is how a calling program is expected to obtain the id_token returned.  The value is returned as `credential.id_token`, where `credential` is the returned credential value from `flow.step2_exchange`.

### Google user profile access

To access user profile details (other than email address) from Google, an additional request is made using the access token provided via the initial OUath2 exchange.  A get request to [https://www.googleapis.com/plus/v1/people/me/openIdConnect](), using authorization credentials from the access token, returns a JSON result with user profiloe details.

For this to work, the client application registered with Google (via [https://cloud.google.com/console]()) must be permitted to use the [Google+ API](https://developers.google.com/+/api/), as shown:

![figures/Google-APIs-screenshot.png](Screenshot showing Google+ API enabled for project)


## Reflections and notes

The Google OIDC diagnostics were generally very helpful, in many cases providing immediate feedback on problems with the OAuth2 requests.  An exception to this was a report copncerning lack of an application name.  It wasn't immediately clear to me that this was a problem with the application registratyion as opposed to the OAuth2 request.  Otherwise, I found the diganostics provided were useful and to the point.

An important part of the development of an OIDC client is registraton of the client with the OIDC providers that may be used.  This is needed (a) to establish a client secret between client and provider that is an important part of the overall security model, (b) to provide informaton that the OIDC provider can display when soliciting authorization for client access, (c) to register a set of allowable endpoints to be used as the target of redirection after authorization has been confirmed, and (d) probably to address some other security- or usability-related concerns.

OAuth2 redirection endpoints have to be pre-registered with the authorization/authentication provider (AP) - this means that the flow cannot be invoked to return directly to an arbitrary requested resource at the client.  Instead, I use a "login complete" URI that performs the final redirect to the originally requested resource.

The first time I ran a successful OAuth2 flow, I found the redirect from the AP back to my client caused the browser "NoScript" plugin to throw an ABE violation (Application Boundary Enforcement).  This was using a client running as `http://localhost...`.  I'm not sure if this is a special case or a more general potential problem.  I only got the process to complete by disabling NoScript's ABE feature, which suggests a problem with either OAuth2 (a potential security hole?) or with NoScript.  See also [http://noscript.net/abe/web-authors.html](), which suggests web sites should publish exceptions.

