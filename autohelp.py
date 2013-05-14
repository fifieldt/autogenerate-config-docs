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

from git import *

# this is for the internationalisation function in gettext
import __builtin__
__builtin__.__dict__['_'] = lambda x: x

import common

def main(action, group_file, repo_location):
    package_name = common.git_check(repo_location)

    sys.path.append(repo_location)
    try:
        __import__(package_name)
    except ImportError as e:
        print str(e)
        print "Failed to import: %s (%s)" % (package_name, e)

    flags = common.extract_flags(repo_location, package_name)
    print "%s flags" % len(flags)

    if action == "names":
        common.write_flags(group_file, flags, name_only=True)

    if action == "docbook":
        groups = common.populate_groups(group_file)
        print "%s groups" % len(groups)
        common.write_docbook('.', flags, groups, package_name)
    sys.exit(0)

if  __name__ == "__main__":
    if (len(sys.argv) != 4 or
    (sys.argv[1] != 'docbook' and sys.argv[1] != 'names')):
        common.usage()
        sys.exit(1)

    main(sys.argv[1], sys.argv[2], sys.argv[3])
