from __future__ import print_function
import argparse
import os

from esp8266_setup.tools import current_user, BASE_DIR
from esp8266_setup.library import start_library, modify_library
from esp8266_setup.project import start_project, modify_settings
from esp8266_setup.package import add_library, remove_library, update_library
from esp8266_setup.toolchain import install_toolchain

__version__ = "1.0"

#
# Callables
#

def version(args):
    print(__version__)

def parse():
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
    # parser_toolchain = subparsers.add_parser(
    #     'install-toolchain',
    #     help='Download and install toolchain')
    # parser_toolchain.add_argument('destination', help='Destination directory for toolchain')

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

    print('esp8266-setup v%s' % __version__)

    # operation function can take 1 arg (args)
    if args.operation:
        operation_func = globals()[args.operation.replace('-', '_')]
        operation_func(args)
    else:
        parser.print_usage()


if __name__ == '__main__':
    main()
