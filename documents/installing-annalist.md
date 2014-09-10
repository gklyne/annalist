# Prerequisites

* Python 2.7
* virtualenv (includes setuptools and pip)

# Installing software

The following assumes that software is installed under a directory called $WORKSPACE; i.e. Annalist software is installed to $WORKSPACE/annalist.  This could be a user home directory.

1. Go to the workspace directory, create a Python virtual environment and activate it (i.e. make it the current Python environment).  This avids having the Annalist installation stomp over any otrher python installation, and makes it very easy to discard if or when it is not required.

        cd $WORKSPACE
        virtualenv annenv
        source annenv/bin/activate

    In an environment where the are multiple versions of Python installed, a `virtualenv` command like this might be needed to ensure that the appropriate version of Python is used:

        virtualenv -p python2.7 annenv

2. Obtain a copy of the Annalist distribution kit, e.g. from @@TODO, and copy to a conventient location (e.g., $WORKSPACE/Annalist-0.1.2.tar.gz).  Then install it thus:

        pip install $WORKSPACE/Annalist-0.1.2.tar.gz

3. ALternatively, install the software from PyPI (@@TODO: will be uploaded to PyPI when the initial release is stabilized):

        pip install annalist

# Setting up an Annalist site

Before setting up an Annalist configuration, theer are two issues to be aware of.  Or if you just want a quick installation for evaluation purposes, skip ahead to "Initial site setup",

## Annalist site options

Annalist deploymemnt details are controlled by files in the `src/annalist_rot/annalist_site/settings` directory.  Annalist comes with three pre-defined configurations: deveopment, personal, and shared.  The main differences between these are the location of the Annalist site data files, and the location of certain private configuration files.  (Other configuration options are possible by defining a new settings file.)

**Development**: Annalist site data is kept in a directory within the Annalist software source tree, and configuration files are in subdirectory `.annalist` of the installing user's home directory.

**Personal**: Annalist site data is in a sibdirectory `annalist_site`, and configuration files are in subdirectory `.annalist`, of the installing user's home directory.

**Shared**: Annalist site data is kept in directory `/var/annalist_site`, and configuration files are in subdirectory `/etc/annalist`.  Such an installation will typically require root privileges on the host computer system to complete.

## Analist authentication options

Annalist has been implemented to use federated authentication based on Open ID Connect (http://openid.net/connect/) rather than local user credential management.  Using third party authentication services should facilitate integration with single-sign-on (SSO) services, and avoids the security risks assciated with local password storage.  Unfortunately, installing and configuring a system to use an OpenID Connect authentication service does take some addtional effort to register the installed application with the authentication service.

Annalist currently supports two user authentication mechanisms: OpenID Connect using Google+, and local user login credentials.  (Other OpenID Connect providers may also work, but have not been tested.)


### OpenID Connect using Google+

Annalist OpenID Connect authentication has been tested with Google+ identity service.  Instructions for configuring a new installation to work with Google+ are in the [Annalist README](https://github.com/gklyne/annalist/blob/master/README.md). (@@TODO: _move to separate document and update link_)

The configuration details for using an OpenID Connect provider are stored in a private area, away from the Annalist source files and site data, since they contain private keying data.  A subdirectory `providers` of the Annalist configuration directory contains a description file for weach supported OpenID Connect provider.  New providers may be supported by adding descrtiption files to this directory.  The provider description for Google may be a useful example for creating descriptions for other providers.  (But be aware that different providers will have different registration procedures, and may require subtlely different forms of configuration information.)


### Local user database

Annalist can also allow users to log in using locally stored credentials, which may be useful for quick evaluation deployments but is not the recommended mechanism for normal operational use.

When installing Annalist, an administration account may be created using the `annalist-manager` tool.  When logged in to Annalist using this account, the `admin` link in the footer of most Annalist pages will allow new user accounts to be created via the Django admin interface.  More documentation about using this admin intrefcae is in the [The Django Admin Site](http://www.djangobook.com/en/2.0/chapter06.html), which isChapter 6 of [The Django Book](http://www.djangobook.com/en/2.0/index.html).


## Initial site setup

These instructions use the example of a development configuration (`devel`) and a local user database: these options are not suitable for a full deployment, but are probably the least intrusive to use for early evaluation purposes.

@@TODO more here



# Accessing Annalist

# Create a collection

