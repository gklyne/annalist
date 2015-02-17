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
#__version__        = "0.1.8"   # Bump version number for release
#__version__        = "0.1.8a"  # Hotfix: https://github.com/gklyne/annalist/issues/39 (bad username causes server error)
#__version__        = "0.1.9"   # Bump version number (odd = unstable)
                                # Add field alias option
                                # Option ("+") to create new linked record from referring record view
                                # Rework handling of repeated use of same field
                                # When changing list view, don't filter by entity type
                                # Various bug fixes
                                # Form display and response code refactoring
                                # Use placholder as descriptive label foprn repeat group form display
                                # Refactor field rendering logic
                                # Implement special renderer for field placement (position/size)
                                # Document default admin user permissions created with new site
                                # annalist-manager enhancements; permissions help, new subcommands
                                # Added build scripts for Docker containers
#__version__        = "0.1.10"  # Bump version number for release
#__version__        = "0.1.11"  # Bump version number (odd = unstable)
                                # Save logs in root of annalist_site data, for Docker visibility
                                # Introduce non-edit view of entities, with navigation links
                                # New render type: Boolean as checkbox
                                # New render type: URI as Hyperlink
                                # New render type: URI as embedded image
                                # New render type: long text with Markdown formatting; and new CSS
                                # Page layout/styling changes; rationalize some CSS usage
                                # Change 'Add field' button to 'Edit view'
                                # Add 'View description' button on non-editing entity views
                                # View display: suppress headings for empty repeatgrouprow value
                                # Preserve current value in form if not present in drop-down options
                                # Various bug fixes (see release notes)
__version__        = "0.1.12"  # Bump version number for release


# End.
