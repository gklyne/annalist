# $Id: ScanDirectories.py 1047 2009-01-15 14:48:58Z graham $
#
"""
Function to scan the sub-directory structure in a given directory.
"""

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, Graham Klyne, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

from os.path import join, isdir, normpath
import os
import logging

logger = logging.getLogger("ScanDirectories")
#logger.setLevel(logging.INFO)

# Scan the sub-directory structure in a given directory
#
# Exceptions are left to the calling program.
#
# srcdir    directory to search, maybe including sub-directories
# DirFunc   a function to be called for each selected directory name
#           as DirFunc( dir ).  (NOTE:  this can be an
#           object method with access to the instance data of
#           the object to which it belongs.)
# FileFunc a function to be called for each selected file name
#           as FileFunc( file ).  (NOTE:  this can be an
#           object method with access to the instance data of
#           the object to which it belongs.)
# recursive is True if directories are to be scanned recursively,
#           otherwise only the named directory is scanned.
#
def ScanDirectoriesEx(srcdir, DirFunc, FileFunc=None, recursive=True):
    """
    Scan all sub-directories in a given source directory.
    Exceptions are thrown back to the calling program.
    """
    if not srcdir.endswith(os.path.sep): srcdir += os.path.sep
    directoryList = os.listdir(srcdir)
    for directoryComponent in directoryList:
        path = srcdir+directoryComponent
        if isdir(path):
            DirFunc(path)
            if recursive:
                logger.debug("Adding Directory %s " % (path))
                ScanDirectoriesEx(path, DirFunc, FileFunc, recursive)
        elif FileFunc:
            FileFunc(path)
    return

# Scan the sub-directory structure in a given directory
#
# This is just like 'ScanDirectoriesEx' above, except that an error 
# is reported if an I/O exception occurs.
#
# srcdir    directory to search, maybe including sub-directories
# DirFunc  a function to be called for each selected directory name
#           as DirFunc( dir ).  (NOTE:  this can be an
#           object method with access to the instance data of
#           the object to which it belongs.)
# recursive is True if directories are to be scanned recursively,
#           otherwise only the named directory is scanned.
#
def ScanDirectories(srcdir, DirFunc, listFiles=False, recursive=True):
    try:
        ScanDirectoriesEx(srcdir, DirFunc, listFiles, recursive)
    except (IOError, os.error), why:
        logger.debug("Can't scan %s: %s" % (`srcdir`, str(why)))
        print "Can't scan %s: %s" % (`srcdir`, str(why))
    return

# Collect directories/sub-directories found under the source directory
#
# srcdir    directory to search, maybe including sub-directories
# baseDir   a base directory that is removed from all results returned.
# listFiles is True if files are to be included in the listing returned
# recursive is True if directories are to be scanned recursively,
#           otherwise only the named directory is scanned.
# appendSep is True if path separator character is to be appended to directory names
#
# Returns a list of directory contents
#
def CollectDirectoryContents(srcDir, baseDir="", 
        listDirs=True, listFiles=False, recursive=True, appendSep=False):
    """
    Return a list of directory contents found under the source directory.
    """
    logger.debug("CollectDirectories: %s, %s, %s"%(srcDir,baseDir,str(os.path.sep)))
    dirsuffix = ""
    if appendSep: dirsuffix = os.path.sep
    collection = []
    if (baseDir != "") and (not baseDir.endswith(os.path.sep)):
        baseDir = baseDir+os.path.sep
    def CollectDir(path):
        logger.debug("- CollectDir base: %s, path: %s"%(baseDir, path))
        if listDirs: collection.append(path.replace(baseDir,"",1)+dirsuffix)
    def CollectFile(path):
        logger.debug("- CollectFile base: %s, path: %s"%(baseDir, path))
        if listFiles: collection.append(path.replace(baseDir,"",1))
    ScanDirectoriesEx(srcDir, CollectDir, CollectFile, recursive)
    return collection

if __name__ == "__main__":
    directoryCollection = CollectDirectoryContents(".", baseDir=".", 
        listFiles=True, listDirs=False, appendSep=True)
    print "\n".join(directoryCollection)

# End.
