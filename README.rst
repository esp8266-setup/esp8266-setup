=============
ESP8266 Setup
=============

This is a build system for easier project and library setup for the ESP8266 platform.
I have written this because the learning curve of getting a new project set up correctly
seemed too high. If you're fine using the Arduino port of the ESP8266 SDK feel free to
do so.

This build system is primarily intended to be used with the RTOS flavor of the ESP SDK.


Installation
============

Just get it via ``pip``:

    pip install esp8266-setup

You probably want to setup a virtual environment before:

    Python 2:
    
    virtualenv $HOME/.virtualenvs/esp
    . $HOME/.virtualenvs/esp/bin/activate

    
    Python 3:
    python -m venv $HOME/.virtualenvs/esp
    . $HOME/.virtualenvs/esp/bin/activate

Usage
=====

Creating projects
-----------------

To create a project just run the ``start-project`` command like so:

    esp8266-setup start-project <project_name>

This will create a new sub-folder for the project and set up the needed
``Makefile`` and some other files.

Be aware that it copies the BSD-2-Clause license file to the ``LICENSE.txt``.
In the header of that file there is a copyright. The copyright holder will be
set to your current user-name of your OS, you may probably want to change that.

You may define the flash-layout you want to use, just consult the ``--help`` option for
more options. (The default options are usually fine, but if you have more than half a
kilobyte flash on your board you may consider telling this to the project manager)

If you forgot to set an option or your platform changed you can use the
``modify-settings`` command.

The license of all generated files is set to BSD-2-Clause, while the license of
``esp8266-setup`` is the GPL version 2 license.


Library management
------------------

The real fun stuff starts here. ``esp8266-setup`` contains a small package manager which
is able to import source code libraries into your project. And the best thing is that
the author of the library you want to use does not even have to know about this project.
This is done via library definition files. Those are simple json files that describe
which files to include into your project.

The ``esp8266-setup`` distribution includes some library definitions for commonly useful
libraries for you to install.

The other alternative is ``esp8266-setup``-native libraries. Those may just be installed
by providing a git URL. The cool thing with those: They could easily be imported into
non-``esp8266-setup`` type projects by just grabbing the build artifacts and include
files. (This is the reverse of the library definition way above)

To manage a library just change into your project directory and issue one of the
following commands:

    esp8266-setup add-library git+https://github.com/esp8266-setup/simplehttp.git
    esp8266-setup add-library json
    esp8266-setup add-library library-defs/my_cool_library.json

    esp8266-setup update-library my_cool_library
    esp8266-setup remove-library json
    

The build tool takes all the responsibilities that come up with libraries, like:

- Adding include directories
- Making calls to the correct Makefiles
- Adding SDK dependencies
- Warning you about a not-installed dependency
- Probably adding linker and compiler flags
- Adding a ``last-updated`` file to the library directory to be able to 
  actually update libraries

So be careful if you change the ``Makefile`` of your project manually.


Creating libraries
------------------

There are two ways to create a library that can be imported into a ``esp8266-setup``
project:

- Native ``esp8266-setup`` libraries
- JSON library definitions for other sources

Native libraries
++++++++++++++++

To create a native library use the ``start-library`` command. It has some options:

- ``--author`` the library author, probably you, use a string in the following
  format ``Your Name <email-address>``
- ``--license`` use a ``SPDX short identifier`` (default is ``BSD-2-Clause``)
- ``--url`` an URL to check for updates, currently we support ``http(s)``
  and ``git+`` URLs. Preferably use a git URL as the check for http-downloads
  relies on the server to send a 304 reponse reliably
- ``--dependencies`` library names or URLs this library depends on, will be issued
  as a warning to the user if they miss a library. Is not used for any kind of
  automatic resolving.
- ``--sdk-dependencies`` add a dependency that is included in the SDK (like ``lwip``
  or the ``espconn`` libraries, makes sure the include path is set up correctly)

You may later on change those settings with ``modify-library`` or by editing the
generated ``library.json`` or ``Makefile``.

JSON Library definitions
++++++++++++++++++++++++

To adapt a foreign library to this build system you may write a JSON library definition.
Some are included in the distribution.

It looks like this:

    {
        "name": "<Library name>",
        "author": "Your name <your@email>",
        "license": "SPDX short identifier",
        "url": "<http or git URL>",
        "dependencies": [
            "<name or url of library>"
        ],
        "sdk_dependencies": [
            "<name of sdk included library>"
        ],
        "extra_cflags": "<needed c compiler flags>",
        "extra_ldflags": "<needed linker flags>",
        "extra_includes": "<needed include flags>",
        "source": [
            "<path/to/file.x>"
        ],
        "include": [
            "<path/to/include.h>"
        ],
        "run_script": "<relative path to python script to run after downloading>"
    }

When a library is installed from such a manifest file it will be downloaded (and
unpacked if neccessary) into a sub-folder in ``.libs``. After that is done the
python file defined in ``run_script`` is executed in the directory to fix anything
that probably has to be fixed to make this compile. And the next step is actually
creating a ``Makefile`` and copying the library into the default ``esp8266-setup``
structure. (This way it actually converts the libraries into a native library
before compiling)