from __future__ import print_function

import os
import re
import json

from esp8266_setup.tools import BASE_DIR, current_user, replace_placeholders


def make_library_makefile(mk, args):
    # project name
    m = re.search(r'^PROJECT[ \t]*:=[ \t]*[^\n]*$', mk, flags=re.MULTILINE)
    mk = mk[:m.start()] + 'PROJECT     := ' + args.name + mk[m.end():]

    # includes
    m = re.search(r'^INCDIR[ \t]*\+=[ \t]*([^\n]*)$', mk, flags=re.MULTILINE)
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
    if args.include is not None:
        inc = args.include.split(' ')
        for i in inc:
            includes.add(i)
    mk = mk[:m.start()] + 'INCDIR      +=' + " ".join(includes) + mk[m.end():]

    if args.cflags is not None:
        m = re.search(r'^CFLAGS[ \t]*\+=[ \t]*[^\n]*$', mk, flags=re.MULTILINE)
        mk = mk[:m.start()] + 'CFLAGS      += ' + args.cflags + mk[m.end():]

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
    if args.cflags is not None:
        obj['extra_cflags'] = args.cflags
    if args.ldflags is not None:
        obj['extra_ldflags'] = args.ldflags
    if args.include is not None:
        obj['extra_includes'] = args.include
    return obj


def start_library(args):
    if os.path.exists(args.name):
        print('ERROR: the path {} already exists, please use a different name or remove the file or directory!'.format(args.name))
        exit(1)
    os.mkdir(args.name)
    os.mkdir(os.path.join(args.name, 'src'))
    os.mkdir(os.path.join(args.name, 'include'))
    with open(os.path.join(args.name, 'Makefile'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "makefiles", "library.mk"), 'r') as fpi:
            mk = make_library_makefile(fpi.read(), args)
        fpo.write(mk)
    with open(os.path.join(args.name, 'library.json'), 'w') as fp:
        settings = make_library_json({}, args)
        json.dump(settings, fp, indent=4)
    with open(os.path.join(args.name, 'README.md'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "library.md"), 'r') as fpi:
            url = args.url if args.url is not None and len(args.url) > 0 else "<unknown URL>"
            fpo.write(replace_placeholders(fpi.read(), project=args.name, url=url))
    with open(os.path.join(args.name, 'LICENSE.txt'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "BSD.txt"), 'r') as fpi:
            fpo.write(replace_placeholders(fpi.read()))
    with open(os.path.join(args.name, 'src', args.name + '.c'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "library.c"), 'r') as fpi:
            fpo.write(replace_placeholders(fpi.read(), project=args.name))
    with open(os.path.join(args.name, 'include', args.name + '.h'), 'w') as fpo:
        with open(os.path.join(BASE_DIR, "skel", "library.h"), 'r') as fpi:
            fpo.write(replace_placeholders(fpi.read(), project=args.name))

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
