import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='esp8266_setup',
    version='1.0.0',
    author='Johannes Schriewer',
    author_email='hallo@dunkelstern.de',
    packages=find_packages(),
    scripts=['bin/esp8266-setup'],
    url='https://github.com/esp8266-setup/esp8266-setup',
    license='LICENSE.txt',
    description='ESP8266 Build system.',
    long_description=README,
    include_package_data=True,
    install_requires=[
    ],
    classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Console',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: GPLv2 License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
    ],
)