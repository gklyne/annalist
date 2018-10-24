# Read stdin looking for "rdfs:comment" field, add "annal:tooltip" field and update comment

import sys
import re

lines   = sys.stdin.readlines()
label   = None
comment = None
tooltip = None

for l in lines:
    m1 = re.match(r'\s*,\s*"rdfs:label":\s*"(.*)"\s*$', l)
    if m1:
        label = m1.group(1)
    m2 = re.match(r'\s*,\s*"rdfs:comment":\s*"(.*)"\s*$', l)
    if m2:
        comment = m2.group(1)
    m3 = re.match(r'\s*,\s*"annal:tooltip":\s*"(.*)"\s*$', l)
    if m3:
        tooltip = m3.group(1)

if tooltip is not None:
    sys.stdout.writelines(lines)
else:
    for l in lines:
        m2 = re.match(r'(\s*,\s*"rdfs:comment":\s*)"(.*)"\s*$', l)
        if m2:
            sys.stdout.write(''', "rdfs:comment":               "# %s\\r\\n\\r\\n%s"\n'''%(label, comment))
            sys.stdout.write(''', "annal:tooltip":              "%s"\n'''%(comment,))
        else:
            sys.stdout.write(l)

