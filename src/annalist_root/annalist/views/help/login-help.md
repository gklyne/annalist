# Login page

The intended means of user authentication is via a third party login service:

* Enter a local username (which is how Annalist will identify you, independently of any third party authentication account you may use), select an identity provider (IDP) (e.g. `Google`) and click **Login**.
* If you are not already logged in to the IDP you will be asked to login via their site.  Then the IDP will ask your permission to disclose basic identifying information (email, first name and last name) to Annalist.  This step is skipped if you have completed these actions previously.
* If this is an existing Annalist account, and the email from the IDP matches the Annalist account email, you will be logged in.  If the username given does not match an existing Annalist account, a new account is created with the appropriate details and you are logged in to it.

Authentication using a local user account (e.g. created by an admin user using the 'admin' link on the page footer) can be performed by selecting `Local` as the Login service, and entering a password when requested.

Being logged in does not necessarily mean you have permissions to access Annalist data;  it simply means that Annalist has an indication of who you are.  Permissions to access Annalist collection data are set up separately by the site administrator or data collection owner.

Initial administrator access and permissions can be established using the `annalist-manager` command line utility.
