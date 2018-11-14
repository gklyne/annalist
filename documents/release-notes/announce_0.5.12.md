## To Google group:

### Announcing Annalist release 0.5.12

I've just released an update (release 0.5.12) of Annalist.

This is a maintenance release, with no significant changes in functionality.  Package dependencies have been updated to latest versions (Except Django is updated to 1.11, the last release to support Python 2).

All code has been updated to run under Python 3.7, but package dependencies Django 1.11 and rdflib-jsonld 0.4.0 are not ready (though easily patched).

The OpenID Connect login code has been updated to use a newer support library, a consequence of which is that HTTPS must be used to access Annalist, which would be achieved by running Annalist behind a robust HTTP server such as Apache HTTPD or Nginx.  (The Annalist installation document has initial instructions for installation with Apache, including installation of a "LetsEncrypt" certificate.)

The test suite has been updated to cover `annalist-manager` functionality.

More details can be found in the "History" section of the 
[latest release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.5.md), 
[previous release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md) and via the 
[GitHub issues list](https://github.com/gklyne/annalist/issues).

The Annalist demo site is at [annalist.net](http://annalist.net/), with links to several other introductory pages.

The Annalist live demo system is at [demo.annalist.net](http://demo.annalist.net/annalist/site/), and [instructions for installing Annalist](https://github.com/gklyne/annalist/blob/master/documents/installing-annalist.md) are available from, the [Annalist GitHub project](https://github.com/gklyne/annalist).  The [Annalist tutorial](http://annalist.net/documents/tutorial/annalist-tutorial.html) is also available from the demo system site.

#g

...

## To research-object, RDS-CREAM and FAST:

== Announcing Annalist release 0.5.12 ==

I've just released an update (release 0.5.12) of Annalist.

This is a maintenance release, with no substantial changes in functionality.  Package dependencies have been updated to latest versions (Except Django is updated to 1.11, the last release to support Python 2), and code has been migrated to run under Python 3.7 (but package dependencies Django 1.11 and rdflib-jsonld 0.4.0 are not ready).

The full announcement is at:
https://groups.google.com/d/msg/annalist-discuss/WOAR47fcCrs/wtGi5W5NAAAJ
https://groups.google.com/d/msg/annalist-discuss/@@@@@@

See also: 

Annalist demo site: http://annalist.net/

Release notes (see "history" section for details) at:
https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.5.md

#g

