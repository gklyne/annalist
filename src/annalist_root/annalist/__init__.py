"""
Annalist application
"""

__author__        = "Graham Klyne"
__author_email__  = "GK@ACM.ORG"
__copyright__     = "Copyright 2014, G. Klyne"
__license__       = "MIT (http://opensource.org/licenses/MIT)"

# https://docs.djangoproject.com/en/dev/ref/applications/
default_app_config = 'annalist.apps.AnnalistConfig'

# Version 0.1: initial public prototype
#__version__        = "0.1.1"   # Feature freeze
#__version__        = "0.1.2"   # Test with Django 1.7
                                # Initial installation kit
                                # Apply sorting to entity lists to make test cases more robust across systems
                                # Setup scripts to initialize installation and site data
                                # Fix problem with local logins
                                # Various minor page presentation changes
                                # Access root URI path ('/') redirects to site display
                                # Add some online help text for site, collection front pages, and login page
                                # Resolve virtualenv problem on Ubuntu 14.04
                                # util.removetree hack to allow test suite to run on Windows
                                # Initial documentation
                                # Demonstration screencast
#__version__        = "0.1.3"   # Bump version number
                                # Post-release documentation updates
                                # Update annalist_manager with updatesitedata command and 
                                #   to create auth providers directory
                                # Updated field view definition to include extra fields used for 
                                #   enumerated type displays, etc.
                                # Updated view editing form description.
                                # Update field and view description of fields to restrict 
                                #   presentation of field choices
                                # Fix problem of ignoring blank value in submitted form (issue #30)
                                # Use collection and list labels for headings on entity list page (issue #26)
                                # Clean up page and section headings in record editing view
                                # Change confusing 'Select' label of field id (Field_sel) dropdown in view description
                                # Initialize entity label and comment to blank (issue #24)
                                # Fixed problem with rename locally created Default_view (issue #22)
                                # Fix that changing type of entity was not deleting old record (issue #29)
# __version__        = "0.1.4"  # Bump version number
# __version__        = "0.1.5"  # Bump version number (odd = unstable)
                                # Implemented authorization framework
                                # More new commands in `annalist-manager`
                                # List view option to hide columns on smaller screens
                                # Extend test suite covereage
                                # When adding field to view: check property URI is unique
                                # Documentation updates and new screencasts
                                # When renaming type, rename insrances to new type
                                # Prevent deleting type with instances present
                                # If specified default list not found, revert to built-in default
                                # Fix bug in entity reference field links (was linking to self, not target record)
                                # Add optional enumeration to available field render types
                                # Use separate Django database for each configuration
                                # Improve log file handling; include timestamps
                                # Some small usability improvements
                                # Address some areas of technical debt
#__version__        = "0.1.6"   # Bump version number for release
#__version__        = "0.1.6a"  # Hotfix: server error copying view without URI field
#__version__        = "0.1.7"   # Bump version number (odd = unstable)
                                # Rework form generator; full support for repeating fields
                                # Enlarge test coverage
                                # Some presentation improvements
                                # Various smaller bug fixes
__version__        = "0.1.8"   # Bump version number for release

# End.
