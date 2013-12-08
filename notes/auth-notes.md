AUTH* Notes for Annalist

# Specifications and links

* OAUTH2
* JSON tokens
  - http://tools.ietf.org/html/draft-ietf-oauth-json-web-token-13
  - http://tools.ietf.org/html/draft-ietf-oauth-jwt-bearer-06
* UMA - see http://tools.ietf.org/html/draft-hardjono-oauth-umacore-07, etc.
  - http://en.wikipedia.org/wiki/User-Managed_Access
  - http://smartjisc.wordpress.com/2012/06/30/puma-building-a-requester-application/#more-603
  - http://smartjisc.wordpress.com/2012/04/20/puma-building-a-host-application/#more-600
  - http://kantarainitiative.org/confluence/display/uma/Home
  - https://bitbucket.org/smartproject
  - http://ox.gluu.org/doku.php?id=start
  - https://svn.gluu.info/repository/openxdi/
  - http://ox.gluu.org/doku.php?id=oxd:concept
  - https://svn.gluu.info/repository/oauth2ApacheHTTPD/


## UMA and related links

Auth* - see http://tools.ietf.org/html/draft-hardjono-oauth-umacore-07, etc.
- http://en.wikipedia.org/wiki/User-Managed_Access
- http://smartjisc.wordpress.com/2012/06/30/puma-building-a-requester-application/#more-603
- http://smartjisc.wordpress.com/2012/04/20/puma-building-a-host-application/#more-600
- http://kantarainitiative.org/confluence/display/uma/Home
- https://bitbucket.org/smartproject

- http://tools.ietf.org/html/draft-ietf-oauth-json-web-token-13
- http://tools.ietf.org/html/draft-ietf-oauth-jwt-bearer-06

- http://ox.gluu.org/doku.php?id=start
- https://svn.gluu.info/repository/openxdi/
- http://ox.gluu.org/doku.php?id=oxd:concept
- https://svn.gluu.info/repository/oauth2ApacheHTTPD/


# Authentication model

Goal: confirmed URI; could be OpenId or Persona?


# Authorization model sketch

In all cases, id is a confirmed id provided by the authentication service.

    authorization: collection -> (id, operation, source) -> [(role, obligation)]

?? how to select among multiple roles?  For now, assume just one coming back from authorization

    obligation:  IO( Maybe token )

     - 3 cases initially: deny, allow, agree t&c to allow

    permission: token -> collection -> (id, operation, source) -> IO(boolean)

Oauth.  The above flow appears to be very similar to what is provided by Oauth2, so it would probably make sense to try and use that.  Authentication will need to be handled separately.  Also look out for potential security problems, and make use HTTP is used for token exchanges (cf. http://hueniverse.com/2012/07/oauth-2-0-and-the-road-to-hell/, http://hueniverse.com/oauth/) 

=> collection as security realm

https://github.com/litl/rauth seems to be the favoured Python implementation of Oauth 2 (and 1?)

## OAUTH2 resources

"Ryan Boyd’s Getting Started with OAuth 2.0 (O’Reilly) for a readable, detailed explanation of OAuth 2.0."

## UMA notes

I've read through the UMA spec and find it's really quite hard to follow.  This may be in part because it's highly dependent on OAuth2, and assumes pretty good knowledge of that spec.

My requirement is to provide authentication and access control for a research data management platform, a requirement for which is an option to open read access to parts of the data to applications that have no awareness of the auth* protocols used.  Also, I want to be able to hand an access token to a 3rd party (non-browser) application ahead of actually accessing a protected resource.  Based on my reading of the UMA authorization flows, neither of these are possible using UMA.

My current line of investigation is to use Open-ID connect for authorization, and some other flow (possibly from the OAuth2 spec) for access control.  In this, I may use some of the UMA protocol elements (I'm thinking of the JSON structures) rather than invent new ones.  I'm anticipating generating something like bearer tokens that have restricted applicability in terms of who can use them, period of validity and resources for which they are valid.  I think the UMA elements cover this.
