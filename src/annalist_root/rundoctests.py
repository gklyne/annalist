#! /usr/bin/env python -Wall

# Coped from http://dodrum.blogspot.co.uk/2011/01/running-doctests-in-django-project.html

"""
Run doctests from a given set of modules in django environment.
@author: Asad
@license: BSD
"""

import os, sys, glob
from sys import stderr 
os.environ['DJANGO_SETTINGS_MODULE'] = "annalist_site.settings.runtests"
from django.test.utils import setup_test_environment
import doctest

if len(sys.argv) < 2:
    n = sys.argv[0]
    print >> stderr, "Usage: %s path_to_test_file(s) [verbose 0 or 1]" % n
    print >> stderr, "Example: %s appName/lib/a.py 1" % n
    print >> stderr, "Example: %s appName/lib/ <== will search directory" % n
    print >> stderr, "Example: %s appName/lib <== will search directory" % n
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
    print >> stderr, "Don't know how to deal with", path
    if not os.path.exists(path):
        print >> stderr, "Path does not exist"
    sys.exit(1)


ls = [fn for fn in ls if not os.path.basename(fn).startswith('__')]
print "Finding doctests in", ls
results = []
for fn in ls:
    setup_test_environment()
    f = os.path.splitext(fn)[0].replace(os.sep, '.')
    m = __import__(f, {}, {}, ['*'])
    result = doctest.testmod(m, verbose=verbose)
    if verbose: print >> stderr, f, result
    results.append((f, result))

totalTests = 0
totalFailures = 0
for (f, result) in results:
    totalFailures += result.failed
    totalTests += result.attempted

if totalFailures > 0:
    print >> stderr, "Summary:", \
             totalFailures, "failures out of", \
             totalTests, "attempts"
    sys.exit(1)
else:
    print "All", totalTests, "tests passed"

