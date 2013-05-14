#!/usr/bin/env python
#
# A collection of tools for working with flags from OpenStack
# packages and documentation.
#
# Example running:
#  python manipulate_flags.py glance.flagmappings ~/temp/glance
#
# TODO - make some methods for updating the groups files if options are
#  added or removed, and alerting the user - as these are currently
#  manually categorized
#

import os
import sys
import pkgutil
import glob

from git import *
from collections import defaultdict


from xml.sax.saxutils import escape

# this is for the internationalisation function in gettext
import __builtin__
__builtin__.__dict__['_'] = lambda x: x

from oslo.config import cfg
import common

def main(group_file, repo_location):
    repo = Repo(repo_location)
    assert repo.bare is False
    package_name = os.path.basename(repo.remotes.origin.url).rstrip('.git')

    sys.path.append(repo_location)
    try:
        __import__(package_name)
    except ImportError as e:
        print str(e)
        print "Failed to import: %s (%s)" % (package_name, e)

    groups = populate_groups(group_file)
    print "%s groups" % len(groups)
    flags = extract_flags(repo_location, package_name)
    print "%s flags" % len(flags)
    write_docbook('.', flags, groups, package_name)
    sys.exit(0)

if  __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
