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

# this is for the internationalisation function in gettext
import __builtin__
__builtin__.__dict__['_'] = lambda x: x

from oslo.config import cfg

def populate_groups(filepath):
    """
    Takes a file formatted with lines of config option and group
    separated by a space and constructs a dictionary indexed by
    group, which is returned..
    """
    groups = defaultdict(list)
    groups_file = open(os.path.expanduser(filepath), 'r')
    for line in groups_file:
        option, group = line.split(None, 1)
        groups[group.strip()].append(option)
    return groups


def extract_flags(repo_location, module_name, names_only=True):
    """
    Loops through the repository, importing module by module to
    populate the configuration object (cfg.CONF) created from Oslo.
    """
    usable_dirs = []
    module_location = os.path.dirname(repo_location + '/' + module_name)
    for root, dirs, files in os.walk(module_location + '/' + module_name):
        for name in dirs:
            abs_path = os.path.join(root.split(module_location)[1][1:], name)
            if '/tests' not in abs_path and '/locale' not in abs_path and '/cmd' not in abs_path:
                usable_dirs.append(os.path.join(root.split(module_location)[1][1:], name))

    for directory in usable_dirs:
        for python_file in glob.glob(module_location + '/' + directory + "/*.py"):
            if '__init__' not in python_file:
                usable_dirs.append(os.path.splitext(python_file)[0][len(module_location) + 1:])

        package_name = directory.replace('/', '.')
        try:
            __import__(package_name)
            print "imported %s" % package_name
        except ImportError as e:
            """
            work around modules that don't like being imported in this way
            FIXME This could probably be better, but does not affect the
            configuration options found at this stage
            """
            print str(e)
            print "Failed to import: %s (%s)" % (package_name, e)
            continue

    flags = cfg.CONF._opts.items()

    #extract group information
    for group in cfg.CONF._groups.keys():
        flags = flags + cfg.CONF._groups[group]._opts.items()
    flags.sort()

    return flags


def write_flags(filepath, flags, name_only=True):
    """
    write out the list of flags in the cfg.CONF object to filepath
    if name_only is True - write only a list of names, one per line,
    otherwise use MediaWiki syntax to write out the full table with
    help text and default values.
    """
    with open(os.path.expanduser(filepath), 'wb') as f:
        if not name_only:
            f.write("{|\n")  # start table
            # print headers
            f.write("!")
            f.write("!!".join(["name", "default", "description"]))
            f.write("\n|-\n")

        for name, value in flags:
            opt = value['opt']
            if not opt.help:
                opt.help = "No help text available for this option"
            if not name_only:
                f.write("|")
                f.write("||".join([name,
                                    str(opt.default),
                                   opt.help.replace("\n", " ")]))
                f.write("\n|-\n")
            else:
                f.write(name + "\n")

        if not name_only:
            f.write("|}\n")  # end table


def write_docbook(directory, flags, groups, package_name):
    """
    Prints a docbook-formatted table for every group of options.
    """
    count = 0
    for group in groups.items():
        groups_file = open(package_name + '-' + group[0] + '.xml' , 'w')
        groups_file.write('<?xml version="1.0" encoding="UTF-8"?>\n\
        <para xmlns="http://docbook.org/ns/docbook" version="5.0">\n\
        <table rules="all">\n\
          <caption>Description of configuration options for ' + group[0] +\
          '</caption>\n\
           <col width="50%"/>\n\
           <col width="50%"/>\n\
           <thead>\n\
              <tr>\n\
                  <td>Configuration option=Default value</td>\n\
                  <td>(Type) Description</td>\n\
              </tr>\n\
          </thead>\n\
          <tbody>')
        for flag_name in group[1]:
            for flag in flags:
                if flag[0] == flag_name:
                    count = count + 1
                    opt = flag[1]["opt"]
                    groups_file.write('\n              <tr>\n\
                       <td>' + flag_name + '=' + str(opt.default) + '</td>\n\
                       <td>(' + type(opt).__name__ + ')' + opt.help + '</td>\n\
              </tr>')
        groups_file.write('\n       </tbody>\n\
        </table>\n\
        </para>')
        groups_file.close()


def main(group_file, repo_location):
    repo = Repo(repo_location)
    assert repo.bare == False
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
        print "\nUsage: %s <groups file> <source loc>" % sys.argv[0]
        print "\nGenerate a list of all flags for package and prints them in a\n" \
              "docbook table format, grouped by the groups in the groups file.\n"
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
