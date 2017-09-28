import os
import re

from esp8266_setup.tools import BASE_DIR, current_user, replace_placeholders

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


def start_project(args):
    if os.path.exists(args.name):
        print('ERROR: the path {} already exists, please use a different name or remove the file or directory!'.format(args.name))
        exit(1)
    os.mkdir(args.name)
    os.mkdir(os.path.join(args.name, 'lib'))
    os.mkdir(os.path.join(args.name, 'src'))
    with open(os.path.join(args.name, 'Makefile'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "makefiles", "project.mk"), 'r') as fpi:
            mk = make_project_makefile(fpi.read(), args)
        fpo.write(mk)
    with open(os.path.join(args.name, 'src', 'main.c'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "main.c"), 'r') as fpi:
            fpo.write(replace_placeholders(fpi.read()))
    with open(os.path.join(args.name, 'README.md'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "project.md"), 'r') as fpi:
            fpo.write(fpi.read().replace('%project%', args.name))
    with open(os.path.join(args.name, 'LICENSE.txt'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "BSD.txt"), 'r') as fpi:
            fpo.write(replace_placeholders(fpi.read()))

def modify_settings(args):
    if not os.path.exists('Makefile'):
        print('ERROR: Not a project directory, enter the project directory first!')
        exit(1)
    with open('Makefile', 'r+') as fp:
        mk = make_project_makefile(fp.read(), args)
        fp.seek(0)
        fp.truncate()
        fp.write(mk)