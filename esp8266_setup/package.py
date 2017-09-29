from __future__ import print_function

import os
import json
import shutil
import re

from esp8266_setup.tools import BASE_DIR    

class Library(object):

    def __init__(self, name):
        self.library_info = None
        self.definition_location = None
        ok = self.parse_url(name)

        if not ok:
            if name.endswith('.json'):
                # if it ends in json, assume local file
                print('Importing local library definition for {}'.format(name))
                self.definition_location = os.path.dirname(name)
                self.load_definition(name)
            else:
                # try to find in repo that comes with the distribution
                lib_file = os.path.join(BASE_DIR, 'libs', name + '.json')
                if os.path.isfile(lib_file):
                    print('Using distributed library definition for {}'.format(name))
                    self.definition_location = os.path.dirname(lib_file)
                    self.load_definition(lib_file)
                else:
                    raise AttributeError('Unable to find library with name {}'.format(name))
    
    def update(self):
        print('Updating {}...'.format(self.name))
        if self.converted:
            shutil.rmtree(os.path.join('lib', self.name))
            self._update()
            self.convert_library()
        else:
            self._update()
        # TODO: reload library definition file
        
    def _update(self):
        if self.url.startswith('git+'):
            os.system('cd .libs/{}; git reset --hard ; git pull origin'.format(self.name))
        elif self.url.startswith('http://') or self.url.startswith('https://'):
            # TODO: ask server if a newer version is available
            pass
    
    def remove_data(self):
        print('Removing {}...'.format(self.name))
        dirs = [
            os.path.join('lib', self.name),
            os.path.join('.libs', self.name),
        ]
        for d in dirs:
            if os.path.isdir(d):
                shutil.rmtree(d)
    
    @property
    def source_type(self):
        if self.url.startswith('git+'):
            return 'git'
        elif self.url.startswith('http://') or self.url.startswith('https://'):
            return 'archive download'
        return 'local'

    @property
    def converted(self):
        return False if os.path.isfile(os.path.join('.libs', self.name, 'library.json')) else True

    @property
    def conversion_script(self):
        return os.path.abspath(os.path.join(self.definition_location, self.run_script))

    def git_checkout(self, url):
        try:
            url, branch = url.rsplit('@', 1)
        except ValueError:
            print('ERROR: Please supply a branch, tag or commit ID (append @master if unsure)!')
            exit(1)

        if getattr(self, 'name', None) is None:
            _, name = url.rsplit('/', 1)
            if name.endswith('.git'):
                name = name[:-4]
        else:
            name = self.name

        os.system('cd .libs; git clone {} {}'.format(url, name))
        os.system('cd .libs/{}; git checkout {}'.format(name, branch))

        definition_file = os.path.join('lib', name, 'library.json')
        if os.path.isfile(definition_file):
            self.load_definition(definition_file)
        elif self.library_info is None:
            print('ERROR: Not a native library, you will have to supply a library definition!')
            exit(1)

    def download(self, url):
        _, name = url.rsplit('/', 1)
        name, ext = os.path.splitext(name)

        # TODO: download
        # TODO: unpack

        definition_file = os.path.join('lib', name, 'library.json')
        if os.path.isfile(definition_file):
            self.load_definition(definition_file)
        elif self.library_info is None:
            print('ERROR: Not a native library, you will have to supply a library definition!')
            exit(1)

    def link_library(self):
        os.link(os.path.join('.libs', self.name), os.path.join('lib', self.name))

    def load_definition(self, filename):
        with open(filename, 'r') as fp:
            self.library_info = json.load(fp)

        # already downloaded?
        if not self.data_available():
            self.parse_url(self.library_info['url'])

        # ok we should have the data now, do we have to convert?
        if not os.path.isfile(os.path.join('.libs', self.name, 'library.json')):
            if not os.path.isfile(os.path.join('lib', self.name, 'library.json')):
                self.convert_library()
        else:
            # is it already linked?
            if not os.path.isfile(os.path.join('lib', self.name, 'library.json')):
                self.link_library()

    def parse_url(self, name):
        if name.startswith('git+'):
            # download with git
            # url looks like this: git+<web url>@<shasum or branch>
            print('Git repository for {}'.format(name))
            self.git_checkout(name[4:])
        elif name.startswith('http://') or name.startswith('https://'):
            # download an archive file and unpack
            print('Archive download for {}'.format(name))
            self.download(name)
        elif os.path.isfile(os.path.join('lib', name, 'library.json')):
            # already installed?
            self.load_definition(os.path.join('lib', name, 'library.json'))
        else:
            return False
        return True

    def convert_library(self):
        # run conversion script
        cmd = 'cd .libs/{}; chmod a+x {}; {}'.format(self.name, self.conversion_script, self.conversion_script)
        os.system(cmd)

        # create new library
        cmd = 'cd lib; esp8266-setup start-library --author "{author}" --license "{license}" --url "{url}"'.format(
            author=self.author,
            license=self.license,
            url=self.url
        )

        if len(self.dependencies) > 0:
            cmd += ' --dependencies "{}"'.format(",".join(self.dependencies))
        if len(self.sdk_dependencies) > 0:
            cmd += ' --sdk-dependencies "{}"'.format(",".join(self.sdk_dependencies))
        if self.extra_cflags:
            cmd += ' --cflags "{} "'.format(self.extra_cflags)
        if self.extra_ldflags:
            cmd += ' --ldflags "{} "'.format(self.extra_ldflags)
        if self.extra_includes:
            cmd += ' --include "{} "'.format(self.extra_includes)

        cmd += ' ' + self.name

        print(cmd)
        os.system(cmd)

        # remove the default crap
        crap = [
            os.path.join('lib', self.name, 'README.md'),
            os.path.join('lib', self.name, 'LICENSE.txt'),
            os.path.join('lib', self.name, 'src', self.name + '.c'),
            os.path.join('lib', self.name, 'include', self.name + '.h'),
        ]
        for c in crap:
            os.remove(c)
        
        # link readme and license documents from original
        candidates = [
            os.path.join('.libs', self.name, 'LICENSE-BSD.txt'),
            os.path.join('.libs', self.name, 'LICENSE-MIT.txt'),
            os.path.join('.libs', self.name, 'LICENSE-Apache.txt'),
            os.path.join('.libs', self.name, 'LICENSE-GPL.txt'),
            os.path.join('.libs', self.name, 'LICENSE.txt'),
            os.path.join('.libs', self.name, 'LICENSE'),
            os.path.join('.libs', self.name, 'COPYING'),
            os.path.join('.libs', self.name, 'README.txt'),
            os.path.join('.libs', self.name, 'README.md'),
            os.path.join('.libs', self.name, 'README.markdown'),
            os.path.join('.libs', self.name, 'README.rst'),
            os.path.join('.libs', self.name, 'README'),
        ]
        for c in candidates:
            if os.path.isfile(c):
                d = os.path.join('lib', self.name, os.path.basename(c))
                os.link(c, d)

        # link source
        for src in self.source:
            s = os.path.join('.libs', self.name, src)
            d = os.path.join('lib', self.name, 'src', os.path.basename(src))
            os.link(s, d)
        
        # link includes
        for inc in self.include:
            s = os.path.join('.libs', self.name, inc)
            if inc.startswith('include/') or inc.startswith('include\\'):
                inc = inc[8:]
            try:
                os.makedirs(os.path.join('lib', self.name, 'include', os.path.dirname(inc)))
            except OSError as e:
                if e.errno == 17:
                    pass
                else:
                    print('ERROR: Could not create directory')
                    exit(1)
            d = os.path.join('lib', self.name, 'include', inc)
            os.link(s, d)

    def data_available(self):
        return os.path.isdir(os.path.join('.libs', self.library_info['name']))

    def __getattr__(self, attribute):
        return self.library_info[attribute]


def load_installed_libs():
    libs = [d for d in os.listdir('lib') if os.path.isdir(os.path.join('lib', d))]

    result = []
    for lib in libs:
        try:
            l = Library(lib)
            result.append(l)
        except AttributeError as e:
            print('WARNING: Invalid library in {} !'.format(os.path.join('lib', lib)))
            print(e)

    return result

def rewrite_makefile(mk, libs):
    # update src libs
    libs = " ".join([l.name for l in libs])
    m = re.search(r'^SRC_LIBS[ \t]*=[ \t]*[^\n]*$', mk, flags=re.MULTILINE)
    mk = mk[:m.start()] + 'SRC_LIBS     = ' + libs + mk[m.end():]
    
    return mk

def add_library(args):
    if not os.path.isfile('Makefile'):
        print("Not a project directory, please enter project first!")
        exit(1)

    with open('Makefile', 'r+') as fp:
        mk = fp.read()
        libs = load_installed_libs()
        libs.append(Library(args.library))
        mk = rewrite_makefile(mk, libs)
        fp.seek(0)
        fp.truncate()
        fp.write(mk)

def remove_library(args):
    if not os.path.isfile('Makefile'):
        print("Not a project directory, please enter project first!")
        exit(1)

    with open('Makefile', 'r+') as fp:
        mk = fp.read()
        libs = load_installed_libs()
        
        lib_to_remove = None
        for l in libs:
            if l.name == args.library:
                lib_to_remove = l
                break
        if not lib_to_remove:
            print('ERROR: Can not find library with name {}'.format(args.library))
            exit(1)

        lib_to_remove.remove_data()
        libs = [l for l in libs if l != lib_to_remove]

        mk = rewrite_makefile(mk, libs)
        fp.seek(0)
        fp.truncate()
        fp.write(mk)

def update_library(args):
    if not os.path.isfile('Makefile'):
        print("Not a project directory, please enter project first!")
        exit(1)

    with open('Makefile', 'r+') as fp:
        mk = fp.read()
        libs = load_installed_libs()

        # update
        lib_to_update = Library(args.library)
        lib_to_update.update()
        libs = [l for l in libs if l.name != args.library]
        libs.append(lib_to_update)
        
        mk = rewrite_makefile(mk, libs)
        fp.seek(0)
        fp.truncate()
        fp.write(mk)

def show_libraries(args):
    if not os.path.isfile('Makefile'):
        print("Not a project directory, please enter project first!")
        exit(1)

    libs = load_installed_libs()
    if len(libs) == 0:
        print('No libraries installed!')
        exit(0)
    
    print('Installed libraries:')
    for lib in libs:
        typ = 'native'
        if lib.converted:
            typ = 'imported'
        print('{} -> v{} ({}, {})'.format(lib.name, lib.version, typ, lib.source_type))