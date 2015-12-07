#!/bin/bash
#
# This is a one-off script used to update definitions in sitedata
# with context attributes.  The file is left here as an example 
# of how to do this kind of processing with bash, find and sed.
#
# A useful and accessible reference for sed is at http://www.grymoire.com/Unix/Sed.html
#

DATE=`date "+%Y-%m-%dT%H:%M:%S"`

for F in `find . -name "enum_meta.jsonld"`; do

    echo Processing $F ...

    # Belt-and-braces: keep timed backup
    # Use 'git clean -nX' (dry run) and 'git clean -fX' to remove .bak files 
    # after updated files have been committed.

    cp $F $F.$DATE.bak

    # Use sed to apply changes

    sed -e '/"@base":/d' \
        -e '/"@context":/ {
              c\
              \, "@context":           ["../../coll_context.jsonld"]
            }' \
        $F >$F.new

    # sed '/"@base":/d' $F >$F.new

    # sed '/"@context":/ {
    #           c\
    #           \, "@context":           ["../../coll_context.jsonld"]
    #         }
    #     ' $F >$F.new

    # Only do this last command when the script has been debugged and tested:
    # this is the point at which the original data is overwritten.

    # mv $F.new $F

done
