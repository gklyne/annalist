# Configuring Annalist to use OpenID Connect

Annalist is designed to use third party authentication services based on [OpenID Connect ](http://openid.net/connect/), which is a simple identity layer built over the [OAuth2 proptocol](http://oauth.net/2/).

Currently, Annalist has been tested with identity services provided by Google, but should work with other identity providers.  Tje instructions below arte for settimng up with Google.  Some of the steps for other providers will almost certainly be different, but should follow a similar pattern.

In outline, the steps are:

1. Install Annalist.  This is covered in [Installing and setting up Annalist](installing-annalist.md).

2. Register the installed Annalist service with the identity provider (Google).

3. Create a local "client secrets" file containing application authentication protocol details provided by the registration process

4. Log in using third party credentials.

The instructions below assume that Annalist is installed for local access from the computer on which itis installed.  If installed for shared access, the `localhost` domain name in the following steps must be replaced by the full domain name of the host on which it is installed.

Note that being logged in does not necessarily mean you have permissions to access Annalist data;  it simply means that Annalist has an indication of who you are.

(@@NOTE: Currently, the authorization system is not fully implememted, and all authenticated users have full access to the Annalist data, but that will change before the first non-prototype software release.  See [Annalist issue 11](https://github.com/gklyne/annalist/issues/11))


## Register Annalist service with Google

In order to use Google OAuth2/OpenID Connect authentication the installed Annalist service must be registered with Google (via [https://cloud.google.com/console](https://cloud.google.com/console)) and must be permitted to use the [Google+ API](https://developers.google.com/+/api/), as shown:

![Screenshot showing Google+ API enabled for project](screenshots/Google-APIs-screenshot.png)

* Create new project
* Under `APIs & Auth > APIs`, enable Google+ and disable all others
* Under `APIs & Auth > Credentials`, Create new Client Id:
  * Select "Web application"
  * Authorized redirect URI is `http://localhost:8000/annalist/login_done/` (don't omit the trailing "/").
  * Add an additional authorized redirect URIs using an actual host name if the application is to be accessible from other hosts; e.g. `http://example.org:8000/annalist/login_done/`.  Additional redirect URIs need to be included also in the local configuration file (see below).
  * No authorized Javascript origins (yet)
  * Then click button "Create client ID"
* Under `APIs & Auth > Consent screen`, fill in a name for the application
* The window now displays client id and client secret values.  The button "Download JSON" can be used to download a file that can be used to populate the file `~/.annalist/providers/google_oauth2_client_secrets.json`, but note that Annalist also uses an additional field not populated by Google.

The JSON file provided by Google looks something like this:

    {
      "web": {
        "client_id": "9876543210.apps.googleusercontent.com",
        "client_secret": "secret-12345678901234567890",
        "client_email": "9876543210@developer.gserviceaccount.com",
        "client_x509_cert_url": 
            "https://www.googleapis.com/robot/v1/metadata/x509/9876543210@developer.gserviceaccount.com",
        "redirect_uris": 
          [ "http://localhost:8000/annalist/login_done/", 
            "http://annalist-demo.example.org:8000/annalist/login_done/"
          ],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
      }
    }


## Create a local client secrets file

Annalist keeps authentication data in a location separate from the installed software.  The default location is a directory called  `.annalist` in the home directory of the user running the Annalist service.

A subdirectory called `providers` contains a client secrets file for each supported identity provider.  Annalist reads the contehnt of this directory to build a list of identity providers that are offered on the initial login screen.

To configure Annalist to use the Google authentication service based on the service registration above:

1.  Edit the client secrets file returned by Google to add a provider name; e.g.

        {
          "web": {
            "provider": "Google",
            "client_id": "9876543210.apps.googleusercontent.com",
            "client_secret": "secret-12345678901234567890",
            "client_email": "9876543210@developer.gserviceaccount.com",
            "client_x509_cert_url": 
                "https://www.googleapis.com/robot/v1/metadata/x509/9876543210@developer.gserviceaccount.com",
            "redirect_uris": 
              [ "http://localhost:8000/annalist/login_done/", 
                "http://annalist-demo.example.org:8000/annalist/login_done/"
              ],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
          }
        }

    This provider name is used to populate the dropdown box on Annalist's login page, so it should be a short string that will be recogizable to a user.

2.  Copy the modified client secrets file to `~/.annalist/providers/google_oauth2_client_secrets.json`.  (The exact filename is not critical, just its location and content)

3.  Restart the Annalist server if it is already running.  (The client secrets are loaded and cached the first time a user logs in)


## Log in with Google credentials

Now point a local browser at [http://localhost:8000/annalist](http://localhost:8000/annalist).  Clicking on the login link should display a login screen with "Google" offered as a login service.  Enter a user ID and click "Login" to invoke an OAuth2 authentication sequence with Google.

(Note: if using the "NoScript" browser plugin, this will trigger an XSS warning, and separately an ABE warning.  Hopefully, NoScript will fix this.  Meanwhile I added accounts.google.com as an exception from XSS sanitization, and disabled ABE checking, in NoScript.)


