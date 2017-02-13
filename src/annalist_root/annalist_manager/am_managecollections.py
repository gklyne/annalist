"""
Collection management and migration helpers

See also: documents/notes/schema-evolution-notes:
"""

from __future__ import print_function

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2016, G. Klyne"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

import os
import sys
import logging
import subprocess
import importlib
import shutil
import datetime

log = logging.getLogger(__name__)

from annalist                       import layout
from annalist.identifiers           import ANNAL, RDFS
from annalist.util                  import valid_id, extract_entity_id, make_type_entity_id
from annalist.collections           import installable_collections

from annalist.models.site           import Site
from annalist.models.collection     import Collection
from annalist.models.recordtype     import RecordType
from annalist.models.recordview     import RecordView
from annalist.models.recordlist     import RecordList
from annalist.models.recordfield    import RecordField
from annalist.models.recordgroup    import RecordGroup
from annalist.models.collectiondata import initialize_coll_data, copy_coll_data, migrate_coll_data

import am_errors
from am_settings                    import am_get_settings, am_get_site_settings, am_get_site
from am_getargvalue                 import getarg, getargvalue

# Collection access helpers

def get_settings_site(annroot, userhome, options):
    """
    Get settings and site data based on command line options provided

    returns:

        (status, settings, site)

    where 'settings' and/or 'site' are None if not found.
    """
    status   = am_errors.AM_SUCCESS
    settings = am_get_settings(annroot, userhome, options)
    site     = None
    if not settings:
        print("Settings not found (%s)"%(options.configuration), file=sys.stderr)
        status = am_errors.AM_NOSETTINGS
    if status == am_errors.AM_SUCCESS:
        sitesettings = am_get_site_settings(annroot, userhome, options)
        if not sitesettings:
            print("Site settings not found (%s)"%(options.configuration), file=sys.stderr)
            status = am_errors.AM_NOSETTINGS
    if status == am_errors.AM_SUCCESS:
        site        = am_get_site(sitesettings)
    return (status, settings, site)

def coll_type(coll, type_id):
    """
    Return identified type in collection, or None
    """
    return RecordField.load(coll, field_id, altscope="all")

def coll_types(coll):
    """
    Return iterator over types in collection
    """
    return coll.types()

def coll_view(coll, view_id):
    """
    Return identified view in collection, or None
    """
    return RecordView.load(coll, view_id, altscope="all")

def coll_views(coll):
    """
    Return iterator over views in collection
    """
    for fid in coll._children(RecordView, altscope="all"):
        f = coll_view(coll, fid)
        if f and f.get_id() != "_initial_values":
            yield f
    return

def coll_list(coll, list_id):
    """
    Return identified list in collection, or None
    """
    return RecordList.load(coll, list_id, altscope="all")

def coll_lists(coll):
    """
    Return iterator over lists in collection
    """
    for fid in coll._children(RecordList, altscope="all"):
        f = coll_list(coll, fid)
        if f and f.get_id() != "_initial_values":
            yield f
    return

def coll_field(coll, field_id):
    """
    Return identified field in collection, or None
    """
    return RecordField.load(coll, field_id, altscope="all")

def coll_fields(coll):
    """
    Return iterator over fields in collection
    """
    for fid in coll._children(RecordField, altscope="all"):
        f = coll_field(coll, fid)
        if f and f.get_id() != "_initial_values":
            yield f
    return

def coll_group(coll, group_id):
    """
    Return identified group in collection, or None
    """
    return RecordGroup.load(coll, group_id, altscope="all")

def coll_groups(coll):
    """
    Return iterator over groups in collection
    """
    for gid in coll._children(RecordGroup, altscope="all"):
        g = coll_group(coll, gid)
        if g and g.get_id() != "_initial_values":
            yield g
    return

# Common logic for View, List and Group field lists

def add_to_set(value, values):
    """
    Add non-empty value to set of values
    """
    if value:
        values.add(value)
    return values

def field_in_field_list(field_list, field_id, property_uri):
    """
    Tests to see if field is referenced in field list
    """
    for fref in field_list:
        if ( (extract_entity_id(fref.get(ANNAL.CURIE.field_id, "")) == field_id) or
             (fref.get(ANNAL.CURIE.property_uri, "") == property_uri) ):
            return True
    return False

def group_in_field_list(field_list, coll, group_ids):
    """
    Tests to see if any of group ids are referenced in field list
    """
    for fref in field_list:
        fid  = extract_entity_id(fref.get(ANNAL.CURIE.field_id, ""))
        fdef = coll_field(coll, fid)
        if fdef.get(ANNAL.CURIE.group_ref, "") in group_ids:
            return True
    return False

def types_using_field(coll, field_id, property_uri):
    """
    Returns a list of type ids that may use a specified field or property URI
    """
    type_ids  = set()
    type_uris = set()
    group_ids = set()
    # Look at field definition
    f = coll_field(coll, field_id)
    add_to_set(f.get(ANNAL.CURIE.field_entity_type, ""), type_uris)
    # Look at groups that reference field
    for g in coll_groups(coll):
        if field_in_field_list(g[ANNAL.CURIE.group_fields], field_id, property_uri):
            add_to_set(g.get_id(), group_ids)
            add_to_set(extract_entity_id(g.get(ANNAL.CURIE.record_type, "")), type_uris)
    # Look at views that reference field or groups
    for v in coll_views(coll):
        if ( field_in_field_list(v[ANNAL.CURIE.view_fields], field_id, property_uri) or
             group_in_field_list(v[ANNAL.CURIE.view_fields], coll, group_ids) ):
            add_to_set(extract_entity_id(v.get(ANNAL.CURIE.record_type, "")), type_uris)
    # Look at lists that reference field or groups
    for l in coll_lists(coll):
        if ( field_in_field_list(l[ANNAL.CURIE.list_fields], field_id, property_uri) or
             group_in_field_list(l[ANNAL.CURIE.list_fields], coll, group_ids) ):
            add_to_set(extract_entity_id(l.get(ANNAL.CURIE.record_type, "")), type_uris)
            add_to_set(extract_entity_id(l.get(ANNAL.CURIE.default_type, "")), type_uris)
    # Collect type ids
    for t in coll_types(coll):
        type_uri       = t.get(ANNAL.CURIE.uri, "")
        supertype_uris = set( s[ANNAL.CURIE.supertype_uri] for s in t.get(ANNAL.CURIE.supertype_uris,[]) )
        if (type_uri in type_uris) or (supertype_uris & type_uris):
            add_to_set(t.get_id(), type_ids)
    return type_ids

def compare_field_list(old_coll, new_coll, old_field_list, new_field_list, reporting_prefix):
    """
    Report URI changes between fields lists as seen in group, view and list definitions
    """
    old_len = len(old_field_list)
    new_len = len(new_field_list)
    if new_len != old_len:
        print("* %s, field count changed from %d to %d"%(reporting_prefix, old_len, new_len))
    for i in range(new_len):
        for j in range(old_len):
            # Look for field in old group.
            # If not found, ignore it - we're looking for URI changes
            # @@TODO: ... or are we?
            new_f = new_field_list[i]
            old_f = old_field_list[j]
            field_id = extract_entity_id(new_f[ANNAL.CURIE.field_id])
            if field_id == extract_entity_id(old_f[ANNAL.CURIE.field_id]):
                # Field found - check for incompatible URI override
                # Note that field definitions are already checked
                old_uri = old_f.get(ANNAL.CURIE.property_uri, "")
                new_uri = new_f.get(ANNAL.CURIE.property_uri, "")
                if (not old_uri) and new_uri:
                    old_field = coll_field(old_coll, field_id)
                    old_uri   = old_field[ANNAL.CURIE.property_uri]
                if old_uri and (not new_uri):
                    new_field = coll_field(new_coll, field_id)
                    new_uri   = new_field[ANNAL.CURIE.property_uri]
                if old_uri != new_uri:
                    print(
                        "* %s, field %s, property URI changed from '%s' to '%s'"%
                        (reporting_prefix, field_id, old_uri, new_uri)
                        )
                    print(
                        "    Consider adding supertype '%s' to type '%s' in collection '%s'"%
                        (old_uri, type_id, new_coll_id)
                        )
                    report_property_references(new_coll, old_uri, "URI '%s'"%(old_uri))
                break
    return

def report_property_references(coll, property_uri, reporting_prefix):
    """
    Report all references to a specified property URI.
    """
    # Reference from types
    for t in coll_types(coll):
        type_id = t.get_id()
        alias_value_uris = [ a[ANNAL.CURIE.alias_source] for a in t.get(ANNAL.CURIE.field_aliases,[]) ]
        if property_uri in alias_value_uris:
            print("%s appears as an alias value of type '%s'"%(reporting_prefix, type_id))
    # References from views
    for v in coll_views(coll):
        view_id = v.get_id()
        report_property_references_in_field_list(
            coll, property_uri, v[ANNAL.CURIE.view_fields], 
            reporting_prefix, "fields for view %s"%(view_id)
            )
    # References from lists
    for l in coll_lists(coll):
        list_id = l.get_id()
        if property_uri in l.get(ANNAL.CURIE.list_entity_selector, ""):
            print("%s appears in selector for list '%s'"%(reporting_prefix, list_id))
        report_property_references_in_field_list(
            coll, property_uri, v[ANNAL.CURIE.list_fields], 
            reporting_prefix, "fields for list %s"%(list_id)
            )
    # References from fields
    for f in coll_fields(coll):
        field_id = f.get_id()
        if property_uri == f.get(ANNAL.CURIE.property_uri, ""):
            print("%s appears as property URI for field '%s'"%(reporting_prefix, field_id))
        if property_uri in f.get(ANNAL.CURIE.field_ref_restriction, ""):
            print("%s appears in value restriction for field '%s'"%(reporting_prefix, field_id))
    # References from groups
    for g in coll_groups(coll):
        group_id  = g.get_id()
        report_property_references_in_field_list(
            coll, property_uri, g[ANNAL.CURIE.group_fields], 
            reporting_prefix, "fields for group %s"%(group_id)
            )
    return

def report_property_references_in_field_list(
        coll, property_uri, field_list, 
        reporting_prefix, reporting_suffix):
    """
    Report occurrences of a property URI appearing in a field list.
    """
    for f in field_list:
        if property_uri == f.get(ANNAL.CURIE.property_uri, ""):
            print("%s appears in %s"%(reporting_prefix, reporting_suffix))
    return

def report_type_references(coll, type_uri, reporting_prefix):
    """
    Report all references to a specified type URI.
    """
    # Reference from types
    for t in coll_types(coll):
        type_id = t.get_id()
        supertype_uris = [ u[ANNAL.CURIE.supertype_uri] for u in t.get(ANNAL.CURIE.supertype_uris,[]) ]
        if type_uri in supertype_uris:
            print("%s appears as a supertype of type '%s'"%(reporting_prefix, type_id))
    # References from views
    for v in coll_views(coll):
        view_id = v.get_id()
        if type_uri == v.get(ANNAL.CURIE.record_type, ""):
            print("%s appears as entity type for view '%s'"%(reporting_prefix, view_id))
    # References from lists
    for l in coll_lists(coll):
        list_id = l.get_id()
        if type_uri == l.get(ANNAL.CURIE.record_type, ""):
            print("%s appears as entity type for list '%s'"%(reporting_prefix, list_id))
        if type_uri in l.get(ANNAL.CURIE.list_entity_selector, ""):
            print("%s appears in selector for list '%s'"%(reporting_prefix, list_id))
    # References from fields
    for f in coll_fields(coll):
        field_id = f.get_id()
        if type_uri == f.get(ANNAL.CURIE.field_value_type, ""):
            print("%s appears as value type for field '%s'"%(reporting_prefix, field_id))
        if type_uri == f.get(ANNAL.CURIE.field_entity_type, ""):
            print("%s appears as entity type for field '%s'"%(reporting_prefix, field_id))
        if type_uri in f.get(ANNAL.CURIE.field_ref_restriction, ""):
            print("%s appears in value restriction for field '%s'"%(reporting_prefix, field_id))
    # References from groups
    for g in coll_groups(coll):
        group_id  = g.get_id()
        if type_uri == g.get(ANNAL.CURIE.record_type, ""):
            print("%s appears as entity type for group %s"%(reporting_prefix, group_id))
    return

# Migration helper functions

def am_migrationreport(annroot, userhome, options):
    """
    Collection migration report helper

        annalist_manager migrationreport old_coll new_coll

    Generates a report of changes to data needed to match type and property 
    URI changes moving from old_coll to new_coll.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    status, settings, site = get_settings_site(annroot, userhome, options)
    if status != am_errors.AM_SUCCESS:
        return status
    if len(options.args) > 2:
        print("Unexpected arguments for %s: (%s)"%(options.command, " ".join(options.args)), file=sys.stderr)
        return am_errors.AM_UNEXPECTEDARGS
    old_coll_id = getargvalue(getarg(options.args, 0), "Old collection Id: ")
    old_coll    = Collection.load(site, old_coll_id)
    if not (old_coll and old_coll.get_values()):
        print("Old collection not found: %s"%(old_coll_id), file=sys.stderr)
        return am_errors.AM_NOCOLLECTION
    new_coll_id = getargvalue(getarg(options.args, 1), "New collection Id: ")
    new_coll    = Collection.load(site, new_coll_id)
    if not (new_coll and new_coll.get_values()):
        print("New collection not found: %s"%(new_coll_id), file=sys.stderr)
        return am_errors.AM_NOCOLLECTION
    status      = am_errors.AM_SUCCESS
    print("# Migration report from collection '%s' to '%s' #"%(old_coll_id, new_coll_id))
    print("")
    # Scan and report on type URI changes
    for new_type in coll_types(new_coll):
        type_id  = new_type.get_id()
        old_type = old_coll.get_type(type_id)
        if old_type:
            old_uri  = old_type[ANNAL.CURIE.uri]
            new_uri  = new_type[ANNAL.CURIE.uri]
            if old_uri != new_uri:
                print("* Type %s, URI changed from '%s' to '%s'"%(type_id, old_uri, new_uri))
                supertype_uris = [ u[ANNAL.CURIE.supertype_uri] for u in new_type.get(ANNAL.CURIE.supertype_uris,[]) ]
                if old_uri not in supertype_uris:
                    print(
                        "    Consider adding supertype '%s' to type '%s' in collection '%s'"%
                        (old_uri, type_id, new_coll_id)
                        )
                report_type_references(new_coll, old_uri, "    URI '%s'"%(old_uri))
    # Scan and report on property URI changes in field definitions
    for new_field in coll_fields(new_coll):
        field_id  = new_field.get_id()
        old_field = coll_field(old_coll, field_id)
        if old_field:
            old_uri = old_field[ANNAL.CURIE.property_uri]
            new_uri = new_field[ANNAL.CURIE.property_uri]
            if old_uri != new_uri:
                print("* Field %s, property URI changed from '%s' to '%s'"%(field_id, old_uri, new_uri))
                type_ids = types_using_field(new_coll, field_id, old_uri)
                for tid in type_ids:
                    print(
                        "    Consider adding property alias for '%s' to type %s in collection '%s'"%
                        (old_uri, tid, new_coll_id)
                        )
    # Scan and report on property URI changes in group definitions
    for new_group in coll_groups(new_coll):
        group_id  = new_group.get_id()
        old_group = coll_group(old_coll, group_id)
        if old_group:
            compare_field_list(
                old_coll, new_coll, 
                old_group[ANNAL.CURIE.group_fields], 
                new_group[ANNAL.CURIE.group_fields],
                "Group %s"%group_id)
    # Scan and report on property URI changes in view definitions
    for new_view in coll_views(new_coll):
        view_id  = new_view.get_id()
        old_view = coll_view(old_coll, view_id)
        if old_view:
            compare_field_list(
                old_coll, new_coll, 
                old_view[ANNAL.CURIE.view_fields], 
                new_view[ANNAL.CURIE.view_fields],
                "View %s"%view_id)
    # Scan and report on property URI changes in list definitions
    for new_list in coll_lists(new_coll):
        list_id  = new_list.get_id()
        old_list = coll_list(old_coll, list_id)
        if old_list:
            compare_field_list(
                old_coll, new_coll, 
                old_list[ANNAL.CURIE.list_fields], 
                new_list[ANNAL.CURIE.list_fields],
                "List %s"%list_id)
    print("")
    return status

# Collection management functions

def am_installcollection(annroot, userhome, options):
    """
    Install software-defined collection data

        annalist_manager installcollection coll_id

    Copies data from an existing collection to a new collection.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    status, settings, site = get_settings_site(annroot, userhome, options)
    if status != am_errors.AM_SUCCESS:
        return status
    if len(options.args) > 1:
        print(
            "Unexpected arguments for %s: (%s)"%
              (options.command, " ".join(options.args)), 
            file=sys.stderr
            )
        return am_errors.AM_UNEXPECTEDARGS
    # Check collection Id
    coll_id = getargvalue(getarg(options.args, 0), "Collection Id to install: ")
    if coll_id in installable_collections:
        src_dir_name = installable_collections[coll_id]['data_dir']
    else:
        print("Collection name to install not known: %s"%(coll_id), file=sys.stderr)
        print("Available collection Ids are: %s"%(",".join(installable_collections.keys())))
        return am_errors.AM_NOCOLLECTION
    # Check if ciollection already exists
    coll    = Collection.load(site, coll_id)
    if (coll and coll.get_values()):
        if options.force:
            print("Existing collection %s will be removed ('--force' specified)"%(coll_id), file=sys.stderr)
            Collection.remove(site, coll_id)
        else:
            print("Collection already exists: %s"%(coll_id), file=sys.stderr)
            return am_errors.AM_COLLECTIONEXISTS
    # Install collection now
    src_dir = os.path.join(annroot, "annalist/data", src_dir_name)
    print("Installing collection '%s' from data directory '%s'"%(coll_id, src_dir))
    coll_metadata = installable_collections[coll_id]['coll_meta']
    date_time_now = datetime.datetime.now().replace(microsecond=0)
    coll_metadata[ANNAL.CURIE.comment] = (
        "Initialized at %s by `annalist-manager installcollection`"%
        date_time_now.isoformat()
        )
    coll = site.add_collection(coll_id, coll_metadata)
    msgs = initialize_coll_data(src_dir, coll)
    if msgs:
        for msg in msgs:
            print(msg)
        status = am_errors.AM_INSTALLCOLLFAIL
    return status

def am_copycollection(annroot, userhome, options):
    """
    Copy collection data

        annalist_manager copycollection old_coll_id new_coll_id

    Copies data from an existing collection to a new collection.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    status, settings, site = get_settings_site(annroot, userhome, options)
    if status != am_errors.AM_SUCCESS:
        return status
    if len(options.args) > 2:
        print(
            "Unexpected arguments for %s: (%s)"%
              (options.command, " ".join(options.args)), 
            file=sys.stderr
            )
        return am_errors.AM_UNEXPECTEDARGS
    old_coll_id = getargvalue(getarg(options.args, 0), "Old collection Id: ")
    old_coll    = Collection.load(site, old_coll_id)
    if not (old_coll and old_coll.get_values()):
        print("Old collection not found: %s"%(old_coll_id), file=sys.stderr)
        return am_errors.AM_NOCOLLECTION
    new_coll_id = getargvalue(getarg(options.args, 1), "New collection Id: ")
    new_coll    = Collection.load(site, new_coll_id)
    if (new_coll and new_coll.get_values()):
        print("New collection already exists: %s"%(new_coll_id), file=sys.stderr)
        return am_errors.AM_COLLECTIONEXISTS
    # Copy collection now
    print("Copying collection '%s' to '%s'"%(old_coll_id, new_coll_id))
    new_coll = site.add_collection(new_coll_id, old_coll.get_values())
    msgs     = copy_coll_data(old_coll, new_coll)
    if msgs:
        for msg in msgs:
            print(msg)
        status = am_errors.AM_COPYCOLLFAIL
    print("")
    return status

def am_migratecollection(annroot, userhome, options):
    """
    Apply migrations for a specified collection

        annalist_manager migratecollection coll

    Reads and writes every entity in a collection, thereby applying data 
    migrations and saving them in the stored data.

    annroot     is the root directory for the Annalist software installation.
    userhome    is the home directory for the host system user issuing the command.
    options     contains options parsed from the command line.

    returns     0 if all is well, or a non-zero status code.
                This value is intended to be used as an exit status code
                for the calling program.
    """
    status, settings, site = get_settings_site(annroot, userhome, options)
    if status != am_errors.AM_SUCCESS:
        return status
    coll_id = getargvalue(getarg(options.args, 0), "Collection Id: ")
    coll    = Collection.load(site, coll_id)
    if not (coll and coll.get_values()):
        print("Collection not found: %s"%(coll_id), file=sys.stderr)
        return am_errors.AM_NOCOLLECTION
    status = am_errors.AM_SUCCESS
    print("Apply data migrations in collection '%s'"%(coll_id,))
    msgs   = migrate_coll_data(coll)
    if msgs:
        for msg in msgs:
            print(msg)
        status = am_errors.AM_MIGRATECOLLFAIL
    return status

# End.
