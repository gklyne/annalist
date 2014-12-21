#!/bin/bash
#
# Clean out all compiled python files
#

echo "Remove all compiled python (.pyc) filerd from directory tree"
echo "find . -type f -name '*.pyc' -delete"
find . -type f -name '*.pyc' -delete

# End.

