#!/Users/dark/.virtualenvs/esp/bin/python
#
# ESP8266 Project setup utility
# https://github.com/esp8266-setup/esp8266-setup
#
# Copyright (C) 2017 Johannes Schriewer <hallo@dunkelstern.de>.
#
# This program is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by the Free
# Software Foundation
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301 USA.

from __future__ import print_function
from datetime import datetime
import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
import re

try:
  import pwd
except ImportError:
  import getpass
  pwd = None

def current_user():
  if pwd:
    return pwd.getpwuid(os.geteuid()).pw_name
  else:
    return getpass.getuser()

__version__ = "1.0"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

#
# Helpers
#

def make_project_makefile(mk, args):
    # Add the SDK libs as requested
    if args.sdk_libs is not None:
        libs = " ".join(args.sdk_libs.split(","))
        m = re.search(r'^LIBS[ \t]*\+=[ \t]*[^\n]*$', mk, flags=re.MULTILINE)
        mk = mk[:m.start()] + 'LIBS        += ' + libs + mk[m.end():]

    # Flash layout
    if args.flash_layout is not None:
        if args.flash_layout == '4m':
            ld_script = 'eagle.app.v6.new.512.app1.ld'
        elif args.flash_layout == '8m':
            ld_script = 'eagle.app.v6.new.1024.app1.ld'
        elif args.flash_layout == '16m' or args.flash_layout == '32m':
            ld_script = 'eagle.app.v6.new.2048.ld'
        else:
            ld_script = 'eagle.app.v6.new.512.app1.ld'
            print('ERROR: Unknown flash layout, defaulting to 4m')
        
        m = re.search(r'^LD_SCRIPT[ \t]*=[ \t]*[^\n]*$', mk, flags=re.MULTILINE)
        mk = mk[:m.start()] + 'LD_SCRIPT   = ' + ld_script + mk[m.end():]

    return mk

def make_library_makefile(mk, args):
    # project name
    m = re.search(r'^PROJECT[ \t]*:=[ \t]*[^\n]*$', mk, flags=re.MULTILINE)
    mk = mk[:m.start()] + 'PROJECT     := ' + args.name + mk[m.end():]

    # includes
    m = re.search(r'^INCDIR[ \t]*\+=[ \t]*([^\n]*)$', mk, flags=re.MULTILINE)
    print(m.group(1))
    includes = set(m.group(1).split(' '))

    if args.sdk_dependencies is not None:
        deps = args.sdk_dependencies.split(',')
        for dep in deps:
            if dep == 'lwip':
                includes.add('-I$(SDK_PATH)/include/lwip')
                includes.add('-I$(SDK_PATH)/include/lwip/ipv4')
                includes.add('-I$(SDK_PATH)/include/lwip/ipv6')
                includes.add('-I$(SDK_PATH)/include/lwip/posix')
            elif dep == 'espconn':
                includes.add('-I$(SDK_PATH)/include/espconn')
            elif dep == 'json':
                includes.add('-I$(SDK_PATH)/include/json')
            elif dep == 'mbedtls':
                includes.add('-I$(SDK_PATH)/include/mbedtls')
            elif dep == 'nopoll':
                includes.add('-I$(SDK_PATH)/include/nopoll')
            elif dep == 'openssl':
                includes.add('-I$(SDK_PATH)/include/openssl')
            elif dep == 'spiffs':
                includes.add('-I$(SDK_PATH)/include/spiffs')
            elif dep == 'ssl':
                includes.add('-I$(SDK_PATH)/include/ssl')
    mk = mk[:m.start()] + 'INCDIR      +=' + " ".join(includes) + mk[m.end():]

    return mk

def make_library_json(obj, args):
    if args.name is not None:
        obj['name'] = args.name
    if args.author is not None:
        obj['author'] = args.author
    if args.license is not None:
        obj['license'] = args.license
    if args.url is not None:
        obj['url'] = args.url
    if args.dependencies is not None:
        obj['dependencies'] = [d for d in args.dependencies.split(',') if len(d) > 0]
    if args.sdk_dependencies is not None:
        obj['sdk_dependencies'] = [d for d in args.sdk_dependencies.split(',') if len(d) > 0]
    return obj

#
# Callables
#

def version(args):
    print(__version__)

def start_project(args):
    if os.path.exists(args.name):
        print('ERROR: the path {} already exists, please use a different name or remove the file or directory!'.format(args.name))
        exit(1)
    os.mkdir(args.name)
    os.mkdir(os.path.join(args.name, 'lib'))
    os.mkdir(os.path.join(args.name, 'src'))
    with open(os.path.join(args.name, 'Makefile'), 'wb') as fpo:
        with open(os.path.join(BASE_DIR, "makefiles", "project.mk"), 'rb') as fpi:
            mk = make_project_makefile(fpi.read(), args)
        fpo.write(mk)
    with open(os.path.join(args.name, 'src', 'main.c'), 'wb') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "main.c"), 'rb') as fpi:
            fpo.write(fpi.read())
    with open(os.path.join(args.name, 'README.md'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "project.md"), 'r') as fpi:
            fpo.write(fpi.read().replace('%project%', args.name))
    with open(os.path.join(args.name, 'LICENSE.txt'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "BSD.txt"), 'r') as fpi:
            fpo.write(fpi.read().replace('%year%', str(datetime.now().year)).replace('%user%', current_user()))

def start_library(args):
    if os.path.exists(args.name):
        print('ERROR: the path {} already exists, please use a different name or remove the file or directory!'.format(args.name))
        exit(1)
    os.mkdir(args.name)
    os.mkdir(os.path.join(args.name, 'src'))
    os.mkdir(os.path.join(args.name, 'include'))
    open(os.path.join(args.name, 'src', 'main.c'), 'wb').close()
    with open(os.path.join(args.name, 'Makefile'), 'wb') as fpo:
        with open(os.path.join(BASE_DIR, "makefiles", "library.mk"), 'rb') as fpi:
            mk = make_library_makefile(fpi.read(), args)
        fpo.write(mk)
    with open(os.path.join(args.name, 'library.json'), 'wb') as fp:
        settings = make_library_json({}, args)
        json.dump(settings, fp, indent=4)
    with open(os.path.join(args.name, 'README.md'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "library.md"), 'r') as fpi:
            url = args.url if args.url is not None and len(args.url) > 0 else "<unknown URL>"
            fpo.write(fpi.read().replace('%project%', args.name).replace('%url%', url))
    with open(os.path.join(args.name, 'LICENSE.txt'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "BSD.txt"), 'r') as fpi:
            fpo.write(fpi.read().replace('%year%', str(datetime.now().year)).replace('%user%', current_user()))

def add_library(args):
    pass

def remove_library(args):
    pass

def update_library(args):
    pass

def modify_settings(args):
    if not os.path.exists('Makefile'):
        print('ERROR: Not a project directory, enter the project directory first!')
        exit(1)
    with open('Makefile', 'r+') as fp:
        mk = make_project_makefile(fp.read(), args)
        fp.seek(0)
        fp.truncate()
        fp.write(mk)

def modify_library(args):
    if not os.path.exists('library.json'):
        print('ERROR: Not a library directory, enter the library directory first!')
        exit(1)
    with open('Makefile', 'r+') as fp:
        mk = make_library_makefile(fp.read(), args)
        fp.seek(0)
        fp.truncate()
        fp.write(mk)
    with open('library.json', 'r+') as fp:
        settings = make_library_json(json.load(fp), args)
        fp.seek(0)
        fp.truncate()
        json.dump(settings, fp, indent=4)

def install_toolchain(args):
    pass

#
# End of operations functions
#


def main():
    parser = argparse.ArgumentParser(description='esp8266.py v%s - ESP8266 Project Setup Utility' % __version__, prog='esp8266')

    subparsers = parser.add_subparsers(
        dest='operation',
        help='Run esp8266 {command} -h for additional help')

    # create project templates
    parser_project = subparsers.add_parser(
        'start-project',
        help='Start a new project')
    parser_project.add_argument('name', help='Project name')
    parser_project.add_argument('--flash-layout', choices=['4m', '8m', '16m', '32m'], default='4m', help='Flash size')
    parser_project.add_argument('--sdk-libs', default='', help='Link with these libs from the SDK')

    # create library templates
    parser_start_library = subparsers.add_parser(
        'start-library',
        help='Start a new library')
    parser_start_library.add_argument('name', help='Library name')
    parser_start_library.add_argument('--author', default=current_user(), help='Library author')
    parser_start_library.add_argument('--license', default='BSD-2-Clause', help='Library license')
    parser_start_library.add_argument('--url', default='', help='URL where to get the library source, either git+<GIT URL> or http(s) URL')
    parser_start_library.add_argument('--dependencies', default='', help='Comma separated list of dependencies')
    parser_start_library.add_argument('--sdk-dependencies', default='', help='Comma separated list of sdk dependencies')


    # add library to project
    parser_add_library = subparsers.add_parser(
        'add-library',
        help='Add a library to a project')
    parser_add_library.add_argument('library', help='Library name or git URL in the form of git+<URL>')

    # remove a library from a project
    parser_remove_library = subparsers.add_parser(
        'remove-library',
        help='Remove a library from a project')
    parser_remove_library.add_argument('library', help='Library name')

    # update a library in a project
    parser_update_library = subparsers.add_parser(
        'update-library',
        help='Update a library in a project')
    parser_update_library.add_argument('library', help='Library name')


    # install toolchain
    parser_toolchain = subparsers.add_parser(
        'install-toolchain',
        help='Download and install toolchain')
    parser_toolchain.add_argument('destination', help='Destination directory for toolchain')

    # change settings for project
    parser_modify_settings = subparsers.add_parser(
        'modify-settings',
        help='Modify settings of an existing project')
    parser_modify_settings.add_argument('--flash-layout', choices=['4m', '8m', '16m', '32m'], default=None, help='Flash size')
    parser_modify_settings.add_argument('--sdk-libs', default=None, help='Link with these libs from the SDK')

    parser_modify_lib_settings = subparsers.add_parser(
        'modify-library',
        help='Modify settings of an existing library project')
    parser_modify_lib_settings.add_argument('--author', default=None, help='Library author')
    parser_modify_lib_settings.add_argument('--license', default=None, help='Library license')
    parser_modify_lib_settings.add_argument('--url', default=None, help='URL where to get the library source, either git+<GIT URL> or http(s) URL')
    parser_modify_lib_settings.add_argument('--dependencies', default=None, help='Comma separated list of dependencies')
    parser_modify_lib_settings.add_argument('--sdk-dependencies', default=None, help='Comma separated list of sdk dependencies')

    # display version
    subparsers.add_parser(
        'version', help='Print esp8266.py version')

    # internal sanity check - every operation matches a module function of the same name
    for operation in subparsers.choices.keys():
        op = operation.replace('-', '_')
        assert op in globals(), "%s should be a module function" % op

    args = parser.parse_args()

    print('esp8266.py v%s' % __version__)

    # operation function can take 1 arg (args)
    operation_func = globals()[args.operation.replace('-', '_')]
    operation_func(args)


if __name__ == '__main__':
    main()
