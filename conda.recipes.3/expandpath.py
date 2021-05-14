#!/usr/bin/env python

import sys
from pkg_resources import Requirement, resource_filename

pkg = Requirement.parse('topas4rmc')
TOPAS4RMCPATH = resource_filename(pkg, '')
assert TOPAS4RMCPATH.lower().startswith(sys.prefix.lower())
TOPAS4RMCBASE = TOPAS4RMCPATH[len(sys.prefix):].replace('\\', '/').strip('/')

if __name__ == "__main__":
    content = open(sys.argv[1]).read()
    output = content.replace('@TOPAS4RMCBASE@', TOPAS4RMCBASE)
    sys.stdout.write(output)
