#! /usr/bin/env python -Wall
# pylint: disable=multiple-imports, ungrouped-imports

"""
Run doctests from a given set of modules in django environment.
@author: Asad
@license: BSD
"""

from __future__ import unicode_literals
from __future__ import absolute_import, division, print_function

import os, sys, glob
from sys import stderr 
import doctest

os.environ['DJANGO_SETTINGS_MODULE'] = "annalist_site.settings.runtests"
from django.test.utils import setup_test_environment

if len(sys.argv) < 2:
    n = sys.argv[0]
    print("Usage: %s path_to_test_file(s) [verbose 0 or 1]" % n, file=stderr)
    print("Example: %s appName/lib/a.py 1" % n, file=stderr)
    print("Example: %s appName/lib/ <== will search directory" % n, file=stderr)
    print("Example: %s appName/lib <== will search directory" % n, file=stderr)
    sys.exit(1)

path = sys.argv[1]
verbose = False
if len(sys.argv) == 3 and int(sys.argv[2]) == 1:
    verbose = True

ls = []
if os.path.splitext(path)[1] == '.py' and os.path.isfile(path):
    ls = [path]
elif os.path.isdir(path): 
    path = os.path.join(path, '*.py')
    ls = glob.glob(path)
else:
    print("Don't know how to deal with", path, file=stderr)
    if not os.path.exists(path):
        print("Path does not exist", file=stderr)
    sys.exit(1)


ls = [fn for fn in ls if not os.path.basename(fn).startswith('__')]
print("Finding doctests in %r"%(ls,))
results = []
for fn in ls:
    setup_test_environment()
    f = os.path.splitext(fn)[0].replace(os.sep, '.')
    m = __import__(f, {}, {}, ['*'])
    result = doctest.testmod(m, verbose=verbose)
    if verbose: 
        print(f, result, file=stderr) 
    results.append((f, result))

totalTests = 0
totalFailures = 0
for (f, result) in results:
    totalFailures += result.failed
    totalTests += result.attempted

if totalFailures > 0:
    print("Summary:", \
          totalFailures, "failures out of", \
          totalTests, "attempts",
          file=stderr)
    sys.exit(1)
else:
    print("All", totalTests, "tests passed")

# End.
