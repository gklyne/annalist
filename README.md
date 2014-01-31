annalist
========

Free-form web data platform - "Data management for little guys"


Goals
-----

Think of a kind of "Linked data journal" or "Linked data wiki".  (The name "annalist" derives from ["a person who writes annals"](http://www.oxforddictionaries.com/definition/english/annalist).)

* Easy data: out-of-box data acquisition and modification
* Flexible data: new record types and fields can be added as-required.
* Sharable data: use textual, easy to read file formats that can be shared by web, email, file transfer, version management system, memory stick, etc.
* Remixable data: records that can be first class participants in a wider ecosystem of linked data, with links in and links out.

In Annalist, I hope to create a generic data journal which can be used for diverse purposes, in which I have been motivated by the needs of small academic research groups, and my own past experiences running a small business.  I want to deliver a self-hostable, web-based tool that will, "out-of-box", allow collection of web accessible, linked data without prior design of its structure.  Rather, I want to allow structure in data to be developed as needs arise.  Some of my ideas for this are drawn from pre-web PC tools (e.g. [WordPerfect Notebook](https://raw.github.com/gklyne/annalist/master/presentations/wpnotebook_screenshots.png) and [Blackwell Idealist](https://raw.github.com/gklyne/annalist/master/presentations/matrix.png)) which used simple text based file formats to drive flexible, small-scale databases.  I find these products occupied a sweet spot that hasn't since been matched by any web-based software of which I'm aware.

The work on Annalist is in its very early stages, but I'm committed to open development from the outset, so you can see all the technical work and notes to date [here](https://github.com/gklyne/annalist).  There's nothing usable yet (as of January 2014).  Note that all the active development takes place on the ["develop" branch](https://github.com/gklyne/annalist/tree/develop).  In due course, I plan to follow a ["gitflow"-inspired](http://nvie.com/posts/a-successful-git-branching-model/) working style that uses the "master" branch for released, tested software.


Installation
------------

These instructions are my attempt to capture the steps to get a development copy of Annalist running.  The project and instructions are currently work-in-progress, so they may break.

    # Clone git repository
    cd _workspase_base_
    git clone https://github.com/gklyne/annalist.git
    cd annalist
    git checkout develop

    # Create Pythoin virtualenv for testing Annalist
    virtualenv -p python2.7 anenv
    . anenv/bin/activate
    pip install -r src/annalist_site/requirements/devel.txt 
    cd src/annalist_site/

    # Run tests
    python manage.py test

    # Create development site data and run up server
    # To use Google as OAuth2/OpenID Connect provider, register the application as 
    # described in the next section, then:
    # - Copy project file `src/annalist_site/oauth2/google_oauth2_client_secrets.json.example`
    #   to `~/.annalist/providers/google_oauth2_client_secrets.json`
    # - edit `~/.annalist/providers/google_oauth2_client_secrets.json` to include the
    #   application identifier and client secret allocated when the application was
    #   registered

    # Initialize the web application data
    python manage.py dbsync
    mkdir devel
    cp -rfv test/init/annalist_site/ devel

    # Start the web application
    python manage.py runserver

Now point a local browser at [http://localhost:8000/annalist](http://localhost:8000/annalist).  Clicking on the login link should display a login screen with "Google" offered as a login service.  Enter a user ID and click "Login" to invoke an OAuth2 authentication sequence with Google.

(Note: if using the "NoScript" browser plugin, this will trigger an XSS warning, and separately an ABE warning.  Hopefully, NoScript will fix this.  Meanwhile I added accounts.google.com as an exception from XSS sanitization, and disabled ABE checking, in NoScript.)


Google profile access
---------------------

Annalist uses OAuth2/OpenID Connect authentication to control access to data resources.  This is currently tested with Google's OAuth2 services.  For this to work, the client application must be registered with Google (via [https://cloud.google.com/console]()) and must be permitted to use the [Google+ API](https://developers.google.com/+/api/), as shown:

![Screenshot showing Google+ API enabled for project](https://raw.github.com/gklyne/annalist/develop/notes/figures/Google-APIs-screenshot.png)

* Create new project
* Under `APIs & Auth > APIs`, enable Google+ and disable all others
* Under `APIs & Auth > Credentials`, Create new Client Id:
  * Select "Web application"
  * Authorized redirect URI is `http://localhost:8000/annalist/login_done/` (don't omit the trailing "/")
  * No authorized Javascript origins (yet)
  * Then click button "Create client ID"
* Under `APIs & Auth > Consent screen`, fill in a name for the appliucation
* The window now displays client id and client secret values.  The button "Download JSON" can be used to download a file that can be used to populate the file `~/.annalist/providers/google_oauth2_client_secrets.json`, but note that Annalist also uses additional field(s) not populated by the Google console.

To access user profile details (other than email address) from Google, an additional request is made using the access token provided via the initial OUath2 exchange.  A get request to [https://www.googleapis.com/plus/v1/people/me/openIdConnect](), using authorization credentials from the access token, returns a JSON result with user profile details.


Technical elements
------------------

Note: active development is taking place on the "develop" branch in git - see [https://github.com/gklyne/annalist/tree/develop](https://github.com/gklyne/annalist/tree/develop))

* Standard web server
* Access control with 3rd party IDP authentication
* File based data storage model
    * File format RDF-based. Have settled on JSON-LD for initial work.
    * Records/Entities, Attachments (blobs), Collections, Groups
    * Directory based organization
    * Separate indexing as and when required.
* User interface
    * Self-maintained configuration data
    * Grid-based flexible layout engine (e.g. Bootstrap)
* Bridges for other data sources
    * Spreadsheet
    * JSON?
    * XML?
    * _others_


TODO
----

See: [https://github.com/gklyne/annalist/blob/develop/TODO.txt]()
