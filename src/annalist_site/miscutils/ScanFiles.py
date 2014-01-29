# $Id: ScanFiles.py 1047 2009-01-15 14:48:58Z graham $
#
"""
Funtions to scan all files with names matching a given pattern in
a directory or directory tree.

Note that directories are not included in the results returned.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from os.path import join, isdir, normpath
import os

# Scan files matching pattern in a directory tree
#
# Exceptions are left to the calling program.
#
# srcdir    directory to search, maybe including subdirectories
# pattern   a compiled regex pattern, for filename selection
# FileFunc  a function to be called for each selected filename
#           as FileFunc( dir, name ).  (NOTE:  this can be an
#           object method with access to the instance data of
#           the object to which it belongs.)
# recursive is True if directories are to be scanned recursively,
#           otherwise only the named directory is scanned.
#
def ScanFilesEx(srcdir, pattern, FileFunc, recursive=True):
    """
    Scan all files in a directory or directory tree matching a given pattern.
    Exceptions are thrown back to the calling program.
    """
    names = os.listdir(srcdir)
    for name in names:
        srcname = join(srcdir, name)
        if isdir(srcname):
            if recursive:
                ScanFilesEx(srcname, pattern, FileFunc)
        elif pattern.match(name):
            FileFunc(srcdir, name)

# Scan files matching pattern in a directory tree
#
# This is just like 'ScanFilesEx' above, except that an error 
# is reported if an I/O exception occurs.
#
# srcdir    directory to search, maybe including subdirectories
# pattern   a compiled regex pattern, for filename selection
# FileFunc  a function to be called for each selected filename
#           as FileFunc( dir, name ).  (NOTE:  this can be an
#           object method with access to the instance data of
#           the object to which it belongs.)
# recursive is True if directories are to be scanned recursively,
#           otherwise only the named directory is scanned.
#
def ScanFiles(srcdir, pattern, FileFunc, recursive=True):
    try:
        ScanFilesEx(srcdir, pattern, FileFunc, recursive)
    except (IOError, os.error), why:
        print "Can't scan %s: %s" % (`srcdir`, str(why))

# Collect files matching pattern in a directory tree
#
# srcdir    directory to search, maybe including subdirectories
# pattern   a compiled regex pattern, for filename selection
# recursive is True if directories are to be scanned recursively,
#           otherwise only the named directory is scanned.
#
# Returns a list of pairs of the form (directory,filename)
#
def CollectFiles(srcdir, pattern, recursive=True):
    """
    Return a list of (dir,name) pairs for matching files in a directory tree.
    """
    global collection
    collection = []
    ScanFilesEx(srcdir, pattern, Collect, recursive)
    return collection

def Collect(fdir,fnam):
    global collection
    collection.append( (fdir,fnam) )

# Helper functions to read the contents of a file into a string
def joinDirName(fdir,fnam):
    """
    Return a normalized path name obtained by combining a named directory
    with a file name.  The first argument is presumed to name a directory, 
    even when its trailing directory indicator is omitted.
    """
    return normpath(join(fdir,fnam))

def readDirNameFile(fdir,fnam):
    """
    Read a file from a specified directory, and return its content as a string.
    """
    return readFile(joinDirName(fdir,fnam))

def readFile(nam):
    """
    Read a file and return its content as a string.
    """
    f = open(nam,"r")
    s = f.read()
    f.close()
    return s

# Test case

if __name__ == "__main__":
    import re
    pattern = re.compile( r'^.+\.py$' )
    c = CollectFiles(".", pattern)
    for (d,f) in c:
        print d+"\\"+f

# print "*******************************************"
# def ProcFile(path,name):
#     print "path: ", path, ", name: ", name
# pattern=re.compile(r'.*')
# ScanFilesEx(".",pattern,ProcFile)

# $Log: ScanFiles.py,v $
