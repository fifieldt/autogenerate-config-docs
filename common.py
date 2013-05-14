#
# A collection of shared functions for managing help flag mapping files.
#

import os
import sys
import pkgutil
import glob

from collections import defaultdict

from xml.sax.saxutils import escape

from git import Repo

# gettext internationalisation function requisite:
import __builtin__
__builtin__.__dict__['_'] = lambda x: x

from oslo.config import cfg

def git_check(repo_path):
    """
    Check a passed directory to verify it is a valid git repository.
    """
    try:
        repo = Repo(repo_path)
        assert repo.bare is False
        package_name = os.path.basename(repo.remotes.origin.url).rstrip('.git')
    except:
        print "\nThere is a problem verifying that the directory passed in"
        print "is a valid git repoistory.  Please try again.\n"
        sys.exit(1)
    return package_name

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
            if ('/tests' not in abs_path and '/locale' not in abs_path and
                '/cmd' not in abs_path  and '/db/migration' not in abs_path):
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
        groups_file = open(package_name + '-' + group[0] + '.xml', 'w')
        groups_file.write('<?xml version="1.0" encoding="UTF-8"?>\n\
        <para xmlns="http://docbook.org/ns/docbook" version="5.0">\n\
        <table rules="all">\n\
          <caption>Description of configuration options for ' + group[0] +
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
                    if not opt.help:
                        opt.help = "No help text available for this option"
                    groups_file.write('\n              <tr>\n\
                       <td>' + flag_name + '=' + str(opt.default) + '</td>\n\
                       <td>(' + type(opt).__name__ + ')' + escape(opt.help) + '</td>\n\
              </tr>')
        groups_file.write('\n       </tbody>\n\
        </table>\n\
        </para>')
        groups_file.close()

def create(flag_file, repo_path):
    """
        Create new flag mappings file, containing help information for
        the project whose repo location has been passed in at the command line.
    """

    # flag_file testing.
    #try:
        # Test for successful creation of flag_file.
    #except:
        # If the test(s) fail, exit noting the problem(s).

    # repo_path git repo validity testing.
    #try:
        # Test to be sure the repo_path passed in is a valid directory
        # and that directory is a valid existing git repo.
    #except:
        # If the test(s) fail, exit noting the problem(s).

    # get as much help as possible, searching recursively through the
    # entire repo source directory tree.
    #help_data = get_help(repo_path)

    # Write this information to the file.
    #write_file(flag_file, help_data)

def update():
    """
        Update flag mappings file, adding or removing entries as needed.
        This will update the file content, essentially overriding the data.
        The primary difference between create and update is that create will
        make a new file, and update will just work with the data that is
        data that is already there.
    """

    # flag_file testing.
    #try:
        # Test for successful creation of flag_file.
    #except:
        # If the test(s) fail, exit noting the problem(s).

    # repo_path git repo validity testing.
    #try:
        # Test to be sure the repo_path passed in is a valid directory
        # and that directory is a valid existing git repo.
    #except:
        # If the test(s) fail, exit noting the problem(s).

def verify(flag_file):
    """
        Verify flag file contents.  No actions are taken.
    """
    pass

def usage():
        print "\nUsage: %s docbook <groups file> <source loc>" % sys.argv[0]
        print "\nGenerate a list of all flags for package in source loc and"\
              "\nwrites them in a docbook table format, grouped by the groups"\
              "\nin the groups file, one file per group.\n"
        print "\n       %s names <names file> <source loc>" % sys.argv[0]
        print "\nGenerate a list of all flags names for the package in"\
              "\nsource loc and writes them to names file, one per line \n"
