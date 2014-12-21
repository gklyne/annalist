To Google group:

I've just released an update (0.1.6) to the first public prototype of Annalist.

The major visible change in this release is the implementation of an Authorization (access control) framework (separate from the authentication mechanisms).  Authorization is applied mainly at the level of an Annalist collection, with provision for site-wide defaults to be defined through the `annalist-manager` utility.  Separate permissions are used for accessing data, creating data, modifying data, changing collection structure and changing user permissions.  More details can be found in the [Guide to using Annalist](https://github.com/gklyne/annalist/blob/master/documents/using-annalist.md), in the section headed "Access control and user permissions".

There are many other small improvements in this release, including:
- New field rendering types (token set and optional enumerated value)
- Fix some bug/usability problems associated with renaming or deleting record types
- Configuration and logging enhancements
- Usability improvements
- Additional `annalist-manager` capabilities
- Documentation updates and new screencast videos
- Extended test coverage
- Numerous small bug fixes and code improvements
- Requires Django 1.7 (or maybe later)

More details can be found in the "History" section of the [release notes](https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md), and via the GitHub issues list.

#g

...

To research-object:

I've just released Annalist 0.1.6.

The announcement is at:
https://groups.google.com/forum/#!topic/annalist-discuss/o3OUWQNH2kI

Release notes (see "history" section for details) at:
https://github.com/gklyne/annalist/blob/master/documents/release-notes/release-v0.1.md

Annalist project on Github:
https://github.com/gklyne/annalist


This is still a prototype release, with some important functions not completed, and usability improvements needed in some areas.  The main addition in this release is an authorization (access control) framework, linked to OAuth2-0based authenticated identifies.

That said, I am finding the present version is both capable and robust enough for me to start using it in some of my own personal data management activities.

#g
--

